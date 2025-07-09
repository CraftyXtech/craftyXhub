"""Dashboard schemas for editor module."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

from schemas.post import AuthorResponse
from schemas.post import CategoryResponse
from .posts import PostSummaryResponse


class DashboardStatsRequest(BaseModel):
    """Request schema for dashboard statistics."""
    period: str = Field(default="month", pattern="^(day|week|month|year)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=50)


class DashboardSummaryResponse(BaseModel):
    """Response schema for dashboard summary."""
    total_views: int
    recent_views: int
    published_posts: int
    draft_posts: int
    scheduled_posts: int
    pending_review_posts: int
    total_likes: int
    total_comments: int
    view_growth_percentage: float
    engagement_rate: float


class TrendingPostResponse(BaseModel):
    """Response schema for trending posts."""
    id: UUID
    title: str
    slug: str
    view_count: int
    view_growth: int
    likes_count: int
    comments_count: int
    published_at: datetime
    engagement_score: float

    class Config:
        from_attributes = True


class ViewTrendsResponse(BaseModel):
    """Response schema for view trends."""
    labels: List[str]  # Date labels
    data: List[int]    # View counts per date
    period: str
    total_views: int
    growth_percentage: float


class PostDistributionResponse(BaseModel):
    """Response schema for post distribution."""
    published: int
    draft: int
    under_review: int
    scheduled: int
    rejected: int


class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics."""
    summary: DashboardSummaryResponse
    trending_posts: List[TrendingPostResponse]
    view_trends: ViewTrendsResponse
    post_distribution: PostDistributionResponse
    recent_posts: List[PostSummaryResponse]


class ViewMetricsResponse(BaseModel):
    """Response schema for view metrics."""
    total_views: int
    unique_views: int
    views_today: int
    views_this_week: int
    average_session_duration: int


class EngagementMetricsResponse(BaseModel):
    """Response schema for engagement metrics."""
    total_likes: int
    total_comments: int
    total_shares: int
    engagement_rate: float
    average_reading_time: int


class PostAnalyticsResponse(BaseModel):
    """Response schema for post analytics."""
    post: PostSummaryResponse
    views: ViewMetricsResponse
    engagement: EngagementMetricsResponse
    performance_score: float


class PerformanceSummaryResponse(BaseModel):
    """Response schema for performance summary."""
    total_posts: int
    average_views_per_post: float
    average_engagement_rate: float
    top_performing_category: Optional[CategoryResponse]
    best_performing_day: str
    total_reading_time: int


class CategoryPerformanceResponse(BaseModel):
    """Response schema for category performance."""
    category: CategoryResponse
    post_count: int
    total_views: int
    average_engagement: float
    performance_score: float


class EngagementTrendsResponse(BaseModel):
    """Response schema for engagement trends."""
    labels: List[str]  # Date labels
    likes_data: List[int]
    comments_data: List[int]
    shares_data: List[int]
    period: str
    total_engagement: int
    growth_percentage: float


class EditorAnalyticsResponse(BaseModel):
    """Response schema for editor analytics."""
    posts_analytics: List[PostAnalyticsResponse]
    performance_summary: PerformanceSummaryResponse
    top_categories: List[CategoryPerformanceResponse]
    engagement_trends: EngagementTrendsResponse


class AnalyticsExportRequest(BaseModel):
    """Request schema for analytics export."""
    start_date: datetime
    end_date: datetime
    format: str = Field(default="csv", pattern="^(csv|json|pdf)$")
    include_posts: bool = Field(default=True)
    include_engagement: bool = Field(default=True)
    include_views: bool = Field(default=True)


class ContentPerformanceResponse(BaseModel):
    """Response schema for content performance."""
    total_posts: int
    published_posts: int
    draft_posts: int
    scheduled_posts: int
    pending_review_posts: int
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    average_views_per_post: float
    average_engagement_rate: float
    top_performing_posts: List[PostSummaryResponse]
    recent_posts: List[PostSummaryResponse]
    performance_trends: ViewTrendsResponse
    category_performance: List[CategoryPerformanceResponse]

    class Config:
        from_attributes = True


class UserEngagementResponse(BaseModel):
    """Response schema for user engagement."""
    total_users: int
    active_users: int
    new_users: int
    returning_users: int
    average_session_duration: float
    bounce_rate: float
    engagement_rate: float
    top_engaging_content: List[PostSummaryResponse]

    class Config:
        from_attributes = True


class TagPerformanceResponse(BaseModel):
    """Response schema for tag performance."""
    tag_name: str
    tag_slug: str
    post_count: int
    total_views: int
    total_likes: int
    total_comments: int
    average_engagement: float
    performance_score: float

    class Config:
        from_attributes = True


class RecentActivityResponse(BaseModel):
    """Response schema for recent activity."""
    activity_type: str
    title: str
    description: str
    timestamp: datetime
    user: Optional[AuthorResponse] = None
    post_id: Optional[UUID] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class ContentInsightsResponse(BaseModel):
    """Response schema for content insights."""
    recommended_topics: List[str]
    trending_keywords: List[str]
    optimal_posting_times: List[str]
    content_gaps: List[str]
    performance_recommendations: List[str]
    seasonal_trends: List[str]

    class Config:
        from_attributes = True


class QuickStatsResponse(BaseModel):
    """Response schema for quick stats."""
    total_posts: int
    published_posts: int
    draft_posts: int
    total_views: int
    total_likes: int
    total_comments: int
    pending_reviews: int
    recent_activity_count: int

    class Config:
        from_attributes = True


class ContentAnalyticsResponse(BaseModel):
    """Response schema for content analytics."""
    overview: DashboardSummaryResponse
    performance_metrics: ContentPerformanceResponse
    engagement_metrics: EngagementMetricsResponse
    user_engagement: UserEngagementResponse
    content_insights: ContentInsightsResponse
    trending_content: List[TrendingPostResponse]

    class Config:
        from_attributes = True 