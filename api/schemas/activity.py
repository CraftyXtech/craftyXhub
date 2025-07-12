
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from .user import UserResponse
from .post import PostSummaryResponse


class ActivityFeedResponse(BaseModel):
    """General activity feed response."""
    activities: List["ActivityItemResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    feed_type: str
    last_updated: datetime

    class Config:
        from_attributes = True


class ActivityItemResponse(BaseModel):
    """Individual activity item."""
    id: UUID
    activity_type: str  # like, comment, follow, post, bookmark, view
    actor: UserResponse
    target_type: Optional[str] = None  # post, comment, user
    target_id: Optional[UUID] = None
    target_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_public: bool = True
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """User activity history response."""
    user_id: UUID
    activities: List[ActivityItemResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    activity_type_filter: Optional[str] = None
    timeframe: str = "all"
    summary: "ActivitySummaryData"

    class Config:
        from_attributes = True


class ActivitySummaryData(BaseModel):
    """Activity summary data."""
    total_activities: int = 0
    likes_given: int = 0
    comments_made: int = 0
    posts_created: int = 0
    bookmarks_made: int = 0
    follows_made: int = 0
    most_active_day: Optional[str] = None
    activity_score: float = 0.0

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """User notifications response."""
    notifications: List["NotificationItemResponse"]
    total_count: int
    unread_count: int
    page: int
    page_size: int
    has_next: bool
    notification_type_filter: Optional[str] = None
    status_filter: str = "all"

    class Config:
        from_attributes = True


class NotificationItemResponse(BaseModel):
    """Individual notification item."""
    id: UUID
    notification_type: str  # like, comment, follow, mention, system
    title: str
    message: str
    actor: Optional[UserResponse] = None
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    target_data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class SocialTimelineResponse(BaseModel):
    """Social timeline response."""
    timeline_items: List["TimelineItemResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    timeline_type: str = "all"
    last_updated: datetime

    class Config:
        from_attributes = True


class TimelineItemResponse(BaseModel):
    """Individual timeline item."""
    id: UUID
    item_type: str  # post, activity, announcement
    content: Optional[PostSummaryResponse] = None
    activity: Optional[ActivityItemResponse] = None
    created_at: datetime
    relevance_score: float = 0.0
    interaction_counts: "TimelineInteractionCounts"

    class Config:
        from_attributes = True


class TimelineInteractionCounts(BaseModel):
    """Interaction counts for timeline items."""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    bookmarks: int = 0

    class Config:
        from_attributes = True


class ActivityStatsResponse(BaseModel):
    """Activity statistics response."""
    user_id: UUID
    timeframe: str
    activity_breakdown: Dict[str, int]
    daily_activity: List["DailyActivityData"]
    engagement_received: "EngagementReceivedData"
    activity_trends: List["ActivityTrendData"]
    activity_score: float
    rank: Optional[int] = None

    class Config:
        from_attributes = True


class DailyActivityData(BaseModel):
    """Daily activity data point."""
    date: datetime
    activity_count: int
    activity_types: Dict[str, int]
    engagement_score: float

    class Config:
        from_attributes = True


class EngagementReceivedData(BaseModel):
    """Engagement received by user."""
    total_likes: int = 0
    total_comments: int = 0
    total_bookmarks: int = 0
    total_views: int = 0
    total_follows: int = 0
    engagement_rate: float = 0.0

    class Config:
        from_attributes = True


class ActivityTrendData(BaseModel):
    """Activity trend data."""
    period: str
    activity_count: int
    growth_rate: float
    trend_direction: str  # up, down, stable

    class Config:
        from_attributes = True


class ActivityFilterRequest(BaseModel):
    """Activity filter request."""
    activity_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    actors: Optional[List[UUID]] = None
    target_types: Optional[List[str]] = None
    is_public: Optional[bool] = None

    class Config:
        from_attributes = True


class NotificationSettingsResponse(BaseModel):
    """Notification settings response."""
    user_id: UUID
    email_notifications: "EmailNotificationSettings"
    push_notifications: "PushNotificationSettings"
    in_app_notifications: "InAppNotificationSettings"
    frequency_settings: "NotificationFrequencySettings"

    class Config:
        from_attributes = True


class EmailNotificationSettings(BaseModel):
    """Email notification settings."""
    enabled: bool = True
    likes: bool = True
    comments: bool = True
    follows: bool = True
    mentions: bool = True
    post_updates: bool = True
    weekly_digest: bool = True

    class Config:
        from_attributes = True


class PushNotificationSettings(BaseModel):
    """Push notification settings."""
    enabled: bool = True
    likes: bool = True
    comments: bool = True
    follows: bool = True
    mentions: bool = True
    breaking_news: bool = True

    class Config:
        from_attributes = True


class InAppNotificationSettings(BaseModel):
    """In-app notification settings."""
    enabled: bool = True
    likes: bool = True
    comments: bool = True
    follows: bool = True
    mentions: bool = True
    system_updates: bool = True

    class Config:
        from_attributes = True


class NotificationFrequencySettings(BaseModel):
    """Notification frequency settings."""
    immediate: bool = True
    hourly_digest: bool = False
    daily_digest: bool = False
    weekly_digest: bool = True
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format

    class Config:
        from_attributes = True


class NotificationMarkRequest(BaseModel):
    """Request to mark notification."""
    status: str = Field(..., description="Status: read, unread")

    class Config:
        from_attributes = True


class BulkNotificationRequest(BaseModel):
    """Bulk notification operation request."""
    notification_ids: List[UUID]
    status: str = Field(..., description="Status: read, unread")

    class Config:
        from_attributes = True


class ActivitySummaryResponse(BaseModel):
    """Activity summary response."""
    user_id: UUID
    timeframe: str
    summary: ActivitySummaryData
    highlights: List["ActivityHighlight"]
    recommendations: List["ActivityRecommendation"]
    goals_progress: Optional["GoalsProgressData"] = None

    class Config:
        from_attributes = True


class ActivityHighlight(BaseModel):
    """Activity highlight."""
    highlight_type: str
    title: str
    description: str
    value: float
    comparison: Optional[str] = None  # vs previous period
    trend: str  # up, down, stable

    class Config:
        from_attributes = True


class ActivityRecommendation(BaseModel):
    """Activity recommendation."""
    recommendation_type: str
    title: str
    description: str
    action_text: str
    action_url: Optional[str] = None
    priority: str  # high, medium, low

    class Config:
        from_attributes = True


class GoalsProgressData(BaseModel):
    """Goals progress data."""
    daily_goal: Optional[int] = None
    weekly_goal: Optional[int] = None
    monthly_goal: Optional[int] = None
    daily_progress: float = 0.0
    weekly_progress: float = 0.0
    monthly_progress: float = 0.0

    class Config:
        from_attributes = True


class PersonalizedFeedResponse(BaseModel):
    """Personalized feed response."""
    feed_items: List["FeedItemResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    feed_type: str
    personalization_score: float
    last_updated: datetime

    class Config:
        from_attributes = True


class FeedItemResponse(BaseModel):
    """Individual feed item."""
    id: UUID
    item_type: str  # post, activity, recommendation, trending
    content: Optional[PostSummaryResponse] = None
    activity: Optional[ActivityItemResponse] = None
    recommendation_data: Optional[Dict[str, Any]] = None
    relevance_score: float
    created_at: datetime
    interaction_counts: TimelineInteractionCounts
    user_interaction_status: Optional[Dict[str, bool]] = None

    class Config:
        from_attributes = True


class TrendingActivitiesResponse(BaseModel):
    """Trending activities response."""
    trending_activities: List[ActivityItemResponse]
    timeframe: str
    activity_type_filter: Optional[str] = None
    total_count: int
    last_updated: datetime

    class Config:
        from_attributes = True


class ActivityInsightsResponse(BaseModel):
    """Activity insights response."""
    user_id: UUID
    timeframe: str
    insights: List["ActivityInsight"]
    patterns: List["ActivityPattern"]
    recommendations: List[ActivityRecommendation]
    comparative_data: "ComparativeActivityData"

    class Config:
        from_attributes = True


class ActivityInsight(BaseModel):
    """Individual activity insight."""
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]
    importance: str  # high, medium, low

    class Config:
        from_attributes = True


class ActivityPattern(BaseModel):
    """Activity pattern."""
    pattern_type: str
    description: str
    frequency: str
    confidence: float
    impact: str  # positive, negative, neutral

    class Config:
        from_attributes = True


class ComparativeActivityData(BaseModel):
    """Comparative activity data."""
    vs_previous_period: Dict[str, float]
    vs_platform_average: Dict[str, float]
    percentile_rank: float

    class Config:
        from_attributes = True


class FollowingActivityResponse(BaseModel):
    """Following activity response."""
    activities: List[ActivityItemResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    activity_type_filter: Optional[str] = None
    following_count: int

    class Config:
        from_attributes = True


class RecentInteractionsResponse(BaseModel):
    """Recent interactions response."""
    interactions: List["InteractionItemResponse"]
    total_count: int
    interaction_type_filter: Optional[str] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class InteractionItemResponse(BaseModel):
    """Individual interaction item."""
    id: UUID
    interaction_type: str
    actor: UserResponse
    target_content: Optional[PostSummaryResponse] = None
    created_at: datetime
    interaction_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True 