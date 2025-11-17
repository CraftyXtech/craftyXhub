from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .user import AdminUserStatsResponse


class DashboardOverview(BaseModel):
    """
    High-level overview metrics for the dashboard.

    For admins/moderators, this can include user statistics.
    For normal users, user-related fields will typically be omitted by the frontend.
    """

    total_posts: int = Field(..., ge=0)
    published_posts: int = Field(..., ge=0)
    draft_posts: int = Field(..., ge=0)

    # Admin-only contextual fields
    total_users: Optional[int] = Field(None, ge=0)
    active_users: Optional[int] = Field(None, ge=0)
    inactive_users: Optional[int] = Field(None, ge=0)
    admin_count: Optional[int] = Field(None, ge=0)
    moderator_count: Optional[int] = Field(None, ge=0)
    user_count: Optional[int] = Field(None, ge=0)
    recent_registrations: Optional[int] = Field(None, ge=0)
    pending_reviews: Optional[int] = Field(None, ge=0)


class PostOverviewStats(BaseModel):
    total_posts: int = Field(..., ge=0)
    published_posts: int = Field(..., ge=0)
    draft_posts: int = Field(..., ge=0)
    trending_count: int = Field(..., ge=0)


class EngagementMetrics(BaseModel):
    total_views: int = Field(..., ge=0)
    total_likes: int = Field(..., ge=0)
    total_comments: int = Field(..., ge=0)
    total_bookmarks: int = Field(..., ge=0)


class DashboardPostSummary(BaseModel):
    uuid: str
    title: str
    view_count: int = Field(..., ge=0)
    like_count: int = Field(..., ge=0)
    comment_count: int = Field(..., ge=0)
    bookmark_count: int = Field(..., ge=0)
    is_published: bool
    published_at: Optional[datetime] = None


class DashboardActivityItem(BaseModel):
    """
    Represents a single item in the 'Recent Activity' timeline.
    """

    id: str
    type: str
    title: str
    description: Optional[str] = None
    created_at: datetime
    icon: Optional[str] = None
    color: Optional[str] = None


class DashboardDocumentSummary(BaseModel):
    """
    Generic summary for items shown in the 'Recent Documents' or 'Drafts' sections.
    This can represent posts, drafts, or other content types.
    """

    uuid: str
    title: str
    status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[str] = None


class AdminDashboardResponse(BaseModel):
    """
    Response envelope for the admin/moderator dashboard.
    """

    overview: DashboardOverview
    posts_overview: PostOverviewStats
    engagement_metrics: EngagementMetrics
    top_posts: List[DashboardPostSummary]
    recent_activity: List[DashboardActivityItem]
    recent_documents: List[DashboardDocumentSummary] = []


class UserDashboardResponse(BaseModel):
    """
    Response envelope for the normal user (creator) dashboard.
    """

    overview: DashboardOverview
    posts_overview: PostOverviewStats
    engagement_metrics: EngagementMetrics
    top_posts: List[DashboardPostSummary]
    recent_activity: List[DashboardActivityItem]
    drafts: List[DashboardDocumentSummary] = []
    recent_documents: List[DashboardDocumentSummary] = []


