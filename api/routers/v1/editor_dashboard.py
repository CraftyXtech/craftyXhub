"""
Editor Dashboard API Router

Provides endpoints for the editor dashboard with analytics and insights.
Follows SubPRD-EditorDashboard.md specifications.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.editor_permissions import require_editor_or_admin
from models.user import User
from services.editor.dashboard_service import DashboardService
from schemas.editor.dashboard import (
    DashboardStatsRequest,
    DashboardStatsResponse,
    TrendingPostResponse,
    ViewTrendsResponse,
    PostDistributionResponse,
    ContentPerformanceResponse,
    UserEngagementResponse,
    CategoryPerformanceResponse,
    TagPerformanceResponse,
    RecentActivityResponse,
    ContentInsightsResponse,
    QuickStatsResponse,
    EngagementMetricsResponse,
    ContentAnalyticsResponse
)

router = APIRouter(prefix="/editor/dashboard", tags=["Editor - Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    period: str = Query("7d", description="Time period: 1d, 7d, 30d, 90d, 1y"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard statistics."""
    service = DashboardService(db)
    request = DashboardStatsRequest(period=period)
    return await service.get_dashboard_stats(request, current_user)


@router.get("/quick-stats", response_model=QuickStatsResponse)
async def get_quick_stats(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get quick statistics for dashboard overview."""
    service = DashboardService(db)
    return await service.get_quick_stats(current_user)


@router.get("/trending-posts", response_model=List[TrendingPostResponse])
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    period: str = Query("7d", description="Time period: 1d, 7d, 30d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get trending posts based on engagement metrics."""
    service = DashboardService(db)
    return await service.get_trending_posts(limit, period, current_user)


@router.get("/view-trends", response_model=ViewTrendsResponse)
async def get_view_trends(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get view trends over time."""
    service = DashboardService(db)
    return await service.get_view_trends(period, current_user)


@router.get("/post-distribution", response_model=PostDistributionResponse)
async def get_post_distribution(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get post distribution by status and category."""
    service = DashboardService(db)
    return await service.get_post_distribution(current_user)


@router.get("/content-performance", response_model=ContentPerformanceResponse)
async def get_content_performance(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    limit: int = Query(10, ge=1, le=50, description="Number of posts to analyze"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get content performance metrics."""
    service = DashboardService(db)
    return await service.get_content_performance(period, limit, current_user)


@router.get("/user-engagement", response_model=UserEngagementResponse)
async def get_user_engagement(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user engagement metrics."""
    service = DashboardService(db)
    return await service.get_user_engagement(period, current_user)


@router.get("/category-performance", response_model=List[CategoryPerformanceResponse])
async def get_category_performance(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get category performance metrics."""
    service = DashboardService(db)
    return await service.get_category_performance(period, limit, current_user)


@router.get("/tag-performance", response_model=List[TagPerformanceResponse])
async def get_tag_performance(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    limit: int = Query(10, ge=1, le=50, description="Number of tags to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get tag performance metrics."""
    service = DashboardService(db)
    return await service.get_tag_performance(period, limit, current_user)


@router.get("/recent-activity", response_model=List[RecentActivityResponse])
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100, description="Number of activities to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity feed."""
    service = DashboardService(db)
    return await service.get_recent_activity(limit, current_user)


@router.get("/content-insights", response_model=ContentInsightsResponse)
async def get_content_insights(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get content insights and recommendations."""
    service = DashboardService(db)
    return await service.get_content_insights(period, current_user)


@router.get("/engagement-metrics", response_model=EngagementMetricsResponse)
async def get_engagement_metrics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed engagement metrics."""
    service = DashboardService(db)
    return await service.get_engagement_metrics(period, current_user)


@router.get("/content-analytics", response_model=ContentAnalyticsResponse)
async def get_content_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive content analytics."""
    service = DashboardService(db)
    return await service.get_content_analytics(period, current_user)


@router.get("/my-posts/stats", response_model=dict)
async def get_my_posts_stats(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for current user's posts."""
    service = DashboardService(db)
    return await service.get_user_posts_stats(current_user.id, period, current_user)


@router.get("/pending-tasks", response_model=dict)
async def get_pending_tasks(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get pending tasks for the editor."""
    service = DashboardService(db)
    return await service.get_pending_tasks(current_user)


@router.get("/notifications/summary", response_model=dict)
async def get_notifications_summary(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get notifications summary for the dashboard."""
    service = DashboardService(db)
    return await service.get_notifications_summary(current_user) 