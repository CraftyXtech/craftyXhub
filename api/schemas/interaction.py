

from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

from .post import PaginationMeta


class InteractionType(str, Enum):
    LIKE = "like"
    BOOKMARK = "bookmark"
    FOLLOW = "follow"
    VIEW = "view"
    SHARE = "share"


class BookmarkCollection(str, Enum):
    DEFAULT = "default"
    FAVORITES = "favorites"
    READ_LATER = "read_later"
    TUTORIALS = "tutorials"
    INSPIRATION = "inspiration"


class LikeToggleResponse(BaseModel):
    """Response for like toggle operations"""
    liked: bool
    like_count: int
    message: str
    post_id: UUID

    class Config:
        from_attributes = True


class BookmarkToggleRequest(BaseModel):
    """Request for bookmark toggle operations"""
    collection_name: str = Field(default="default", max_length=50, description="Bookmark collection name")

    @validator('collection_name')
    def validate_collection_name(cls, v):
        v = v.strip().lower()
        if not v:
            return "default"
        return v

    class Config:
        from_attributes = True


class BookmarkToggleResponse(BaseModel):
    """Response for bookmark toggle operations"""
    bookmarked: bool
    message: str
    collection: str
    post_id: UUID

    class Config:
        from_attributes = True


class FollowToggleResponse(BaseModel):
    """Response for follow toggle operations"""
    following: bool
    follower_count: int
    following_count: int
    message: str
    user_id: UUID

    class Config:
        from_attributes = True


class PostInteractionsResponse(BaseModel):
    """Response for post interaction status"""
    post_id: UUID
    is_liked: bool = False
    is_bookmarked: bool = False
    like_count: int = 0
    bookmark_count: int = 0
    view_count: int = 0
    comment_count: int = 0
    share_count: int = 0

    class Config:
        from_attributes = True


class BatchInteractionsRequest(BaseModel):
    """Request for batch interaction status"""
    post_ids: List[UUID] = Field(max_items=50, description="List of post IDs to check")

    class Config:
        from_attributes = True


class BatchInteractionsResponse(BaseModel):
    """Response for batch interaction status"""
    interactions: Dict[str, PostInteractionsResponse]  # UUID as string key
    total_posts: int
    processed_posts: int

    class Config:
        from_attributes = True


class InteractionHistoryQuery(BaseModel):
    """Query parameters for interaction history"""
    interaction_type: Optional[InteractionType] = Field(None, description="Filter by interaction type")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=20, ge=1, le=100, description="Number of interactions per page")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")

    class Config:
        from_attributes = True


class InteractionHistoryResponse(BaseModel):
    """Response for interaction history"""
    id: UUID
    type: InteractionType
    target_type: str  # 'post', 'user', 'comment'
    target_id: UUID
    target_title: Optional[str] = None
    target_author: Optional[str] = None
    created_at: datetime
    metadata: Optional[Dict] = None

    class Config:
        from_attributes = True


class InteractionHistoryListResponse(BaseModel):
    """Paginated interaction history response"""
    interactions: List[InteractionHistoryResponse]
    pagination: PaginationMeta
    stats: Dict[str, int]  # Interaction type counts

    class Config:
        from_attributes = True


class BookmarkCollectionRequest(BaseModel):
    """Request for creating/updating bookmark collections"""
    name: str = Field(min_length=1, max_length=50, description="Collection name")
    description: Optional[str] = Field(None, max_length=200, description="Collection description")
    is_public: bool = Field(default=False, description="Whether collection is public")

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Collection name cannot be empty')
        return v

    class Config:
        from_attributes = True


class BookmarkCollectionResponse(BaseModel):
    """Response for bookmark collections"""
    id: UUID
    name: str
    description: Optional[str] = None
    is_public: bool = False
    post_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookmarkListQuery(BaseModel):
    """Query parameters for bookmark listing"""
    collection: Optional[str] = Field(None, description="Filter by collection name")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=20, ge=1, le=100, description="Number of bookmarks per page")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")

    class Config:
        from_attributes = True


class BookmarkResponse(BaseModel):
    """Response for individual bookmarks"""
    id: UUID
    post_id: UUID
    post_title: str
    post_excerpt: Optional[str] = None
    post_author: str
    collection_name: str
    created_at: datetime
    post_published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """Paginated bookmark list response"""
    bookmarks: List[BookmarkResponse]
    pagination: PaginationMeta
    collections: List[BookmarkCollectionResponse]

    class Config:
        from_attributes = True


class UserFollowingQuery(BaseModel):
    """Query parameters for following/followers listing"""
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=20, ge=1, le=100, description="Number of users per page")
    search: Optional[str] = Field(None, description="Search term for user names")

    class Config:
        from_attributes = True


class UserFollowResponse(BaseModel):
    """Response for user follow relationships"""
    id: UUID
    name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    is_following: bool = False
    is_followed_by: bool = False
    followed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserFollowListResponse(BaseModel):
    """Paginated user follow list response"""
    users: List[UserFollowResponse]
    pagination: PaginationMeta
    total_followers: int
    total_following: int

    class Config:
        from_attributes = True


class InteractionStatsResponse(BaseModel):
    """Response for interaction statistics"""
    user_id: UUID
    total_likes_given: int = 0
    total_likes_received: int = 0
    total_bookmarks: int = 0
    total_following: int = 0
    total_followers: int = 0
    total_posts_liked: int = 0
    total_posts_bookmarked: int = 0
    most_liked_post_id: Optional[UUID] = None
    most_bookmarked_post_id: Optional[UUID] = None
    interaction_streak: int = 0
    last_interaction_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteractionNotificationResponse(BaseModel):
    """Response for interaction notifications"""
    id: UUID
    type: InteractionType
    actor_id: UUID
    actor_name: str
    target_type: str
    target_id: UUID
    target_title: Optional[str] = None
    message: str
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionAnalyticsResponse(BaseModel):
    """Response for interaction analytics"""
    post_id: UUID
    date: datetime
    like_count: int = 0
    bookmark_count: int = 0
    view_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    total_interactions: int = 0

    class Config:
        from_attributes = True 