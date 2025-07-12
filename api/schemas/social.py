
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from .user import UserResponse


class UserSocialProfileResponse(BaseModel):
    """Comprehensive social profile for a user."""
    user: UserResponse
    social_stats: "UserSocialStatsResponse"
    relationship_status: Optional["UserRelationshipResponse"] = None
    is_following: bool = False
    is_followed_by: bool = False
    mutual_connections_count: int = 0
    can_follow: bool = True
    privacy_settings: "UserPrivacyResponse"
    activity_summary: "UserActivitySummaryResponse"

    class Config:
        from_attributes = True


class UserSocialStatsResponse(BaseModel):
    """Social statistics for a user."""
    user_id: UUID
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    comments_count: int = 0
    likes_received: int = 0
    likes_given: int = 0
    bookmarks_count: int = 0
    views_received: int = 0
    engagement_rate: float = 0.0
    influence_score: float = 0.0
    timeframe: str = "all"
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserFollowersResponse(BaseModel):
    """Response for user followers list."""
    followers: List["FollowerResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    search_query: Optional[str] = None

    class Config:
        from_attributes = True


class FollowerResponse(BaseModel):
    """Individual follower information."""
    user: UserResponse
    followed_at: datetime
    is_mutual: bool = False
    relationship_status: Optional[str] = None

    class Config:
        from_attributes = True


class UserFollowingResponse(BaseModel):
    """Response for users that this user follows."""
    following: List["FollowingResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    search_query: Optional[str] = None

    class Config:
        from_attributes = True


class FollowingResponse(BaseModel):
    """Individual following information."""
    user: UserResponse
    followed_at: datetime
    is_mutual: bool = False
    relationship_status: Optional[str] = None

    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """User activity history response."""
    activities: List["ActivityItemResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    activity_type_filter: Optional[str] = None
    timeframe: str = "all"

    class Config:
        from_attributes = True


class ActivityItemResponse(BaseModel):
    """Individual activity item."""
    id: UUID
    activity_type: str  # like, comment, follow, post, bookmark
    user: UserResponse
    target_type: Optional[str] = None  # post, comment, user
    target_id: Optional[UUID] = None
    target_title: Optional[str] = None
    activity_data: Dict[str, Any] = {}
    created_at: datetime
    is_public: bool = True

    class Config:
        from_attributes = True


class UserConnectionsResponse(BaseModel):
    """User's social connections."""
    connections: List["ConnectionResponse"]
    total_count: int
    connection_type: str  # followers, following, mutual, all
    page: int
    page_size: int
    has_next: bool

    class Config:
        from_attributes = True


class ConnectionResponse(BaseModel):
    """Individual connection information."""
    user: UserResponse
    connection_type: str  # follower, following, mutual
    connected_at: datetime
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None

    class Config:
        from_attributes = True


class MutualConnectionsResponse(BaseModel):
    """Mutual connections between two users."""
    mutual_connections: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool

    class Config:
        from_attributes = True


class SuggestedUsersResponse(BaseModel):
    """Suggested users to follow."""
    suggestions: List["UserSuggestionResponse"]
    total_count: int
    suggestion_reasons: List[str]

    class Config:
        from_attributes = True


class UserSuggestionResponse(BaseModel):
    """Individual user suggestion."""
    user: UserResponse
    suggestion_reason: str
    mutual_connections_count: int = 0
    common_interests: List[str] = []
    similarity_score: float = 0.0

    class Config:
        from_attributes = True


class UserInteractionHistoryResponse(BaseModel):
    """User's interaction history."""
    interactions: List["InteractionHistoryItemResponse"]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    interaction_type_filter: Optional[str] = None

    class Config:
        from_attributes = True


class InteractionHistoryItemResponse(BaseModel):
    """Individual interaction history item."""
    id: UUID
    interaction_type: str
    target_type: str
    target_id: UUID
    target_title: Optional[str] = None
    target_author: Optional[UserResponse] = None
    created_at: datetime
    interaction_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class SocialNetworkStatsResponse(BaseModel):
    """Social network statistics for the platform."""
    total_users: int
    active_users: int
    total_connections: int
    new_connections: int
    average_connections_per_user: float
    most_connected_users: List[UserResponse]
    network_growth_rate: float
    engagement_metrics: Dict[str, Any]
    timeframe: str

    class Config:
        from_attributes = True


class UserInfluenceScoreResponse(BaseModel):
    """User's influence score and ranking."""
    user_id: UUID
    influence_score: float
    rank: int
    percentile: float
    score_breakdown: Dict[str, float]
    factors: List[str]
    last_calculated: datetime

    class Config:
        from_attributes = True


class UserRelationshipResponse(BaseModel):
    """Relationship status between two users."""
    user1_id: UUID
    user2_id: UUID
    is_following: bool = False
    is_followed_by: bool = False
    is_mutual: bool = False
    can_follow: bool = True
    blocked_by_user1: bool = False
    blocked_by_user2: bool = False
    relationship_type: Optional[str] = None

    class Config:
        from_attributes = True


class UserPrivacyResponse(BaseModel):
    """User privacy settings."""
    profile_visibility: str = "public"  # public, followers, private
    show_followers: bool = True
    show_following: bool = True
    show_activity: bool = True
    allow_follow_requests: bool = True

    class Config:
        from_attributes = True


class UserActivitySummaryResponse(BaseModel):
    """Summary of user's recent activity."""
    recent_posts_count: int = 0
    recent_comments_count: int = 0
    recent_likes_count: int = 0
    recent_follows_count: int = 0
    last_active: Optional[datetime] = None
    activity_score: float = 0.0

    class Config:
        from_attributes = True 