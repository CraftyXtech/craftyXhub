from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from schemas.auth import UserRole
from schemas.post import PostSummaryResponse


class UserSummaryResponse(BaseModel):
    """User summary for admin dashboard."""
    id: UUID
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login_at: Optional[datetime] = None
    post_count: int = 0
    comment_count: int = 0


class UserStatsResponse(BaseModel):
    """User statistics for admin dashboard."""
    total: int
    admins: int
    editors: int
    regular_users: int
    active_users: int
    inactive_users: int
    recent_signups: List[UserSummaryResponse]


class CategoryStatsResponse(BaseModel):
    """Category statistics response."""
    id: UUID
    name: str
    slug: str
    post_count: int


class PostStatsResponse(BaseModel):
    """Post statistics response."""
    id: UUID
    title: str
    slug: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]


class AuthorResponse(BaseModel):
    """Author summary for posts."""
    id: UUID
    name: str
    email: str
    avatar: Optional[str] = None


class RecentActivityResponse(BaseModel):
    """Recent activity metrics."""
    new_posts_7_days: int
    new_comments_7_days: int
    new_users_7_days: int
    total_views_7_days: int


class ContentOverviewResponse(BaseModel):
    """Content overview statistics."""
    total_posts: int
    published_posts: int
    draft_posts: int
    scheduled_posts: int
    under_review_posts: int
    rejected_posts: int
    total_views: int
    unique_viewers: int
    total_comments: int
    approved_comments: int
    pending_comments: int
    total_likes: int
    most_viewed_posts: List[PostStatsResponse]
    most_active_users: List[UserSummaryResponse]
    posts_by_category: List[CategoryStatsResponse]
    recent_activity: RecentActivityResponse


class ViewTrendsResponse(BaseModel):
    """View trends data for charts."""
    labels: List[str]  # Date labels
    data: List[int]    # View counts
    period: str        # day/week/month/year


class ApprovalQueueResponse(BaseModel):
    """Content needing approval."""
    pending_posts: List[PostSummaryResponse]
    pending_comments: int
    rejected_posts_count: int


class FiltersResponse(BaseModel):
    """Current filters applied to dashboard."""
    search: Optional[str] = None
    role: Optional[str] = None
    sort_by: str = "published_at"
    sort_direction: str = "desc"
    period: str = "month"
    page: int = 1
    per_page: int = 9


class DashboardResponse(BaseModel):
    """Main admin dashboard response."""
    user_stats: Optional[UserStatsResponse] = None  # Admin only
    content_overview: ContentOverviewResponse
    view_trends: ViewTrendsResponse
    recent_posts: List[PostSummaryResponse]
    content_needing_approval: Optional[ApprovalQueueResponse] = None  # Admin only
    filters: FiltersResponse
    is_admin: bool
    is_editor: bool


# Request schemas for dashboard queries
class DashboardQueryParams(BaseModel):
    """Query parameters for dashboard endpoint."""
    search: Optional[str] = None
    role: Optional[str] = None
    sort_by: str = Field(default="published_at")
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$")
    period: str = Field(default="month", pattern="^(day|week|month|year)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=9, ge=1, le=50)


class GrowthMetricsResponse(BaseModel):
    """Growth metrics for user statistics."""
    daily_growth: float
    weekly_growth: float
    monthly_growth: float
    yearly_growth: float 