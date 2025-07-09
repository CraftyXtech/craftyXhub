"""
Web profile schemas for public-facing API endpoints.

Contains Pydantic models for user profile management, preferences,
and activity tracking in the public web interface.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from schemas.user import UserSummaryResponse
from .posts import PostSummaryResponse, PaginationResponse, CategorySummaryResponse


class UserDetailResponse(BaseModel):
    """Detailed user information for profile view."""
    
    id: UUID
    name: str
    email: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    joined_at: datetime
    role: str
    is_verified: bool = False
    social_links: Dict[str, str] = {}
    location: Optional[str] = None
    website: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserActivityStatsResponse(BaseModel):
    """User activity statistics for profile dashboard."""
    
    posts_count: int = 0
    likes_count: int = 0
    bookmarks_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    reading_streak: int = 0
    total_reading_time: int = 0  # in minutes
    favorite_categories: List[Dict[str, Any]] = []
    engagement_level: str = "low"  # low, medium, high
    last_activity: Optional[datetime] = None
    member_since_days: int = 0
    
    class Config:
        from_attributes = True


class PostWithInteractionResponse(BaseModel):
    """Post with interaction metadata for user collections."""
    
    post: PostSummaryResponse
    interaction_date: datetime
    interaction_type: str  # 'like', 'bookmark'
    reading_status: Optional[str] = None  # 'unread', 'reading', 'completed'
    notes: Optional[str] = None
    tags_added: List[str] = []  # User-added tags for organization
    
    class Config:
        from_attributes = True


class PaginatedPostsResponse(BaseModel):
    """Paginated posts response for user collections."""
    
    posts: List[PostWithInteractionResponse]
    pagination: PaginationResponse
    total_count: int
    filters: Dict[str, Any] = {}
    sort_options: List[Dict[str, str]] = []
    
    class Config:
        from_attributes = True


class UserPreferencesRequest(BaseModel):
    """Request schema for updating user preferences."""
    
    newsletter_enabled: Optional[bool] = None
    personalization_enabled: Optional[bool] = None
    preferred_categories: Optional[List[str]] = Field(None, max_items=10)
    content_recommendations: Optional[bool] = None
    email_notifications: Optional[bool] = None
    reading_reminders: Optional[bool] = None
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    privacy_settings: Optional[Dict[str, bool]] = None
    
    @validator('preferred_categories')
    def validate_categories(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError('Duplicate categories not allowed')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v and v not in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']:
            raise ValueError('Unsupported language')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "newsletter_enabled": True,
                "personalization_enabled": True,
                "preferred_categories": ["technology", "programming"],
                "content_recommendations": True,
                "email_notifications": False,
                "reading_reminders": True,
                "dark_mode": False,
                "language": "en",
                "timezone": "UTC"
            }
        }


class UserPreferencesResponse(BaseModel):
    """Response schema for user preferences."""
    
    newsletter_enabled: bool = True
    personalization_enabled: bool = True
    preferred_categories: List[CategorySummaryResponse] = []
    content_recommendations: bool = True
    email_notifications: bool = True
    reading_reminders: bool = False
    dark_mode: bool = False
    language: str = "en"
    timezone: str = "UTC"
    privacy_settings: Dict[str, bool] = {}
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    """Individual user activity item."""
    
    id: UUID
    activity_type: str  # 'like', 'bookmark', 'comment', 'view', 'post_created'
    post: PostSummaryResponse
    created_at: datetime
    metadata: Dict[str, Any] = {}  # Additional activity-specific data
    is_public: bool = True
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Complete user profile response."""
    
    user: UserDetailResponse
    statistics: UserActivityStatsResponse
    liked_posts: PaginatedPostsResponse
    bookmarked_posts: PaginatedPostsResponse
    preferences: UserPreferencesResponse
    recent_activity: List[UserActivityResponse]
    achievements: List[Dict[str, Any]] = []
    reading_goals: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    social_links: Optional[Dict[str, str]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else None
    
    @validator('website')
    def validate_website(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Website must be a valid URL')
        return v
    
    @validator('social_links')
    def validate_social_links(cls, v):
        if v:
            allowed_platforms = ['twitter', 'linkedin', 'github', 'instagram', 'facebook']
            for platform in v.keys():
                if platform not in allowed_platforms:
                    raise ValueError(f'Unsupported social platform: {platform}')
        return v


class UserReadingGoalsRequest(BaseModel):
    """Request schema for setting reading goals."""
    
    daily_reading_time: Optional[int] = Field(None, ge=1, le=480)  # minutes
    weekly_posts_target: Optional[int] = Field(None, ge=1, le=100)
    monthly_categories: Optional[List[str]] = Field(None, max_items=5)
    yearly_reading_streak: Optional[int] = Field(None, ge=1, le=365)
    
    @validator('daily_reading_time')
    def validate_reading_time(cls, v):
        if v and v < 5:
            raise ValueError('Daily reading time must be at least 5 minutes')
        return v


class UserReadingGoalsResponse(BaseModel):
    """Response schema for user reading goals."""
    
    daily_reading_time: int = 0
    weekly_posts_target: int = 0
    monthly_categories: List[str] = []
    yearly_reading_streak: int = 0
    current_progress: Dict[str, Any] = {}
    achievements: List[Dict[str, Any]] = []
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserCollectionRequest(BaseModel):
    """Request schema for managing user collections."""
    
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_public: bool = True
    tags: List[str] = Field(default=[], max_items=10)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Collection name cannot be empty')
        return v.strip()


class UserCollectionResponse(BaseModel):
    """Response schema for user collections."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    is_public: bool = True
    tags: List[str] = []
    posts_count: int = 0
    created_at: datetime
    updated_at: datetime
    posts: List[PostWithInteractionResponse] = []
    
    class Config:
        from_attributes = True


class UserNotificationSettingsRequest(BaseModel):
    """Request schema for notification settings."""
    
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    comment_replies: Optional[bool] = None
    post_likes: Optional[bool] = None
    new_followers: Optional[bool] = None
    trending_posts: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email_notifications": True,
                "push_notifications": False,
                "weekly_digest": True,
                "comment_replies": True,
                "post_likes": False,
                "new_followers": True,
                "trending_posts": False
            }
        }


class UserNotificationSettingsResponse(BaseModel):
    """Response schema for notification settings."""
    
    email_notifications: bool = True
    push_notifications: bool = False
    weekly_digest: bool = True
    comment_replies: bool = True
    post_likes: bool = False
    new_followers: bool = True
    trending_posts: bool = False
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserPrivacySettingsRequest(BaseModel):
    """Request schema for privacy settings."""
    
    profile_visibility: Optional[str] = None  # public, private, friends
    activity_visibility: Optional[str] = None  # public, private, friends
    email_visibility: Optional[bool] = None
    show_reading_activity: Optional[bool] = None
    allow_friend_requests: Optional[bool] = None
    
    @validator('profile_visibility', 'activity_visibility')
    def validate_visibility(cls, v):
        if v and v not in ['public', 'private', 'friends']:
            raise ValueError('Visibility must be public, private, or friends')
        return v


class UserPrivacySettingsResponse(BaseModel):
    """Response schema for privacy settings."""
    
    profile_visibility: str = "public"
    activity_visibility: str = "public"
    email_visibility: bool = False
    show_reading_activity: bool = True
    allow_friend_requests: bool = True
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Request schema for updating user profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    social_links: Optional[Dict[str, str]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else None
    
    @validator('website')
    def validate_website(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Website must be a valid URL')
        return v
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """Response schema for user statistics."""
    
    timeframe: str
    posts_created: int = 0
    posts_published: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_bookmarks: int = 0
    engagement_rate: float = 0.0
    growth_metrics: Dict[str, float] = {}
    top_performing_posts: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class UserFollowingResponse(BaseModel):
    """Response schema for user following data."""
    
    followers_count: int = 0
    following_count: int = 0
    mutual_followers: List[UserSummaryResponse] = []
    recent_followers: List[UserSummaryResponse] = []
    following_list: List[UserSummaryResponse] = []
    
    class Config:
        from_attributes = True


class UserSocialStatsResponse(BaseModel):
    """Response schema for user social statistics."""
    
    total_interactions: int = 0
    posts_shared: int = 0
    comments_received: int = 0
    mentions_count: int = 0
    social_score: float = 0.0
    community_rank: Optional[int] = None
    
    class Config:
        from_attributes = True


class ActivityFeedResponse(BaseModel):
    """Response schema for user activity feed."""
    
    activities: List[UserActivityResponse]
    total_count: int
    pagination: PaginationResponse
    activity_types: List[str] = []
    
    class Config:
        from_attributes = True


class NotificationPreferencesRequest(BaseModel):
    """Request schema for notification preferences."""
    
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    comment_replies: Optional[bool] = None
    post_likes: Optional[bool] = None
    new_followers: Optional[bool] = None
    
    class Config:
        from_attributes = True


class NotificationPreferencesResponse(BaseModel):
    """Response schema for notification preferences."""
    
    email_notifications: bool = True
    push_notifications: bool = False
    weekly_digest: bool = True
    comment_replies: bool = True
    post_likes: bool = False
    new_followers: bool = True
    last_updated: datetime
    
    class Config:
        from_attributes = True


class ProfileVisibilityRequest(BaseModel):
    """Request schema for profile visibility settings."""
    
    profile_visibility: Optional[str] = None  # public, private, friends
    activity_visibility: Optional[str] = None  # public, private, friends
    email_visibility: Optional[bool] = None
    show_reading_activity: Optional[bool] = None
    
    @validator('profile_visibility', 'activity_visibility')
    def validate_visibility(cls, v):
        if v and v not in ['public', 'private', 'friends']:
            raise ValueError('Visibility must be public, private, or friends')
        return v
    
    class Config:
        from_attributes = True


class ProfileVisibilityResponse(BaseModel):
    """Response schema for profile visibility settings."""
    
    profile_visibility: str = "public"
    activity_visibility: str = "public"
    email_visibility: bool = False
    show_reading_activity: bool = True
    last_updated: datetime
    
    class Config:
        from_attributes = True 