
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, PaginationParams
from dependencies.web_auth import get_optional_current_user, get_current_user
from models.user import User
from services.analytics.analytics_service import AnalyticsService
from services.interactions.interaction_service import InteractionService
from schemas.analytics import (
    TrendingContentResponse, EngagementAnalyticsResponse, PlatformStatsResponse,
    ContentPerformanceResponse, UserEngagementMetricsResponse, PopularTagsResponse,
    TopContributorsResponse, EngagementTrendsResponse, ContentDistributionResponse,
    AudienceInsightsResponse, RealtimeStatsResponse, ViralContentResponse,
    EngagementHeatmapResponse, ContentLifecycleResponse, SocialInfluenceResponse
)

router = APIRouter(prefix="/analytics", tags=["Social Analytics"])


@router.get("/trending/posts", response_model=TrendingContentResponse)
async def get_trending_posts(
    timeframe: str = Query("week", description="Timeframe: hour, day, week, month"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, description="Number of posts", ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get trending posts based on engagement metrics."""
    if timeframe not in ["hour", "day", "week", "month"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = InteractionService(db)
    return await service.get_trending_posts(
        timeframe=timeframe,
        category=category,
        limit=limit
    )


@router.get("/trending/tags", response_model=PopularTagsResponse)
async def get_trending_tags(
    timeframe: str = Query("week", description="Timeframe for trending tags"),
    limit: int = Query(20, description="Number of tags", ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get trending tags based on usage and engagement."""
    if timeframe not in ["hour", "day", "week", "month"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_trending_tags(
        timeframe=timeframe,
        limit=limit
    )


@router.get("/engagement/overview", response_model=EngagementAnalyticsResponse)
async def get_engagement_overview(
    timeframe: str = Query("week", description="Timeframe for analysis"),
    content_type: str = Query("all", description="Content type: posts, comments, all"),
    db: AsyncSession = Depends(get_db)
):
    """Get overall engagement analytics for the platform."""
    if timeframe not in ["day", "week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if content_type not in ["posts", "comments", "all"]:
        raise HTTPException(status_code=422, detail="Invalid content type")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_engagement_overview(
        timeframe=timeframe,
        content_type=content_type
    )


@router.get("/platform/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(
    timeframe: str = Query("month", description="Timeframe for stats"),
    include_historical: bool = Query(False, description="Include historical data"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive platform statistics."""
    if timeframe not in ["day", "week", "month", "quarter", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_platform_stats(
        timeframe=timeframe,
        include_historical=include_historical,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/content/{content_id}/performance", response_model=ContentPerformanceResponse)
async def get_content_performance(
    content_id: UUID,
    content_type: str = Query("post", description="Content type: post, comment"),
    timeframe: str = Query("all", description="Timeframe for analysis"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed performance analytics for specific content."""
    if content_type not in ["post", "comment"]:
        raise HTTPException(status_code=422, detail="Invalid content type")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_content_performance(
        content_id=content_id,
        content_type=content_type,
        timeframe=timeframe,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/users/{user_id}/engagement", response_model=UserEngagementMetricsResponse)
async def get_user_engagement_metrics(
    user_id: UUID,
    timeframe: str = Query("month", description="Timeframe for metrics"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get engagement metrics for a specific user."""
    if timeframe not in ["day", "week", "month", "quarter", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_user_engagement_metrics(
        user_id=user_id,
        timeframe=timeframe,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/top-contributors", response_model=TopContributorsResponse)
async def get_top_contributors(
    timeframe: str = Query("month", description="Timeframe for analysis"),
    metric: str = Query("engagement", description="Metric: posts, likes, comments, engagement"),
    limit: int = Query(10, description="Number of contributors", ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top contributors based on various metrics."""
    if timeframe not in ["day", "week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if metric not in ["posts", "likes", "comments", "engagement", "followers"]:
        raise HTTPException(status_code=422, detail="Invalid metric")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_top_contributors(
        timeframe=timeframe,
        metric=metric,
        limit=limit
    )


@router.get("/engagement/trends", response_model=EngagementTrendsResponse)
async def get_engagement_trends(
    timeframe: str = Query("month", description="Timeframe for trends"),
    granularity: str = Query("day", description="Data granularity: hour, day, week"),
    metric: str = Query("all", description="Metric: likes, comments, views, all"),
    db: AsyncSession = Depends(get_db)
):
    """Get engagement trends over time."""
    if timeframe not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if granularity not in ["hour", "day", "week"]:
        raise HTTPException(status_code=422, detail="Invalid granularity")
    
    if metric not in ["likes", "comments", "views", "bookmarks", "all"]:
        raise HTTPException(status_code=422, detail="Invalid metric")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_engagement_trends(
        timeframe=timeframe,
        granularity=granularity,
        metric=metric
    )


@router.get("/content/distribution", response_model=ContentDistributionResponse)
async def get_content_distribution(
    timeframe: str = Query("month", description="Timeframe for analysis"),
    dimension: str = Query("category", description="Dimension: category, tag, author, status"),
    db: AsyncSession = Depends(get_db)
):
    """Get content distribution analytics."""
    if timeframe not in ["week", "month", "quarter", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if dimension not in ["category", "tag", "author", "status", "type"]:
        raise HTTPException(status_code=422, detail="Invalid dimension")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_content_distribution(
        timeframe=timeframe,
        dimension=dimension
    )


@router.get("/audience/insights", response_model=AudienceInsightsResponse)
async def get_audience_insights(
    timeframe: str = Query("month", description="Timeframe for insights"),
    segment: Optional[str] = Query(None, description="User segment filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audience insights and demographics (admin only)."""
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if timeframe not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_audience_insights(
        timeframe=timeframe,
        segment=segment
    )


@router.get("/realtime/stats", response_model=RealtimeStatsResponse)
async def get_realtime_stats(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time platform statistics."""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_realtime_stats(
        viewer_id=current_user.id if current_user else None
    )


@router.get("/viral/content", response_model=ViralContentResponse)
async def get_viral_content(
    timeframe: str = Query("week", description="Timeframe for viral content"),
    threshold: float = Query(2.0, description="Viral threshold multiplier", ge=1.0, le=10.0),
    limit: int = Query(20, description="Number of items", ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get viral content based on engagement velocity."""
    if timeframe not in ["day", "week", "month"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_viral_content(
        timeframe=timeframe,
        threshold=threshold,
        limit=limit
    )


@router.get("/engagement/heatmap", response_model=EngagementHeatmapResponse)
async def get_engagement_heatmap(
    timeframe: str = Query("week", description="Timeframe for heatmap"),
    metric: str = Query("all", description="Metric for heatmap"),
    granularity: str = Query("hour", description="Time granularity"),
    db: AsyncSession = Depends(get_db)
):
    """Get engagement heatmap data."""
    if timeframe not in ["day", "week", "month"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    if metric not in ["likes", "comments", "views", "posts", "all"]:
        raise HTTPException(status_code=422, detail="Invalid metric")
    
    if granularity not in ["hour", "day"]:
        raise HTTPException(status_code=422, detail="Invalid granularity")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_engagement_heatmap(
        timeframe=timeframe,
        metric=metric,
        granularity=granularity
    )


@router.get("/content/{content_id}/lifecycle", response_model=ContentLifecycleResponse)
async def get_content_lifecycle(
    content_id: UUID,
    content_type: str = Query("post", description="Content type"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content lifecycle analytics."""
    if content_type not in ["post", "comment"]:
        raise HTTPException(status_code=422, detail="Invalid content type")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_content_lifecycle(
        content_id=content_id,
        content_type=content_type,
        viewer_id=current_user.id if current_user else None
    )


@router.get("/social/influence", response_model=SocialInfluenceResponse)
async def get_social_influence_analytics(
    timeframe: str = Query("month", description="Timeframe for analysis"),
    include_network: bool = Query(False, description="Include network analysis"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social influence and network analytics (admin only)."""
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if timeframe not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_social_influence_analytics(
        timeframe=timeframe,
        include_network=include_network
    ) 