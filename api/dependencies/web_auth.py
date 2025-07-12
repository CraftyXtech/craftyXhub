
from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user as auth_get_current_user
from models.user import User
from core.exceptions import AuthenticationError


optional_bearer = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        user = await auth_get_current_user(credentials.credentials, db)
        return user
    except (AuthenticationError, HTTPException):
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user (required)."""
    try:
        user = await auth_get_current_user(credentials.credentials, db)
        return user
    except (AuthenticationError, HTTPException) as e:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_or_redirect(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user or provide redirect information."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Redirect-URL": f"/login?redirect={request.url.path}"
            }
        )
    
    try:
        user = await auth_get_current_user(credentials.credentials, db)
        return user
    except (AuthenticationError, HTTPException):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Redirect-URL": f"/login?redirect={request.url.path}"
            }
        )


async def verify_user_can_comment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify user can create comments."""
    if current_user.role == "banned":
        raise HTTPException(
            status_code=403,
            detail="Account is banned from commenting"
        )
    
    if not current_user.email_verified_at:
        raise HTTPException(
            status_code=403,
            detail="Email verification required to comment"
        )
    
    return current_user


async def verify_user_can_interact(
    user: Optional[User] = Depends(get_optional_current_user)
) -> User:
    """Verify user can interact with posts."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to interact with posts",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active and can interact
    if user.role == "banned":
        raise HTTPException(
            status_code=403,
            detail="Your account has been restricted from interacting with posts"
        )
    
    return user


async def get_user_context(
    user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """Get user context for frontend."""
    if not user:
        return {
            "is_authenticated": False,
            "user_id": None,
            "user_role": None,
            "can_comment": False,
            "can_interact": False,
            "can_moderate": False
        }
    
    return {
        "is_authenticated": True,
        "user_id": user.id,
        "user_role": user.role,
        "can_comment": user.role != "banned",
        "can_interact": user.role != "banned",
        "can_moderate": user.role in ["admin", "editor"]
    }


async def verify_comment_ownership(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Verify user owns the comment or has admin privileges."""
    from models.comment import Comment
    from sqlalchemy import select
    
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    is_owner = comment.user_id == current_user.id
    is_admin = current_user.role == "admin"
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )
    
    return {
        "comment": comment,
        "is_owner": is_owner,
        "is_admin": is_admin
    }


async def get_rate_limit_info(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """Get rate limiting information for the request."""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Rate limits based on user type
    if current_user:
        if current_user.role == "admin":
            rate_limit = {"requests": 1000, "window": 3600}  # 1000/hour
        elif current_user.role == "editor":
            rate_limit = {"requests": 500, "window": 3600}   # 500/hour
        else:
            rate_limit = {"requests": 100, "window": 3600}   # 100/hour
    else:
        rate_limit = {"requests": 20, "window": 3600}        # 20/hour for anonymous
    
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "user_id": current_user.id if current_user else None,
        "rate_limit": rate_limit
    }


async def check_post_access(
    post_id: str,
    user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Check user's access to a post."""
    from models.post import Post
    from sqlalchemy import select
    
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    is_published = post.status == "published" and post.published_at is not None
    
    can_view_unpublished = (
        user and 
        (user.role in ["admin", "editor"] or user.id == post.user_id)
    )
    
    # Determine access
    can_view = is_published or can_view_unpublished
    can_comment = can_view and post.comments_enabled and user and user.role != "banned"
    can_interact = can_view and user and user.role != "banned"
    
    return {
        "post": post,
        "can_view": can_view,
        "can_comment": can_comment,
        "can_interact": can_interact,
        "is_published": is_published,
        "is_owner": user and user.id == post.user_id
    } 