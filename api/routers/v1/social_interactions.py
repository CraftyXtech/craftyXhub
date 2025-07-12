

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, PaginationParams
from dependencies.web_auth import get_optional_current_user, get_current_user
from models.user import User
from services.interactions.like_service import LikeService
from services.interactions.bookmark_service import BookmarkService
from services.interactions.interaction_service import InteractionService
from services.users.user_service import UserService
from schemas.interaction import (
    LikeToggleResponse, BookmarkToggleResponse, FollowToggleResponse,
    InteractionStatsResponse, UserInteractionSummaryResponse,
    TrendingContentResponse, PopularContentRequest
)

router = APIRouter(prefix="/social", tags=["Social Interactions"])


@router.post("/posts/{post_id}/like", response_model=LikeToggleResponse)
async def toggle_post_like(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle like status for a post."""
    service = LikeService(db)
    return await service.toggle_like(post_id, current_user.id)


@router.get("/posts/{post_id}/likes")
async def get_post_likes(
    post_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Get users who liked a post."""
    service = InteractionService(db)
    return await service.get_content_likers(
        content_type="post",
        content_id=post_id,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.post("/posts/{post_id}/bookmark", response_model=BookmarkToggleResponse)
async def toggle_post_bookmark(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle bookmark status for a post."""
    service = BookmarkService(db)
    return await service.toggle_bookmark(post_id, current_user.id)


@router.get("/posts/{post_id}/bookmarks")
async def get_post_bookmarks(
    post_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Get users who bookmarked a post."""
    service = InteractionService(db)
    return await service.get_post_bookmarkers(
        post_id=post_id,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.post("/posts/{post_id}/view")
async def record_post_view(
    post_id: UUID,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a view for a post."""
    service = InteractionService(db)
    
    user_id = current_user.id if current_user else None
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    return await service.record_view(
        post_id=post_id,
        user_id=user_id,
        client_ip=client_ip,
        user_agent=user_agent
    )


@router.post("/users/{user_id}/follow", response_model=FollowToggleResponse)
async def toggle_user_follow(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow or unfollow a user."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    service = UserService(db)
    return await service.toggle_follow(current_user.id, user_id)


@router.get("/users/{user_id}/followers")
async def get_user_followers(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's followers."""
    service = UserService(db)
    return await service.get_user_followers(
        user_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/users/{user_id}/following")
async def get_user_following(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users that this user follows."""
    service = UserService(db)
    return await service.get_user_following(
        user_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/posts/{post_id}/stats", response_model=InteractionStatsResponse)
async def get_post_interaction_stats(
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive interaction statistics for a post."""
    service = InteractionService(db)
    return await service.get_post_engagement_stats(post_id)


@router.get("/users/{user_id}/interaction-summary", response_model=UserInteractionSummaryResponse)
async def get_user_interaction_summary(
    user_id: UUID,
    post_id: UUID = Query(..., description="Post ID to check interactions for"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's interaction summary with a specific post."""
    service = InteractionService(db)
    return await service.get_user_interaction_summary(user_id, post_id)


@router.get("/trending/posts", response_model=TrendingContentResponse)
async def get_trending_posts(
    days: int = Query(7, description="Number of days to consider for trending", ge=1, le=365),
    limit: int = Query(10, description="Number of posts to return", ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get trending posts based on recent engagement."""
    service = InteractionService(db)
    return await service.get_trending_posts(days=days, limit=limit)


@router.get("/popular/content")
async def get_popular_content(
    request: PopularContentRequest = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get popular content across different timeframes."""
    service = InteractionService(db)
    return await service.get_popular_content(
        content_type=request.content_type,
        timeframe=request.timeframe,
        limit=request.limit
    )


@router.get("/me/bookmarks")
async def get_my_bookmarks(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookmarked posts."""
    service = InteractionService(db)
    return await service.get_user_bookmarks(
        user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.get("/me/liked-posts")
async def get_my_liked_posts(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's liked posts."""
    service = InteractionService(db)
    return await service.get_user_liked_posts(
        user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.get("/me/activity")
async def get_my_activity(
    activity_type: Optional[str] = Query(None, description="Filter by activity type: like, bookmark, follow, comment"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's activity history."""
    service = UserService(db)
    return await service.get_user_activity_history(
        user_id=current_user.id,
        activity_type=activity_type,
        limit=pagination.limit,
        offset=pagination.offset
    )


@router.delete("/posts/{post_id}/like")
async def remove_post_like(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove like from a post."""
    service = InteractionService(db)
    success = await service.unlike_content(current_user.id, "post", post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Like not found")
    return {"message": "Like removed successfully"}


@router.delete("/posts/{post_id}/bookmark")
async def remove_post_bookmark(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove bookmark from a post."""
    service = InteractionService(db)
    success = await service.unbookmark_post(current_user.id, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"message": "Bookmark removed successfully"}


@router.delete("/users/{user_id}/follow")
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user."""
    service = UserService(db)
    success = await service.unfollow_user(current_user.id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    return {"message": "User unfollowed successfully"} 