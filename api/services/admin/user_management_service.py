"""
User Management Service

Provides comprehensive user administration capabilities including user listing,
filtering, role management, user statistics, and administrative operations.
Follows SubPRD-UserManagementService.md specifications.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, update, delete
from sqlalchemy.orm import selectinload, joinedload

from models.user import User
from models.post import Post
from models.comment import Comment
from models.interactions import Like, View
from models.audit import AccessAuditLog
from schemas.admin.user_management import (
    UserFilters, PaginatedUsersResponse, UserSummaryResponse,
    UserStatsResponse, UserContributorResponse, UserGrowthMetricsResponse,
    BulkUserUpdate, BulkOperationResponse, UserAuditLogResponse,
    DailySignupResponse, UserRoleUpdateRequest
)
from schemas.user import UserResponse
from dependencies.pagination import PaginationParams, PaginationResponse
from core.exceptions import UserManagementError, UserNotFoundError, PermissionError
from core.security import hash_password


class UserManagementService:
    """Service for user administration and management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_users(
        self, 
        filters: UserFilters, 
        pagination: PaginationParams
    ) -> PaginatedUsersResponse:
        """
        Get paginated user listing with advanced filtering and search.
        
        Args:
            filters: User filtering criteria
            pagination: Pagination parameters
            
        Returns:
            PaginatedUsersResponse: Paginated user data with filters
        """
        try:
            # Build base query with user statistics
            query = select(
                User.id,
                User.name,
                User.email,
                User.role,
                User.created_at,
                User.updated_at,
                User.email_verified_at,
                func.count(Post.id.distinct()).label('posts_count'),
                func.count(Comment.id.distinct()).label('comments_count'),
                func.count(Like.id.distinct()).label('likes_count'),
                func.coalesce(
                    func.max(func.greatest(
                        User.updated_at,
                        func.max(Post.created_at),
                        func.max(Comment.created_at)
                    )), 
                    User.updated_at
                ).label('last_activity')
            ).select_from(User)\
            .outerjoin(Post, User.id == Post.user_id)\
            .outerjoin(Comment, User.id == Comment.user_id)\
            .outerjoin(Like, User.id == Like.user_id)\
            .group_by(
                User.id, User.name, User.email, User.role, 
                User.created_at, User.updated_at, User.email_verified_at
            )
            
            # Apply search filter
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            # Apply role filter
            if filters.role:
                query = query.where(User.role == filters.role)
            
            # Apply activity status filter
            if filters.activity_status:
                now = datetime.utcnow()
                if filters.activity_status == 'active':
                    cutoff = now - timedelta(days=7)
                    query = query.having(func.max(User.updated_at) >= cutoff)
                elif filters.activity_status == 'inactive':
                    active_cutoff = now - timedelta(days=7)
                    inactive_cutoff = now - timedelta(days=30)
                    query = query.having(
                        and_(
                            func.max(User.updated_at) < active_cutoff,
                            func.max(User.updated_at) >= inactive_cutoff
                        )
                    )
                elif filters.activity_status == 'dormant':
                    cutoff = now - timedelta(days=30)
                    query = query.having(func.max(User.updated_at) < cutoff)
            
            # Apply sorting
            if filters.sort_by == 'name':
                sort_column = User.name
            elif filters.sort_by == 'email':
                sort_column = User.email
            elif filters.sort_by == 'created_at':
                sort_column = User.created_at
            elif filters.sort_by == 'posts_count':
                sort_column = func.count(Post.id.distinct())
            else:
                sort_column = User.created_at
            
            if filters.sort_direction == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Get total count
            count_query = select(func.count()).select_from(
                query.subquery()
            )
            total_count = await self.db.scalar(count_query)
            
            # Apply pagination
            offset = (pagination.page - 1) * pagination.per_page
            paginated_query = query.offset(offset).limit(pagination.per_page)
            
            # Execute query
            result = await self.db.execute(paginated_query)
            user_data = result.all()
            
            # Format user responses
            users = []
            for data in user_data:
                activity_status = self._determine_activity_status(data.last_activity)
                
                users.append(UserSummaryResponse(
                    id=data.id,
                    name=data.name,
                    email=data.email,
                    role=data.role,
                    activity_status=activity_status,
                    created_at=data.created_at,
                    last_login_at=data.last_activity,
                    posts_count=data.posts_count or 0,
                    comments_count=data.comments_count or 0,
                    likes_count=data.likes_count or 0,
                    is_verified=data.email_verified_at is not None,
                    can_edit=True,  # Based on admin permissions
                    can_delete=data.role != 'admin'  # Prevent admin deletion
                ))
            
            # Get role counts for filters
            role_counts = await self._get_role_counts()
            
            # Build pagination response
            pagination_response = PaginationResponse(
                page=pagination.page,
                per_page=pagination.per_page,
                total=total_count or 0,
                pages=((total_count or 0) + pagination.per_page - 1) // pagination.per_page
            )
            
            return PaginatedUsersResponse(
                users=users,
                pagination=pagination_response,
                filters=filters,
                total_count=total_count or 0,
                role_counts=role_counts
            )
            
        except Exception as e:
            raise UserManagementError(f"Failed to get users: {str(e)}")
    
    async def update_user_role(
        self, 
        user_id: UUID, 
        new_role: str, 
        admin_id: UUID,
        reason: Optional[str] = None
    ) -> UserResponse:
        """
        Update user role with validation and audit logging.
        
        Args:
            user_id: Target user ID
            new_role: New role to assign
            admin_id: Admin performing the change
            reason: Reason for role change
            
        Returns:
            UserResponse: Updated user data
        """
        try:
            async with self.db.begin():
                # Get current user
                user = await self.db.get(User, user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")
                
                # Validate role change
                old_role = user.role
                self._validate_role_change(old_role, new_role, admin_id, user_id)
                
                # Update user role
                user.role = new_role
                user.updated_at = datetime.utcnow()
                
                # Log the change in audit
                await self._log_role_change(
                    user_id=user_id,
                    admin_id=admin_id,
                    old_role=old_role,
                    new_role=new_role,
                    reason=reason
                )
                
                await self.db.commit()
                
                return UserResponse.from_orm(user)
                
        except Exception as e:
            await self.db.rollback()
            raise UserManagementError(f"Failed to update user role: {str(e)}")
    
    async def delete_user(
        self, 
        user_id: UUID, 
        admin_id: UUID, 
        reason: str
    ) -> bool:
        """
        Delete user account with proper data handling.
        
        Args:
            user_id: Target user ID
            admin_id: Admin performing deletion
            reason: Reason for deletion
            
        Returns:
            bool: Success status
        """
        try:
            async with self.db.begin():
                user = await self.db.get(User, user_id)
                if not user:
                    raise UserNotFoundError(f"User {user_id} not found")
                
                # Validate deletion permissions
                self._validate_user_deletion(user, admin_id, user_id)
                
                # Archive user data before deletion (soft delete approach)
                await self._archive_user_data(user)
                
                # Log the deletion
                await self._log_user_deletion(
                    user_id=user_id,
                    admin_id=admin_id,
                    reason=reason
                )
                
                # Mark user as deleted instead of hard delete
                user.email = f"deleted_{user_id}@deleted.local"
                user.name = f"Deleted User {user_id}"
                user.role = "deleted"
                user.updated_at = datetime.utcnow()
                
                await self.db.commit()
                
                return True
                
        except Exception as e:
            await self.db.rollback()
            raise UserManagementError(f"Failed to delete user: {str(e)}")
    
    async def get_user_stats(self) -> UserStatsResponse:
        """
        Get comprehensive user statistics.
        
        Returns:
            UserStatsResponse: Complete user statistics
        """
        try:
            # Total users
            total_users = await self.db.scalar(
                select(func.count(User.id)).where(User.role != 'deleted')
            )
            
            # Active users (last 7 days)
            active_cutoff = datetime.utcnow() - timedelta(days=7)
            active_users = await self.db.scalar(
                select(func.count(User.id)).where(
                    and_(
                        User.updated_at >= active_cutoff,
                        User.role != 'deleted'
                    )
                )
            )
            
            # New users this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_users_this_month = await self.db.scalar(
                select(func.count(User.id)).where(
                    and_(
                        User.created_at >= month_start,
                        User.role != 'deleted'
                    )
                )
            )
            
            # Users by role
            users_by_role = await self._get_role_counts()
            
            # Users by activity status
            users_by_activity = await self._get_activity_status_counts()
            
            # Recent signups
            recent_signups = await self._get_recent_signups()
            
            # Top contributors
            top_contributors = await self._get_top_contributors()
            
            # Growth metrics
            growth_metrics = await self._calculate_growth_metrics()
            
            return UserStatsResponse(
                total_users=total_users or 0,
                active_users=active_users or 0,
                new_users_this_month=new_users_this_month or 0,
                users_by_role=users_by_role,
                users_by_activity_status=users_by_activity,
                recent_signups=recent_signups,
                top_contributors=top_contributors,
                growth_metrics=growth_metrics
            )
            
        except Exception as e:
            raise UserManagementError(f"Failed to get user stats: {str(e)}")
    
    async def bulk_update_users(
        self, 
        updates: List[BulkUserUpdate],
        admin_id: UUID
    ) -> BulkOperationResponse:
        """
        Perform bulk user operations with transaction safety.
        
        Args:
            updates: List of user updates to perform
            admin_id: Admin performing operations
            
        Returns:
            BulkOperationResponse: Operation results summary
        """
        results = []
        errors = []
        
        try:
            async with self.db.begin():
                for update in updates:
                    try:
                        if update.operation == "update_role":
                            await self.update_user_role(
                                update.user_id, 
                                update.new_role, 
                                admin_id,
                                update.reason
                            )
                        elif update.operation == "delete":
                            await self.delete_user(
                                update.user_id,
                                admin_id,
                                update.reason or "Bulk deletion"
                            )
                        elif update.operation == "deactivate":
                            await self._deactivate_user(update.user_id, admin_id, update.reason)
                        elif update.operation == "activate":
                            await self._activate_user(update.user_id, admin_id, update.reason)
                        
                        results.append({"user_id": update.user_id, "status": "success"})
                        
                    except Exception as e:
                        errors.append({
                            "user_id": update.user_id,
                            "error": str(e),
                            "operation": update.operation
                        })
                
                await self.db.commit()
                
        except Exception as e:
            await self.db.rollback()
            raise UserManagementError(f"Bulk operation failed: {str(e)}")
        
        return BulkOperationResponse(
            total_processed=len(updates),
            successful_operations=len(results),
            failed_operations=len(errors),
            errors=errors,
            summary=self._build_operation_summary(results, errors)
        )
    
    async def get_user_activity_history(self, user_id: UUID) -> List[UserAuditLogResponse]:
        """
        Get user activity history and audit trail.
        
        Args:
            user_id: Target user ID
            
        Returns:
            List[UserAuditLogResponse]: User audit history
        """
        try:
            query = select(AccessAuditLog).where(
                AccessAuditLog.user_id == user_id
            ).options(
                selectinload(AccessAuditLog.admin_user)
            ).order_by(AccessAuditLog.created_at.desc()).limit(100)
            
            result = await self.db.execute(query)
            audit_logs = result.scalars().all()
            
            history = []
            for log in audit_logs:
                history.append(UserAuditLogResponse(
                    id=log.id,
                    action=log.action,
                    admin_user=UserSummaryResponse.from_orm(log.admin_user) if log.admin_user else None,
                    old_values=log.old_values or {},
                    new_values=log.new_values or {},
                    reason=log.reason,
                    created_at=log.created_at
                ))
            
            return history
            
        except Exception as e:
            raise UserManagementError(f"Failed to get user history: {str(e)}")
    
    # Helper methods
    async def _get_role_counts(self) -> Dict[str, int]:
        """Get count of users by role."""
        query = select(
            User.role,
            func.count(User.id).label('count')
        ).where(User.role != 'deleted')\
        .group_by(User.role)
        
        result = await self.db.execute(query)
        role_data = result.all()
        
        return {row.role: row.count for row in role_data}
    
    async def _get_activity_status_counts(self) -> Dict[str, int]:
        """Get count of users by activity status."""
        now = datetime.utcnow()
        active_cutoff = now - timedelta(days=7)
        inactive_cutoff = now - timedelta(days=30)
        
        # Active users
        active_count = await self.db.scalar(
            select(func.count(User.id)).where(
                and_(
                    User.updated_at >= active_cutoff,
                    User.role != 'deleted'
                )
            )
        )
        
        # Inactive users
        inactive_count = await self.db.scalar(
            select(func.count(User.id)).where(
                and_(
                    User.updated_at < active_cutoff,
                    User.updated_at >= inactive_cutoff,
                    User.role != 'deleted'
                )
            )
        )
        
        # Dormant users
        dormant_count = await self.db.scalar(
            select(func.count(User.id)).where(
                and_(
                    User.updated_at < inactive_cutoff,
                    User.role != 'deleted'
                )
            )
        )
        
        return {
            'active': active_count or 0,
            'inactive': inactive_count or 0,
            'dormant': dormant_count or 0
        }
    
    async def _get_recent_signups(self) -> List[UserSummaryResponse]:
        """Get recent user signups."""
        query = select(User).where(User.role != 'deleted')\
            .order_by(User.created_at.desc()).limit(10)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return [
            UserSummaryResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                activity_status=self._determine_activity_status(user.updated_at),
                created_at=user.created_at,
                last_login_at=user.updated_at,
                posts_count=0,  # Would need separate query
                comments_count=0,  # Would need separate query
                likes_count=0,  # Would need separate query
                is_verified=user.email_verified_at is not None,
                can_edit=True,
                can_delete=user.role != 'admin'
            ) for user in users
        ]
    
    async def _get_top_contributors(self) -> List[UserContributorResponse]:
        """Get top contributing users."""
        query = select(
            User.id,
            User.name,
            User.email,
            User.role,
            User.created_at,
            User.updated_at,
            User.email_verified_at,
            func.count(Post.id.distinct()).label('total_posts'),
            func.count(Like.id.distinct()).label('total_likes_received'),
            func.count(Comment.id.distinct()).label('total_comments_received')
        ).select_from(User)\
        .outerjoin(Post, User.id == Post.user_id)\
        .outerjoin(Like, Post.id == Like.post_id)\
        .outerjoin(Comment, Post.id == Comment.post_id)\
        .where(User.role != 'deleted')\
        .group_by(
            User.id, User.name, User.email, User.role,
            User.created_at, User.updated_at, User.email_verified_at
        )\
        .order_by(desc('total_posts'))\
        .limit(10)
        
        result = await self.db.execute(query)
        contributors_data = result.all()
        
        contributors = []
        for data in contributors_data:
            user_summary = UserSummaryResponse(
                id=data.id,
                name=data.name,
                email=data.email,
                role=data.role,
                activity_status=self._determine_activity_status(data.updated_at),
                created_at=data.created_at,
                last_login_at=data.updated_at,
                posts_count=data.total_posts or 0,
                comments_count=0,
                likes_count=data.total_likes_received or 0,
                is_verified=data.email_verified_at is not None,
                can_edit=True,
                can_delete=data.role != 'admin'
            )
            
            engagement_score = self._calculate_engagement_score(
                data.total_posts or 0,
                data.total_likes_received or 0,
                data.total_comments_received or 0
            )
            
            contribution_level = self._determine_contribution_level(engagement_score)
            
            contributors.append(UserContributorResponse(
                user=user_summary,
                total_posts=data.total_posts or 0,
                total_likes_received=data.total_likes_received or 0,
                total_comments_received=data.total_comments_received or 0,
                engagement_score=engagement_score,
                contribution_level=contribution_level
            ))
        
        return contributors
    
    async def _calculate_growth_metrics(self) -> UserGrowthMetricsResponse:
        """Calculate user growth and retention metrics."""
        # Get daily signups for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_query = select(
            func.date(User.created_at).label('signup_date'),
            func.count(User.id).label('signups')
        ).where(
            and_(
                User.created_at >= thirty_days_ago,
                User.role != 'deleted'
            )
        ).group_by(func.date(User.created_at))\
        .order_by('signup_date')
        
        result = await self.db.execute(daily_query)
        daily_data = result.all()
        
        daily_signups = [
            DailySignupResponse(
                date=row.signup_date,
                signups=row.signups
            ) for row in daily_data
        ]
        
        # Calculate growth rate (placeholder)
        monthly_growth_rate = 5.0  # Would need historical comparison
        retention_rate = 85.0      # Would need retention tracking
        churn_rate = 15.0          # Would need churn analysis
        
        return UserGrowthMetricsResponse(
            daily_signups=daily_signups,
            monthly_growth_rate=monthly_growth_rate,
            retention_rate=retention_rate,
            churn_rate=churn_rate
        )
    
    def _validate_role_change(self, old_role: str, new_role: str, admin_id: UUID, user_id: UUID):
        """Validate role change is allowed."""
        if old_role == new_role:
            raise ValueError("New role must be different from current role")
        
        # Prevent self-demotion for admins
        if admin_id == user_id and old_role == "admin" and new_role != "admin":
            raise PermissionError("Cannot demote yourself from admin role")
        
        # Validate role values
        valid_roles = {'user', 'editor', 'admin'}
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role: {new_role}")
    
    def _validate_user_deletion(self, user: User, admin_id: UUID, user_id: UUID):
        """Validate user can be deleted."""
        if user.role == 'admin':
            raise PermissionError("Cannot delete admin users")
        
        if admin_id == user_id:
            raise PermissionError("Cannot delete yourself")
    
    async def _archive_user_data(self, user: User):
        """Archive user data before deletion."""
        # This would implement data archival strategy
        # For now, we're using soft delete approach
        pass
    
    async def _log_role_change(self, user_id: UUID, admin_id: UUID, old_role: str, new_role: str, reason: Optional[str]):
        """Log role change in audit trail."""
        audit_log = AccessAuditLog(
            user_id=user_id,
            admin_user_id=admin_id,
            action='role_change',
            old_values={'role': old_role},
            new_values={'role': new_role},
            reason=reason
        )
        self.db.add(audit_log)
    
    async def _log_user_deletion(self, user_id: UUID, admin_id: UUID, reason: str):
        """Log user deletion in audit trail."""
        audit_log = AccessAuditLog(
            user_id=user_id,
            admin_user_id=admin_id,
            action='account_deleted',
            old_values={},
            new_values={'status': 'deleted'},
            reason=reason
        )
        self.db.add(audit_log)
    
    async def _deactivate_user(self, user_id: UUID, admin_id: UUID, reason: Optional[str]):
        """Deactivate user account."""
        user = await self.db.get(User, user_id)
        if user:
            user.role = 'deactivated'
            user.updated_at = datetime.utcnow()
            
            await self._log_status_change(user_id, admin_id, 'deactivated', reason)
    
    async def _activate_user(self, user_id: UUID, admin_id: UUID, reason: Optional[str]):
        """Activate user account."""
        user = await self.db.get(User, user_id)
        if user:
            user.role = 'user'  # Default to user role
            user.updated_at = datetime.utcnow()
            
            await self._log_status_change(user_id, admin_id, 'activated', reason)
    
    async def _log_status_change(self, user_id: UUID, admin_id: UUID, action: str, reason: Optional[str]):
        """Log status change in audit trail."""
        audit_log = AccessAuditLog(
            user_id=user_id,
            admin_user_id=admin_id,
            action=f'status_change_{action}',
            old_values={},
            new_values={'action': action},
            reason=reason
        )
        self.db.add(audit_log)
    
    def _determine_activity_status(self, last_activity: Optional[datetime]) -> str:
        """Determine user activity status based on last activity."""
        if not last_activity:
            return 'dormant'
        
        now = datetime.utcnow()
        days_since_activity = (now - last_activity).days
        
        if days_since_activity <= 7:
            return 'active'
        elif days_since_activity <= 30:
            return 'inactive'
        else:
            return 'dormant'
    
    def _calculate_engagement_score(self, posts: int, likes: int, comments: int) -> float:
        """Calculate user engagement score."""
        # Weighted calculation
        score = (posts * 3.0) + (likes * 0.5) + (comments * 1.0)
        return round(score, 2)
    
    def _determine_contribution_level(self, score: float) -> str:
        """Determine contribution level based on engagement score."""
        if score >= 50:
            return 'high'
        elif score >= 20:
            return 'medium'
        else:
            return 'low'
    
    def _build_operation_summary(self, results: List, errors: List) -> Dict[str, int]:
        """Build summary of bulk operations."""
        summary = {
            'successful': len(results),
            'failed': len(errors),
            'total': len(results) + len(errors)
        }
        
        # Count operations by type
        for result in results:
            op_type = result.get('operation', 'unknown')
            summary[f'successful_{op_type}'] = summary.get(f'successful_{op_type}', 0) + 1
        
        for error in errors:
            op_type = error.get('operation', 'unknown')
            summary[f'failed_{op_type}'] = summary.get(f'failed_{op_type}', 0) + 1
        
        return summary 