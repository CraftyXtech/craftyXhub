
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from .user import UserResponse
from .post import PostSummaryResponse


class TrendingContentResponse(BaseModel):
    """Response for trending content."""
    trending_posts: List["TrendingPostResponse"]
    timeframe: str
    category_filter: Optional[str] = None
    total_count: int
    last_updated: datetime

    class Config:
        from_attributes = True


class TrendingPostResponse(BaseModel):
    """Individual trending post information."""
    post: PostSummaryResponse
    engagement_score: float
    trend_velocity: float
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    bookmarks_count: int = 0
    shares_count: int = 0
    viral_coefficient: float = 0.0
    rank: int
    rank_change: int = 0

    class Config:
        from_attributes = True


class EngagementAnalyticsResponse(BaseModel):
    """Overall engagement analytics."""
    total_engagement: int
    engagement_by_type: Dict[str, int]
    engagement_trends: List["EngagementDataPoint"]
    top_performing_content: List["ContentPerformanceResponse"]
    average_engagement_rate: float
    engagement_growth_rate: float
    timeframe: str
    content_type_filter: str

    class Config:
        from_attributes = True


class EngagementDataPoint(BaseModel):
    """Single engagement data point for trends."""
    timestamp: datetime
    likes: int = 0
    comments: int = 0
    views: int = 0
    bookmarks: int = 0
    shares: int = 0
    total_engagement: int = 0

    class Config:
        from_attributes = True


class PlatformStatsResponse(BaseModel):
    """Comprehensive platform statistics."""
    user_stats: "UserStatsData"
    content_stats: "ContentStatsData"
    engagement_stats: "EngagementStatsData"
    growth_metrics: "GrowthMetricsData"
    timeframe: str
    historical_data: Optional[List["HistoricalDataPoint"]] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class UserStatsData(BaseModel):
    """User-related statistics."""
    total_users: int
    active_users: int
    new_users: int
    verified_users: int
    user_growth_rate: float
    retention_rate: float
    average_session_duration: float

    class Config:
        from_attributes = True


class ContentStatsData(BaseModel):
    """Content-related statistics."""
    total_posts: int
    published_posts: int
    new_posts: int
    total_comments: int
    new_comments: int
    content_growth_rate: float
    average_posts_per_user: float

    class Config:
        from_attributes = True


class EngagementStatsData(BaseModel):
    """Engagement-related statistics."""
    total_likes: int
    total_comments: int
    total_views: int
    total_bookmarks: int
    total_shares: int
    average_engagement_per_post: float
    engagement_rate: float

    class Config:
        from_attributes = True


class GrowthMetricsData(BaseModel):
    """Growth metrics data."""
    user_growth: float
    content_growth: float
    engagement_growth: float
    revenue_growth: Optional[float] = None
    retention_improvement: float

    class Config:
        from_attributes = True


class HistoricalDataPoint(BaseModel):
    """Historical data point."""
    date: datetime
    users: int
    posts: int
    engagement: int
    growth_rate: float

    class Config:
        from_attributes = True


class ContentPerformanceResponse(BaseModel):
    """Detailed content performance analytics."""
    content_id: UUID
    content_type: str
    title: str
    author: UserResponse
    published_at: datetime
    performance_metrics: "PerformanceMetricsData"
    engagement_timeline: List[EngagementDataPoint]
    audience_insights: "AudienceInsightsData"
    viral_metrics: "ViralMetricsData"
    timeframe: str

    class Config:
        from_attributes = True


class PerformanceMetricsData(BaseModel):
    """Performance metrics for content."""
    views: int = 0
    unique_views: int = 0
    likes: int = 0
    comments: int = 0
    bookmarks: int = 0
    shares: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    bounce_rate: float = 0.0
    read_completion_rate: float = 0.0

    class Config:
        from_attributes = True


class AudienceInsightsData(BaseModel):
    """Audience insights for content."""
    demographics: Dict[str, Any] = {}
    geographic_distribution: Dict[str, int] = {}
    device_breakdown: Dict[str, int] = {}
    referral_sources: Dict[str, int] = {}
    audience_overlap: float = 0.0

    class Config:
        from_attributes = True


class ViralMetricsData(BaseModel):
    """Viral metrics for content."""
    viral_coefficient: float = 0.0
    share_rate: float = 0.0
    amplification_factor: float = 0.0
    reach_multiplier: float = 0.0
    virality_score: float = 0.0

    class Config:
        from_attributes = True


class UserEngagementMetricsResponse(BaseModel):
    """User engagement metrics."""
    user_id: UUID
    engagement_summary: "UserEngagementSummary"
    content_performance: List[ContentPerformanceResponse]
    audience_growth: List["AudienceGrowthPoint"]
    engagement_trends: List[EngagementDataPoint]
    top_performing_posts: List[TrendingPostResponse]
    timeframe: str

    class Config:
        from_attributes = True


class UserEngagementSummary(BaseModel):
    """Summary of user engagement."""
    total_posts: int = 0
    total_likes_received: int = 0
    total_comments_received: int = 0
    total_views_received: int = 0
    total_bookmarks_received: int = 0
    average_engagement_per_post: float = 0.0
    engagement_rate: float = 0.0
    follower_growth_rate: float = 0.0

    class Config:
        from_attributes = True


class AudienceGrowthPoint(BaseModel):
    """Audience growth data point."""
    date: datetime
    followers: int
    following: int
    net_growth: int
    growth_rate: float

    class Config:
        from_attributes = True


class PopularTagsResponse(BaseModel):
    """Popular/trending tags response."""
    tags: List["TagTrendData"]
    timeframe: str
    total_tags: int
    last_updated: datetime

    class Config:
        from_attributes = True


class TagTrendData(BaseModel):
    """Individual tag trend data."""
    tag_name: str
    usage_count: int
    engagement_score: float
    trend_direction: str  # up, down, stable
    growth_rate: float
    rank: int
    rank_change: int

    class Config:
        from_attributes = True


class TopContributorsResponse(BaseModel):
    """Top contributors response."""
    contributors: List["ContributorData"]
    metric: str
    timeframe: str
    last_updated: datetime

    class Config:
        from_attributes = True


class ContributorData(BaseModel):
    """Individual contributor data."""
    user: UserResponse
    metric_value: float
    rank: int
    rank_change: int
    contribution_percentage: float
    activity_summary: Dict[str, Any]

    class Config:
        from_attributes = True


class EngagementTrendsResponse(BaseModel):
    """Engagement trends over time."""
    trends: List[EngagementDataPoint]
    summary_stats: "TrendSummaryStats"
    timeframe: str
    granularity: str
    metric_filter: str

    class Config:
        from_attributes = True


class TrendSummaryStats(BaseModel):
    """Summary statistics for trends."""
    average_growth_rate: float
    peak_engagement: int
    peak_date: datetime
    lowest_engagement: int
    lowest_date: datetime
    volatility_index: float

    class Config:
        from_attributes = True


class ContentDistributionResponse(BaseModel):
    """Content distribution analytics."""
    distribution: List["DistributionData"]
    total_content: int
    dimension: str
    timeframe: str

    class Config:
        from_attributes = True


class DistributionData(BaseModel):
    """Individual distribution data point."""
    category: str
    count: int
    percentage: float
    engagement_score: float
    growth_rate: float

    class Config:
        from_attributes = True


class AudienceInsightsResponse(BaseModel):
    """Audience insights response."""
    demographics: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    engagement_preferences: Dict[str, Any]
    growth_segments: List["AudienceSegment"]
    retention_metrics: Dict[str, float]
    timeframe: str

    class Config:
        from_attributes = True


class AudienceSegment(BaseModel):
    """Audience segment data."""
    segment_name: str
    user_count: int
    engagement_rate: float
    growth_rate: float
    characteristics: Dict[str, Any]

    class Config:
        from_attributes = True


class RealtimeStatsResponse(BaseModel):
    """Real-time platform statistics."""
    active_users: int
    posts_last_hour: int
    comments_last_hour: int
    likes_last_hour: int
    current_trending: List[str]
    server_metrics: Dict[str, Any]
    last_updated: datetime

    class Config:
        from_attributes = True


class ViralContentResponse(BaseModel):
    """Viral content response."""
    viral_content: List["ViralContentItem"]
    threshold: float
    timeframe: str
    total_viral_items: int

    class Config:
        from_attributes = True


class ViralContentItem(BaseModel):
    """Individual viral content item."""
    content: PostSummaryResponse
    viral_score: float
    velocity: float
    reach: int
    amplification: float
    viral_factors: List[str]

    class Config:
        from_attributes = True


class EngagementHeatmapResponse(BaseModel):
    """Engagement heatmap data."""
    heatmap_data: List["HeatmapDataPoint"]
    timeframe: str
    granularity: str
    metric: str
    peak_times: List[str]

    class Config:
        from_attributes = True


class HeatmapDataPoint(BaseModel):
    """Individual heatmap data point."""
    time_slot: str
    value: float
    normalized_value: float  # 0-1 scale
    day_of_week: Optional[str] = None

    class Config:
        from_attributes = True


class ContentLifecycleResponse(BaseModel):
    """Content lifecycle analytics."""
    content_id: UUID
    lifecycle_stages: List["LifecycleStage"]
    performance_summary: PerformanceMetricsData
    predicted_trajectory: List["PredictionPoint"]

    class Config:
        from_attributes = True


class LifecycleStage(BaseModel):
    """Content lifecycle stage."""
    stage: str  # creation, growth, peak, decline, revival
    start_date: datetime
    end_date: Optional[datetime] = None
    engagement_level: str  # low, medium, high
    key_metrics: Dict[str, float]

    class Config:
        from_attributes = True


class PredictionPoint(BaseModel):
    """Prediction data point."""
    date: datetime
    predicted_engagement: float
    confidence_interval: List[float]

    class Config:
        from_attributes = True


class SocialInfluenceResponse(BaseModel):
    """Social influence analytics."""
    influence_network: Dict[str, Any]
    top_influencers: List[ContributorData]
    influence_trends: List["InfluenceDataPoint"]
    network_metrics: Dict[str, float]
    timeframe: str

    class Config:
        from_attributes = True


class InfluenceDataPoint(BaseModel):
    """Influence data point."""
    date: datetime
    influence_score: float
    reach: int
    engagement_multiplier: float

    class Config:
        from_attributes = True 