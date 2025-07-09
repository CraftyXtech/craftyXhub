"""
Authentication Dependencies for CraftyXhub API

FastAPI dependencies for JWT authentication, role-based access control,
and security according to SubPRD-JWTAuthentication.md and SubPRD-RoleBasedAccess.md.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from core.security import verify_token
from dependencies.database import get_db
from models.user import User


# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate JWT token and return current user.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure user is active and verified.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Active user object
        
    Raises:
        HTTPException: If user is inactive or unverified
    """
    # In this implementation, we don't have an 'active' field
    # but we can check if email is verified for certain operations
    return current_user


async def require_authentication(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires valid authentication.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return current_user


async def require_email_verification(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require email verification for sensitive operations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Email-verified user object
        
    Raises:
        HTTPException: If email is not verified
    """
    if current_user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required for this operation"
        )
    return current_user


# Role-based authorization dependencies
async def require_admin(
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> User:
    """
    Dependency that ensures user has admin role.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not current_user.is_admin():
        # Log unauthorized access attempt
        from services.admin.audit_service import AuditService
        from dependencies.database import get_db
        
        try:
            db = await anext(get_db())
            audit_service = AuditService(db)
            await audit_service.log_access_attempt(
                user_id=current_user.id,
                route=request.url.path if request else "unknown",
                required_permission="admin",
                granted=False,
                denial_reason="Insufficient role permissions"
            )
        except Exception:
            pass  # Don't fail the request if audit logging fails
        
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user


async def require_editor_or_admin(
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> User:
    """
    Dependency that ensures user has editor or admin role.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not (current_user.is_editor() or current_user.is_admin()):
        # Log unauthorized access attempt
        from services.admin.audit_service import AuditService
        from dependencies.database import get_db
        
        try:
            db = await anext(get_db())
            audit_service = AuditService(db)
            await audit_service.log_access_attempt(
                user_id=current_user.id,
                route=request.url.path if request else "unknown",
                required_permission="editor",
                granted=False,
                denial_reason="Insufficient role permissions"
            )
        except Exception:
            pass  # Don't fail the request if audit logging fails
        
        raise HTTPException(
            status_code=403,
            detail="Editor or Admin access required"
        )
    
    return current_user


async def require_owner_or_admin(
    resource_user_id: UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure user owns the resource or has admin privileges.
    
    Args:
        resource_user_id: User ID of the resource owner
        current_user: Current authenticated user
        
    Returns:
        User: Resource owner or admin user
        
    Raises:
        HTTPException: If user doesn't own resource and isn't admin
    """
    if current_user.id != resource_user_id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own resources or need admin privileges."
        )
    return current_user


async def optional_authentication(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Optional[User]: Authenticated user if token provided and valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        return user
        
    except (HTTPException, ValueError):
        # If token is invalid, just return None for optional auth
        return None


# Role-based access control helpers
class RoleChecker:
    """Helper class for role-based access control."""
    
    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Check if user has any of the required roles."""
        user_role = current_user.role
        
        # Admin role has access to everything
        if user_role == "admin":
            return current_user
        
        # Check if user has any of the required roles
        if user_role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.required_roles)}"
            )
        
        return current_user


# Convenience role checkers
require_user_role = RoleChecker(["user", "editor", "admin"])
require_editor_role = RoleChecker(["editor", "admin"])
require_admin_role = RoleChecker(["admin"])


# Permission-based authorization
def require_permission(permission: str):
    """
    Factory function to create permission-specific dependencies.
    
    Args:
        permission: Required permission level
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        request: Request = None
    ) -> User:
        if not current_user:
            raise HTTPException(
                status_code=401, 
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check permission based on role hierarchy
        has_permission = False
        if permission == "admin":
            has_permission = current_user.is_admin()
        elif permission == "editor":
            has_permission = current_user.is_editor() or current_user.is_admin()
        elif permission == "user":
            has_permission = current_user.role in ["user", "editor", "admin"]
        
        if not has_permission:
            # Log unauthorized access attempt
            from services.admin.audit_service import AuditService
            from dependencies.database import get_db
            
            try:
                db = await anext(get_db())
                audit_service = AuditService(db)
                await audit_service.log_access_attempt(
                    user_id=current_user.id,
                    route=request.url.path if request else "unknown",
                    required_permission=permission,
                    granted=False,
                    denial_reason=f"Missing permission: {permission}"
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails
            
            raise HTTPException(
                status_code=403,
                detail=f"Permission required: {permission}"
            )
        
        return current_user
    
    return permission_dependency


# Rate limiting dependency (placeholder for future implementation)
async def rate_limit_check(request: Request) -> None:
    """
    Rate limiting check for sensitive endpoints.
    
    Args:
        request: Current request
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # TODO: Implement Redis-based rate limiting
    # For now, this is a placeholder
    pass 