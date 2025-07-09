"""
Web-specific authentication dependencies.

Provides authentication utilities for public-facing web endpoints
with optional authentication and user context handling.
"""

from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from core.exceptions import AuthenticationError


# Optional bearer token for web endpoints
optional_bearer = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    This dependency is used for web endpoints that can work both
    with authenticated and anonymous users.
    
    Args:
        request: FastAPI request object
        credentials: Optional bearer token
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # Use the existing auth dependency to get user
        user = await get_current_user(credentials.credentials, db)
        return user
    except (AuthenticationError, HTTPException):
        # If authentication fails, return None instead of raising
        return None


async def get_current_user_or_redirect(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user or redirect to login.
    
    This dependency is used for web endpoints that require authentication
    and should redirect to login page if user is not authenticated.
    
    Args:
        request: FastAPI request object
        credentials: Optional bearer token
        db: Database session
        
    Returns:
        User object if authenticated
        
    Raises:
        HTTPException: 401 with redirect information if not authenticated
    """
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
        user = await get_current_user(credentials.credentials, db)
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
    user: Optional[User] = Depends(get_optional_current_user)
) -> User:
    """
    Verify that user can comment on posts.
    
    Args:
        user: Current user (optional)
        
    Returns:
        User object if authorized to comment
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not authorized
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to comment",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active and can comment
    if user.role == "banned":
        raise HTTPException(
            status_code=403,
            detail="Your account has been restricted from commenting"
        )
    
    return user


async def verify_user_can_interact(
    user: Optional[User] = Depends(get_optional_current_user)
) -> User:
    """
    Verify that user can interact with posts (like, bookmark).
    
    Args:
        user: Current user (optional)
        
    Returns:
        User object if authorized to interact
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not authorized
    """
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
    """
    Get user context for web responses.
    
    Provides user information and permissions for web endpoints
    that need to customize responses based on user status.
    
    Args:
        user: Current user (optional)
        
    Returns:
        Dictionary with user context information
    """
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
    user: User = Depends(get_current_user_or_redirect),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Verify that user owns the comment or can moderate it.
    
    Args:
        comment_id: Comment ID to verify
        user: Current user
        db: Database session
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: 403 if not authorized, 404 if comment not found
    """
    from models.comment import Comment
    from sqlalchemy import select
    
    # Get comment
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check ownership or moderation rights
    if comment.user_id != user.id and user.role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own comments"
        )
    
    return user


async def get_rate_limit_info(
    user: Optional[User] = Depends(get_optional_current_user)
) -> dict:
    """
    Get rate limit information for the current user.
    
    Args:
        user: Current user (optional)
        
    Returns:
        Dictionary with rate limit information
    """
    if not user:
        return {
            "comment_limit": 5,  # Anonymous users get lower limits
            "interaction_limit": 10,
            "search_limit": 20
        }
    
    # Authenticated users get higher limits
    base_limits = {
        "comment_limit": 30,
        "interaction_limit": 100,
        "search_limit": 200
    }
    
    # Premium users or higher roles get even higher limits
    if user.role in ["editor", "admin"]:
        base_limits.update({
            "comment_limit": 100,
            "interaction_limit": 500,
            "search_limit": 1000
        })
    
    return base_limits


async def check_post_access(
    post_id: str,
    user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Check user's access to a specific post.
    
    Args:
        post_id: Post ID to check
        user: Current user (optional)
        db: Database session
        
    Returns:
        Dictionary with access information
        
    Raises:
        HTTPException: 404 if post not found
    """
    from models.post import Post
    from sqlalchemy import select
    
    # Get post
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if post is published
    is_published = post.status == "published" and post.published_at is not None
    
    # Check if user can view unpublished posts
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