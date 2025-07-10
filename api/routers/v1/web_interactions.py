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