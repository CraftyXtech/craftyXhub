

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, PaginationParams
from dependencies.web_auth import get_optional_current_user, get_current_user
from models.user import User
from services.users.user_service import UserService
from services.analytics.analytics_service import AnalyticsService
from schemas.social import (
    UserSocialProfileResponse, UserSocialStatsResponse, UserFollowersResponse,
    UserFollowingResponse, UserActivityResponse, UserConnectionsResponse,
    MutualConnectionsResponse, SuggestedUsersResponse, UserInteractionHistoryResponse,
    SocialNetworkStatsResponse, UserInfluenceScoreResponse
)

router = APIRouter(prefix="/social/users", tags=["Social Profiles"])


@router.get("/{user_id}/profile", response_model=UserSocialProfileResponse)
async def get_user_social_profile(
    user_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive social profile for a user."""
    service = UserService(db)
    return await service.get_user_social_profile(
        user_id=user_id,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/{user_id}/stats", response_model=UserSocialStatsResponse)
async def get_user_social_stats(
    user_id: UUID,
    timeframe: str = Query("all", description="Timeframe: day, week, month, year, all"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social statistics for a user."""
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    user_service = UserService(db)
    
    # Get analytics data
    analytics_data = await analytics_service.get_user_analytics(user_id)
    
    # Get social stats
    social_stats = await user_service.get_user_social_stats(
        user_id=user_id,
        timeframe=timeframe,
        viewer_id=current_user.id if current_user else None
    )
    
    return UserSocialStatsResponse(
        **analytics_data,
        **social_stats,
        timeframe=timeframe
    )


@router.get("/{user_id}/followers", response_model=UserFollowersResponse)
async def get_user_followers(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search followers by name"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's followers with optional search."""
    service = UserService(db)
    return await service.get_user_followers_detailed(
        user_id=user_id,
        search=search,
        pagination=pagination,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/{user_id}/following", response_model=UserFollowingResponse)
async def get_user_following(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    search: Optional[str] = Query(None, description="Search following by name"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users that this user follows with optional search."""
    service = UserService(db)
    return await service.get_user_following_detailed(
        user_id=user_id,
        search=search,
        pagination=pagination,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/{user_id}/mutual-connections", response_model=MutualConnectionsResponse)
async def get_mutual_connections(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get mutual connections between current user and specified user."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot get mutual connections with yourself")
    
    service = UserService(db)
    return await service.get_mutual_connections(
        user1_id=current_user.id,
        user2_id=user_id,
        pagination=pagination
    )


@router.get("/suggestions", response_model=SuggestedUsersResponse)
async def get_suggested_users(
    limit: int = Query(10, description="Number of suggestions", ge=1, le=50),
    reason: Optional[str] = Query(None, description="Filter by suggestion reason"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get suggested users to follow."""
    service = UserService(db)
    return await service.get_suggested_users(
        user_id=current_user.id,
        limit=limit,
        reason=reason
    )


@router.get("/me/connections", response_model=UserConnectionsResponse)
async def get_my_connections(
    connection_type: str = Query("all", description="Type: followers, following, mutual, all"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's social connections."""
    if connection_type not in ["followers", "following", "mutual", "all"]:
        raise HTTPException(status_code=422, detail="Invalid connection type")
    
    service = UserService(db)
    return await service.get_user_connections(
        user_id=current_user.id,
        connection_type=connection_type,
        pagination=pagination
    )


@router.get("/{user_id}/activity", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: UUID,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's public activity feed."""
    service = UserService(db)
    return await service.get_user_public_activity(
        user_id=user_id,
        activity_type=activity_type,
        pagination=pagination,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/{user_id}/interaction-history", response_model=UserInteractionHistoryResponse)
async def get_user_interaction_history(
    user_id: UUID,
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's interaction history (requires authentication)."""
    # Only allow users to see their own interaction history or admin users
    if current_user.id != user_id and not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Access denied")
    
    service = UserService(db)
    return await service.get_user_interaction_history(
        user_id=user_id,
        interaction_type=interaction_type,
        pagination=pagination
    )


@router.get("/network/stats", response_model=SocialNetworkStatsResponse)
async def get_social_network_stats(
    timeframe: str = Query("month", description="Timeframe for stats"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social network statistics for the platform."""
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_social_network_stats(timeframe=timeframe)


@router.get("/{user_id}/influence-score", response_model=UserInfluenceScoreResponse)
async def get_user_influence_score(
    user_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's influence score and ranking."""
    service = UserService(db)
    return await service.get_user_influence_score(
        user_id=user_id,
        viewer_id=current_user.id if current_user else None
    )


@router.post("/{user_id}/follow")
async def follow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow a user."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    service = UserService(db)
    result = await service.follow_user(current_user.id, user_id)
    return {"message": "User followed successfully", "following": True}


@router.delete("/{user_id}/follow")
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
    return {"message": "User unfollowed successfully", "following": False}


@router.get("/{user_id}/relationship")
async def get_user_relationship(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get relationship status between current user and specified user."""
    service = UserService(db)
    return await service.get_user_relationship(
        user1_id=current_user.id,
        user2_id=user_id
    )


@router.get("/search")
async def search_users(
    q: str = Query(..., description="Search query"),
    filters: Optional[str] = Query(None, description="Additional filters"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for users."""
    service = UserService(db)
    return await service.search_users(
        query=q,
        filters=filters,
        pagination=pagination,
        viewer_id=current_user.id if current_user else None
    ) 