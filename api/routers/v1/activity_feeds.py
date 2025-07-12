
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, PaginationParams
from dependencies.web_auth import get_current_user, get_optional_current_user
from models.user import User
from services.users.user_service import UserService
from services.interactions.interaction_service import InteractionService
from schemas.activity import (
    ActivityFeedResponse, UserActivityResponse, NotificationResponse,
    SocialTimelineResponse, ActivityStatsResponse, ActivityFilterRequest,
    NotificationSettingsResponse, NotificationMarkRequest, BulkNotificationRequest,
    ActivitySummaryResponse, PersonalizedFeedResponse, TrendingActivitiesResponse,
    ActivityInsightsResponse, FollowingActivityResponse, RecentInteractionsResponse
)

router = APIRouter(prefix="/activity", tags=["Activity Feeds"])


@router.get("/feed", response_model=PersonalizedFeedResponse)
async def get_personalized_feed(
    feed_type: str = Query("all", description="Feed type: all, following, trending, personal"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized activity feed for the current user."""
    if feed_type not in ["all", "following", "trending", "personal"]:
        raise HTTPException(status_code=422, detail="Invalid feed type")
    
    service = UserService(db)
    return await service.get_personalized_feed(
        user_id=current_user.id,
        feed_type=feed_type,
        pagination=pagination
    )


@router.get("/timeline", response_model=SocialTimelineResponse)
async def get_social_timeline(
    timeline_type: str = Query("all", description="Timeline type: all, posts, interactions, follows"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social timeline showing activity from followed users."""
    if timeline_type not in ["all", "posts", "interactions", "follows"]:
        raise HTTPException(status_code=422, detail="Invalid timeline type")
    
    service = UserService(db)
    return await service.get_social_timeline(
        user_id=current_user.id,
        timeline_type=timeline_type,
        pagination=pagination
    )


@router.get("/me/history", response_model=UserActivityResponse)
async def get_my_activity_history(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    timeframe: str = Query("week", description="Timeframe: day, week, month, year, all"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's activity history."""
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = UserService(db)
    return await service.get_user_activity_history(
        user_id=current_user.id,
        activity_type=activity_type,
        timeframe=timeframe,
        pagination=pagination
    )


@router.get("/me/stats", response_model=ActivityStatsResponse)
async def get_my_activity_stats(
    timeframe: str = Query("week", description="Timeframe for stats"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's activity statistics."""
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = UserService(db)
    return await service.get_user_activity_stats(
        user_id=current_user.id,
        timeframe=timeframe
    )


@router.get("/notifications", response_model=NotificationResponse)
async def get_notifications(
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    status: str = Query("all", description="Status: all, unread, read"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications."""
    if status not in ["all", "unread", "read"]:
        raise HTTPException(status_code=422, detail="Invalid status filter")
    
    service = UserService(db)
    return await service.get_user_notifications(
        user_id=current_user.id,
        notification_type=notification_type,
        status=status,
        pagination=pagination
    )


@router.post("/notifications/{notification_id}/mark")
async def mark_notification(
    notification_id: UUID,
    request: NotificationMarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read/unread."""
    service = UserService(db)
    return await service.mark_notification(
        notification_id=notification_id,
        user_id=current_user.id,
        status=request.status
    )


@router.post("/notifications/bulk-mark")
async def bulk_mark_notifications(
    request: BulkNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk mark notifications as read/unread."""
    service = UserService(db)
    return await service.bulk_mark_notifications(
        notification_ids=request.notification_ids,
        user_id=current_user.id,
        status=request.status
    )


@router.get("/notifications/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notification settings."""
    service = UserService(db)
    return await service.get_notification_settings(user_id=current_user.id)


@router.put("/notifications/settings")
async def update_notification_settings(
    settings: NotificationSettingsResponse,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user notification settings."""
    service = UserService(db)
    return await service.update_notification_settings(
        user_id=current_user.id,
        settings=settings
    )


@router.get("/following", response_model=FollowingActivityResponse)
async def get_following_activity(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get activity from users that current user follows."""
    service = UserService(db)
    return await service.get_following_activity(
        user_id=current_user.id,
        activity_type=activity_type,
        pagination=pagination
    )


@router.get("/trending", response_model=TrendingActivitiesResponse)
async def get_trending_activities(
    timeframe: str = Query("day", description="Timeframe for trending"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    limit: int = Query(20, description="Number of activities", ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trending activities on the platform."""
    if timeframe not in ["hour", "day", "week"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = InteractionService(db)
    return await service.get_trending_activities(
        timeframe=timeframe,
        activity_type=activity_type,
        limit=limit,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/summary", response_model=ActivitySummaryResponse)
async def get_activity_summary(
    timeframe: str = Query("week", description="Timeframe for summary"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get activity summary for the current user."""
    if timeframe not in ["day", "week", "month", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = UserService(db)
    return await service.get_activity_summary(
        user_id=current_user.id,
        timeframe=timeframe
    )


@router.get("/insights", response_model=ActivityInsightsResponse)
async def get_activity_insights(
    timeframe: str = Query("month", description="Timeframe for insights"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get activity insights and recommendations."""
    if timeframe not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = UserService(db)
    return await service.get_activity_insights(
        user_id=current_user.id,
        timeframe=timeframe
    )


@router.get("/recent-interactions", response_model=RecentInteractionsResponse)
async def get_recent_interactions(
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    limit: int = Query(10, description="Number of interactions", ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent interactions with current user's content."""
    service = InteractionService(db)
    return await service.get_recent_interactions(
        user_id=current_user.id,
        interaction_type=interaction_type,
        limit=limit
    )


@router.get("/users/{user_id}/public-activity", response_model=UserActivityResponse)
async def get_user_public_activity(
    user_id: UUID,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get public activity for a specific user."""
    service = UserService(db)
    return await service.get_user_public_activity(
        user_id=user_id,
        activity_type=activity_type,
        pagination=pagination,
        viewer_id=current_user.id if current_user else None
    )


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification."""
    service = UserService(db)
    success = await service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}


@router.delete("/notifications")
async def clear_all_notifications(
    notification_type: Optional[str] = Query(None, description="Clear specific type only"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all notifications for the current user."""
    service = UserService(db)
    count = await service.clear_notifications(
        user_id=current_user.id,
        notification_type=notification_type
    )
    return {"message": f"Cleared {count} notifications"} 