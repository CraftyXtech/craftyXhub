"""
Web Interactions API Router

Provides endpoints for user interactions with posts and comments
such as likes, bookmarks, views, and social engagement features.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params
from dependencies.web_auth import get_optional_current_user, get_rate_limit_info
from models.user import User
from services.web.interaction_service import WebInteractionService
from schemas.web.interactions import (
    InteractionResponse, InteractionCountsResponse, InteractionStatusResponse,
    BulkInteractionRequest, BulkInteractionResponse, UserInteractionHistoryRequest,
    UserInteractionHistoryResponse, InteractionAnalyticsResponse, PopularContentResponse,
    TrendingPostsResponse, EngagementStatsResponse, InteractionTypeStats
)

router = APIRouter(prefix="/interactions", tags=["Web Interactions"])


@router.post("/posts/{post_id}/like", response_model=InteractionResponse)
async def toggle_post_like(
    post_id: UUID,
    request: Request,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle like status for a post.
    
    - **post_id**: Post UUID to like/unlike
    
    Requires authentication. Returns updated like status and count.
    Handles rate limiting to prevent spam interactions.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to like posts"
        )
    
    service = WebInteractionService(db)
    
    # Get client information for rate limiting
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Toggle like
    response = await service.toggle_like(
        post_id=post_id,
        user=current_user,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    return response


@router.post("/posts/{post_id}/bookmark", response_model=InteractionResponse)
async def toggle_post_bookmark(
    post_id: UUID,
    request: Request,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle bookmark status for a post.
    
    - **post_id**: Post UUID to bookmark/unbookmark
    
    Requires authentication. Allows users to save posts for later reading.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to bookmark posts"
        )
    
    service = WebInteractionService(db)
    
    # Toggle bookmark
    response = await service.toggle_bookmark(
        post_id=post_id,
        user=current_user
    )
    
    return response


@router.post("/posts/{post_id}/view", response_model=InteractionResponse)
async def record_post_view(
    post_id: UUID,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a view for a post.
    
    - **post_id**: Post UUID to record view for
    
    Used for analytics and trending calculations.
    Handles view deduplication and anonymous tracking.
    """
    service = WebInteractionService(db)
    
    # Get client information
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Record view
    response = await service.record_view(
        post_id=post_id,
        user=current_user,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return response


@router.get("/posts/{post_id}/status", response_model=InteractionStatusResponse)
async def get_post_interaction_status(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's interaction status with a post.
    
    - **post_id**: Post UUID to check interactions for
    
    Returns:
    - Like status (liked/not liked)
    - Bookmark status (bookmarked/not bookmarked)
    - View status and timestamp
    - Total interaction counts
    """
    service = WebInteractionService(db)
    
    # Get interaction status
    status_response = await service.get_interaction_status(
        post_id=post_id,
        user=current_user
    )
    
    return status_response


@router.get("/posts/{post_id}/counts", response_model=InteractionCountsResponse)
async def get_post_interaction_counts(
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get interaction counts for a post.
    
    - **post_id**: Post UUID to get counts for
    
    Returns public interaction statistics without requiring authentication.
    """
    service = WebInteractionService(db)
    
    # Get interaction counts
    counts_response = await service.get_interaction_counts(post_id)
    
    return counts_response


@router.post("/bulk", response_model=BulkInteractionResponse)
async def bulk_interactions(
    request_data: BulkInteractionRequest,
    request: Request,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform multiple interactions at once.
    
    - **interactions**: List of interaction operations to perform
    
    Useful for batch operations like bulk bookmarking or liking.
    Requires authentication and enforces rate limiting.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for bulk interactions"
        )
    
    service = WebInteractionService(db)
    
    # Get client information
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Perform bulk interactions
    response = await service.bulk_interaction(
        interactions=request_data.interactions,
        user=current_user,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    return response


@router.get("/users/me/history", response_model=UserInteractionHistoryResponse)
async def get_user_interaction_history(
    request_data: UserInteractionHistoryRequest = Depends(),
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's interaction history.
    
    - **interaction_type**: Filter by interaction type (like, bookmark, view)
    - **date_from**: Start date for filtering
    - **date_to**: End date for filtering
    - **page**: Page number
    - **per_page**: Items per page
    
    Returns paginated history of user's interactions with posts.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view interaction history"
        )
    
    service = WebInteractionService(db)
    
    # Get interaction history
    history_response = await service.get_user_interaction_history(
        user=current_user,
        filters=request_data,
        pagination=pagination
    )
    
    return history_response


@router.get("/users/me/liked", response_model=UserInteractionHistoryResponse)
async def get_user_liked_posts(
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get posts liked by the current user.
    
    Returns paginated list of liked posts with interaction timestamps.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view liked posts"
        )
    
    service = WebInteractionService(db)
    
    # Get liked posts
    liked_posts = await service.get_user_liked_posts(
        user=current_user,
        pagination=pagination
    )
    
    return liked_posts


@router.get("/users/me/bookmarks", response_model=UserInteractionHistoryResponse)
async def get_user_bookmarked_posts(
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get posts bookmarked by the current user.
    
    Returns paginated list of bookmarked posts with bookmark timestamps.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view bookmarks"
        )
    
    service = WebInteractionService(db)
    
    # Get bookmarked posts
    bookmarked_posts = await service.get_user_bookmarked_posts(
        user=current_user,
        pagination=pagination
    )
    
    return bookmarked_posts


@router.get("/analytics/popular", response_model=PopularContentResponse)
async def get_popular_content(
    timeframe: str = "week",  # day, week, month, year, all
    limit: int = 20,
    content_type: str = "posts",  # posts, comments
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular content based on interaction metrics.
    
    - **timeframe**: Time period for popularity calculation
    - **limit**: Maximum number of items to return
    - **content_type**: Type of content (posts or comments)
    
    Returns content ranked by engagement scores and interaction counts.
    """
    # Validate parameters
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if content_type not in ["posts", "comments"]:
        raise HTTPException(status_code=422, detail="Invalid content type")
    
    if limit > 100:
        raise HTTPException(status_code=422, detail="Limit cannot exceed 100")
    
    service = WebInteractionService(db)
    
    # Get popular content
    popular_content = await service.get_popular_content(
        timeframe=timeframe,
        limit=limit,
        content_type=content_type
    )
    
    return popular_content


@router.get("/analytics/trending", response_model=TrendingPostsResponse)
async def get_trending_posts(
    timeframe: str = "day",
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending posts based on recent engagement velocity.
    
    - **timeframe**: Time period for trending calculation
    - **limit**: Maximum number of posts to return
    - **category**: Filter by category slug (optional)
    
    Uses engagement velocity algorithm to identify rapidly growing content.
    """
    # Validate timeframe
    if timeframe not in ["hour", "day", "week"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe for trending")
    
    if limit > 50:
        raise HTTPException(status_code=422, detail="Limit cannot exceed 50")
    
    service = WebInteractionService(db)
    
    # Get trending posts
    trending_posts = await service.get_trending_posts(
        timeframe=timeframe,
        limit=limit,
        category=category
    )
    
    return trending_posts


@router.get("/analytics/engagement", response_model=EngagementStatsResponse)
async def get_engagement_statistics(
    timeframe: str = "week",
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform-wide engagement statistics.
    
    - **timeframe**: Time period for statistics calculation
    
    Returns aggregated interaction metrics and engagement trends.
    """
    # Validate timeframe
    if timeframe not in ["day", "week", "month", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = WebInteractionService(db)
    
    # Get engagement statistics
    engagement_stats = await service.get_engagement_statistics(timeframe)
    
    return engagement_stats


@router.get("/stats/types", response_model=InteractionTypeStats)
async def get_interaction_type_statistics(
    timeframe: str = "week",
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics broken down by interaction type.
    
    - **timeframe**: Time period for statistics calculation
    
    Returns counts and trends for likes, bookmarks, views, and comments.
    """
    # Validate timeframe
    if timeframe not in ["day", "week", "month", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = WebInteractionService(db)
    
    # Get interaction type statistics
    type_stats = await service.get_interaction_type_statistics(timeframe)
    
    return type_stats


@router.delete("/users/me/interactions")
async def clear_user_interactions(
    interaction_type: Optional[str] = None,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear user's interaction history.
    
    - **interaction_type**: Type of interactions to clear (optional, clears all if not specified)
    
    Allows users to clear their interaction history for privacy.
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to clear interactions"
        )
    
    # Validate interaction type if provided
    if interaction_type and interaction_type not in ["like", "bookmark", "view"]:
        raise HTTPException(status_code=422, detail="Invalid interaction type")
    
    service = WebInteractionService(db)
    
    # Clear interactions
    cleared_count = await service.clear_user_interactions(
        user=current_user,
        interaction_type=interaction_type
    )
    
    return {
        "message": f"Cleared {cleared_count} interactions",
        "interaction_type": interaction_type or "all",
        "cleared_count": cleared_count
    } 