from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, delete
import logging

from models.audit import AccessAuditLog
from models.user import User
from core.exceptions import AuditServiceError

logger = logging.getLogger(__name__)


class AuditService:
        
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_access_attempt(
        self,
        user_id: Optional[UUID],
        route: str,
        required_permission: str,
        granted: bool,
        method: str = "GET",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        denial_reason: Optional[str] = None,
        request_headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log access attempt for security monitoring.
        
        Args:
            user_id: User attempting access (None for anonymous)
            route: Route being accessed
            required_permission: Permission level required
            granted: Whether access was granted
            method: HTTP method
            ip_address: Client IP address
            user_agent: Client user agent
            denial_reason: Reason for denial (if access denied)
            request_headers: Request headers for forensics
        """
        try:
            # Get user role if user exists
            user_role = None
            if user_id:
                user_query = select(User.role).where(User.id == user_id)
                result = await self.db.execute(user_query)
                user_role = result.scalar_one_or_none()
            
            # Create audit log entry
            audit_entry = AccessAuditLog(
                user_id=user_id,
                attempted_route=route,
                route_method=method,
                user_role=user_role,
                required_permission=required_permission,
                access_granted=granted,
                ip_address=ip_address,
                user_agent=user_agent,
                request_headers=request_headers,
                denial_reason=denial_reason,
                created_at=datetime.utcnow()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
            # Log security events for real-time monitoring
            if not granted:
                logger.warning(
                    "Access denied",
                    extra={
                        "user_id": str(user_id) if user_id else "anonymous",
                        "route": route,
                        "method": method,
                        "permission": required_permission,
                        "user_role": user_role,
                        "ip_address": ip_address,
                        "reason": denial_reason,
                        "event_type": "access_denied"
                    }
                )
            else:
                # Only log successful access to sensitive routes
                if self._is_sensitive_route(route):
                    logger.info(
                        "Sensitive route accessed",
                        extra={
                            "user_id": str(user_id) if user_id else "anonymous",
                            "route": route,
                            "method": method,
                            "permission": required_permission,
                            "user_role": user_role,
                            "ip_address": ip_address,
                            "event_type": "sensitive_access"
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Failed to log access attempt: {str(e)}")
            # Don't raise exception to avoid breaking the main request flow
    
    async def log_role_change(
        self,
        user_id: UUID,
        admin_id: UUID,
        old_role: str,
        new_role: str,
        reason: Optional[str] = None
    ) -> None:
        """
        Log user role change for audit trail.
        
        Args:
            user_id: User whose role is being changed
            admin_id: Admin performing the change
            old_role: Previous role
            new_role: New role
            reason: Reason for role change
        """
        try:
            audit_entry = AccessAuditLog(
                user_id=user_id,
                admin_user_id=admin_id,
                attempted_route="role_change",
                route_method="UPDATE",
                required_permission="admin",
                access_granted=True,
                denial_reason=None,
                old_values={"role": old_role},
                new_values={"role": new_role},
                reason=reason,
                created_at=datetime.utcnow()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
            logger.info(
                "User role changed",
                extra={
                    "user_id": str(user_id),
                    "admin_id": str(admin_id),
                    "old_role": old_role,
                    "new_role": new_role,
                    "reason": reason,
                    "event_type": "role_change"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log role change: {str(e)}")
    
    async def log_user_deletion(
        self,
        user_id: UUID,
        admin_id: UUID,
        reason: str
    ) -> None:
        """
        Log user deletion for audit trail.
        
        Args:
            user_id: User being deleted
            admin_id: Admin performing deletion
            reason: Reason for deletion
        """
        try:
            audit_entry = AccessAuditLog(
                user_id=user_id,
                admin_user_id=admin_id,
                attempted_route="user_deletion",
                route_method="DELETE",
                required_permission="admin",
                access_granted=True,
                denial_reason=None,
                old_values={"status": "active"},
                new_values={"status": "deleted"},
                reason=reason,
                created_at=datetime.utcnow()
            )
            
            self.db.add(audit_entry)
            await self.db.commit()
            
            logger.warning(
                "User account deleted",
                extra={
                    "user_id": str(user_id),
                    "admin_id": str(admin_id),
                    "reason": reason,
                    "event_type": "user_deletion"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log user deletion: {str(e)}")
    
    async def get_security_events(
        self,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        granted_only: Optional[bool] = None
    ) -> list[AccessAuditLog]:
        """
        Get recent security events for monitoring.
        
        Args:
            limit: Maximum number of events to return
            user_id: Filter by specific user
            granted_only: Filter by access granted status
            
        Returns:
            List of audit log entries
        """
        try:
            query = select(AccessAuditLog).order_by(desc(AccessAuditLog.created_at))
            
            if user_id:
                query = query.where(AccessAuditLog.user_id == user_id)
            
            if granted_only is not None:
                query = query.where(AccessAuditLog.access_granted == granted_only)
            
            query = query.limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get security events: {str(e)}")
            raise AuditServiceError(f"Failed to retrieve security events: {str(e)}")
    
    async def get_failed_access_attempts(
        self,
        hours: int = 24,
        ip_address: Optional[str] = None
    ) -> list[AccessAuditLog]:
        """
        Get failed access attempts for security monitoring.
        
        Args:
            hours: Number of hours to look back
            ip_address: Filter by specific IP address
            
        Returns:
            List of failed access attempts
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(AccessAuditLog).where(
                and_(
                    AccessAuditLog.access_granted == False,
                    AccessAuditLog.created_at >= cutoff_time
                )
            )
            
            if ip_address:
                query = query.where(AccessAuditLog.ip_address == ip_address)
            
            query = query.order_by(desc(AccessAuditLog.created_at))
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get failed access attempts: {str(e)}")
            raise AuditServiceError(f"Failed to retrieve failed access attempts: {str(e)}")
    
    async def get_user_access_history(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> list[AccessAuditLog]:
        """
        Get access history for a specific user.
        
        Args:
            user_id: User ID to get history for
            limit: Maximum number of entries
            
        Returns:
            List of user's access history
        """
        try:
            query = select(AccessAuditLog).where(
                AccessAuditLog.user_id == user_id
            ).order_by(desc(AccessAuditLog.created_at)).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get user access history: {str(e)}")
            raise AuditServiceError(f"Failed to retrieve user access history: {str(e)}")
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Get audit statistics for security dashboard.
        
        Returns:
            Dictionary containing audit statistics
        """
        try:
            # Total access attempts in last 24 hours
            cutoff_24h = datetime.utcnow() - timedelta(hours=24)
            
            total_attempts = await self.db.scalar(
                select(func.count(AccessAuditLog.id)).where(
                    AccessAuditLog.created_at >= cutoff_24h
                )
            )
            
            # Failed attempts in last 24 hours
            failed_attempts = await self.db.scalar(
                select(func.count(AccessAuditLog.id)).where(
                    and_(
                        AccessAuditLog.created_at >= cutoff_24h,
                        AccessAuditLog.access_granted == False
                    )
                )
            )
            
            # Unique users with access attempts
            unique_users = await self.db.scalar(
                select(func.count(AccessAuditLog.user_id.distinct())).where(
                    and_(
                        AccessAuditLog.created_at >= cutoff_24h,
                        AccessAuditLog.user_id.isnot(None)
                    )
                )
            )
            
            # Top failed routes
            failed_routes_query = select(
                AccessAuditLog.attempted_route,
                func.count(AccessAuditLog.id).label('count')
            ).where(
                and_(
                    AccessAuditLog.created_at >= cutoff_24h,
                    AccessAuditLog.access_granted == False
                )
            ).group_by(AccessAuditLog.attempted_route)\
            .order_by(desc('count')).limit(5)
            
            result = await self.db.execute(failed_routes_query)
            top_failed_routes = result.all()
            
            return {
                "total_attempts_24h": total_attempts or 0,
                "failed_attempts_24h": failed_attempts or 0,
                "success_rate_24h": (
                    ((total_attempts - failed_attempts) / total_attempts * 100) 
                    if total_attempts > 0 else 100
                ),
                "unique_users_24h": unique_users or 0,
                "top_failed_routes": [
                    {"route": route, "count": count} 
                    for route, count in top_failed_routes
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {str(e)}")
            raise AuditServiceError(f"Failed to retrieve audit statistics: {str(e)}")
    
    def _is_sensitive_route(self, route: str) -> bool:
        """
        Check if route is considered sensitive for logging.
        
        Args:
            route: Route path
            
        Returns:
            bool: True if route is sensitive
        """
        sensitive_prefixes = [
            "/admin",
            "/api/v1/admin",
            "/editor/users",
            "/api/v1/users",
            "/api/v1/auth/admin"
        ]
        
        return any(route.startswith(prefix) for prefix in sensitive_prefixes)
    
    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """
        Clean up old audit logs to manage database size.
        
        Args:
            days_to_keep: Number of days to retain logs
            
        Returns:
            Number of deleted records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Count records to be deleted
            count_query = select(func.count(AccessAuditLog.id)).where(
                AccessAuditLog.created_at < cutoff_date
            )
            count_to_delete = await self.db.scalar(count_query)
            
            # Delete old records
            delete_query = delete(AccessAuditLog).where(
                AccessAuditLog.created_at < cutoff_date
            )
            await self.db.execute(delete_query)
            await self.db.commit()
            
            logger.info(f"Cleaned up {count_to_delete} old audit log entries")
            
            return count_to_delete or 0
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            raise AuditServiceError(f"Failed to cleanup old logs: {str(e)}") 