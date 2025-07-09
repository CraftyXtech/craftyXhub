"""
Post API Schemas for CraftyXhub

Request and response schemas for post API endpoints following SubPRD-PostAPI.md specifications.
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PostSortBy(str, Enum):
    PUBLISHED_AT = "published_at"
    CREATED_AT = "created_at"
    TITLE = "title"
    LIKE_COUNT = "like_count"
    VIEW_COUNT = "view_count"


class PostListQuery(BaseModel):
    """Query parameters for post listing endpoint"""
    category: Optional[str] = Field(None, description="Category slug for filtering")
    search: Optional[str] = Field(None, description="Search term for title, excerpt, content, and tags")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=9, ge=1, le=50, description="Number of posts per page (max 50)")
    sort_by: PostSortBy = Field(default=PostSortBy.PUBLISHED_AT, description="Field to sort by")
    sort_direction: SortDirection = Field(default=SortDirection.DESC, description="Sort direction")

    @validator('search')
    def validate_search(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError('Search term must be at least 2 characters long')
            if len(v) > 100:
                raise ValueError('Search term must be less than 100 characters')
        return v

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            v = v.strip().lower()
            if not v:
                return None
        return v


class AuthorResponse(BaseModel):
    """Author information in post responses"""
    id: UUID
    name: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Category information in post responses"""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    """Tag information in post responses"""
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True


class PostSummaryResponse(BaseModel):
    """Post summary for listing endpoints"""
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image_path: Optional[str] = None
    published_at: datetime
    author: AuthorResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    like_count: int = 0
    view_count: int = 0
    difficulty_level: Optional[str] = None
    estimated_reading_time: Optional[int] = None

    class Config:
        from_attributes = True


class PostDetailResponse(BaseModel):
    """Full post details for individual post endpoint"""
    id: UUID
    title: str
    slug: str
    body: str
    excerpt: Optional[str] = None
    featured_image_path: Optional[str] = None
    published_at: datetime
    author: AuthorResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    like_count: int = 0
    view_count: int = 0
    is_liked: Optional[bool] = None  # Only if authenticated
    is_bookmarked: Optional[bool] = None  # Only if authenticated
    comments_enabled: bool = True
    difficulty_level: Optional[str] = None
    estimated_reading_time: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @validator('total_pages', pre=True, always=True)
    def calculate_total_pages(cls, v, values):
        if 'total' in values and 'per_page' in values:
            per_page = values['per_page']
            total = values['total']
            return (total + per_page - 1) // per_page if per_page > 0 else 0
        return v

    @validator('has_next', pre=True, always=True)
    def calculate_has_next(cls, v, values):
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return False

    @validator('has_prev', pre=True, always=True)
    def calculate_has_prev(cls, v, values):
        if 'page' in values:
            return values['page'] > 1
        return False


class PaginatedPostsResponse(BaseModel):
    """Paginated response for post listing"""
    data: List[PostSummaryResponse]
    pagination: PaginationMeta
    filters: dict = {}  # Applied filters for reference

    class Config:
        from_attributes = True


class PostStatsResponse(BaseModel):
    """Post statistics response"""
    post_id: UUID
    like_count: int
    view_count: int
    comment_count: int
    bookmark_count: int
    share_count: int = 0
    last_viewed_at: Optional[datetime] = None
    last_liked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostViewRequest(BaseModel):
    """Request model for tracking post views"""
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

    class Config:
        from_attributes = True


class PostSearchResponse(BaseModel):
    """Enhanced search response with relevance scoring"""
    posts: List[PostSummaryResponse]
    search_metadata: dict
    suggestions: List[str] = []
    total_results: int
    search_time_ms: float

    class Config:
        from_attributes = True 