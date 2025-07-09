"""
Web post schemas for public-facing API endpoints.

Contains Pydantic models for post listing, viewing, and search functionality
in the public web interface.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from schemas.auth import AuthorResponse
from schemas.post import CategoryResponse, TagResponse
from schemas.user import UserSummaryResponse


class PostListFilters(BaseModel):
    """Request filters for post listing endpoint."""
    
    q: Optional[str] = Field(None, max_length=200, description="Search query")
    category: Optional[str] = Field(None, description="Category slug")
    tag: Optional[str] = Field(None, description="Tag slug")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=9, ge=1, le=50, description="Items per page")
    sort_by: str = Field(default="published_at", description="Sort field")
    sort_direction: str = Field(default="desc", description="Sort direction")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_sorts = ['published_at', 'title', 'view_count', 'like_count']
        if v not in allowed_sorts:
            raise ValueError(f'sort_by must be one of {allowed_sorts}')
        return v
    
    @validator('sort_direction')
    def validate_sort_direction(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_direction must be asc or desc')
        return v
    
    @validator('q')
    def validate_search_query(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Search query must be at least 2 characters')
        return v.strip() if v else None


class AuthorSummaryResponse(BaseModel):
    """Author summary for post responses."""
    
    id: UUID
    name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    role: str


class CategorySummaryResponse(BaseModel):
    """Category summary for post responses."""
    
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None


class TagSummaryResponse(BaseModel):
    """Tag summary for post responses."""
    
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None


class InteractionCountsResponse(BaseModel):
    """Interaction counts for posts."""
    
    likes_count: int = 0
    bookmarks_count: int = 0
    comments_count: int = 0
    views_count: int = 0


class PostSummaryResponse(BaseModel):
    """Post summary for listing responses."""
    
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image_path: Optional[str] = None
    published_at: datetime
    reading_time: Optional[int] = None  # in minutes
    author: AuthorSummaryResponse
    category: Optional[CategorySummaryResponse] = None
    tags: List[TagSummaryResponse] = []
    interaction_counts: InteractionCountsResponse
    
    class Config:
        from_attributes = True


class CategoryWithCountResponse(BaseModel):
    """Category with post count for filtering."""
    
    id: Optional[UUID] = None
    name: str
    slug: str
    posts_count: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    """Pagination metadata for responses."""
    
    page: int
    per_page: int
    total_pages: int
    total_count: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class PostListResponse(BaseModel):
    """Response for post listing endpoint."""
    
    posts: List[PostSummaryResponse]
    pagination: PaginationResponse
    categories: List[CategoryWithCountResponse]
    filters: PostListFilters
    total_count: int
    
    class Config:
        from_attributes = True


class CommentThreadResponse(BaseModel):
    """Comment thread for post detail."""
    
    id: UUID
    body: str
    created_at: datetime
    updated_at: datetime
    user: UserSummaryResponse
    parent_id: Optional[UUID] = None
    replies: List['CommentThreadResponse'] = []
    can_reply: bool = True
    
    class Config:
        from_attributes = True


class UserInteractionStatusResponse(BaseModel):
    """User interaction status with a post."""
    
    can_like: bool = False
    can_bookmark: bool = False
    can_comment: bool = False
    has_liked: bool = False
    has_bookmarked: bool = False
    reading_progress: Optional[int] = None  # Percentage


class SEODataResponse(BaseModel):
    """SEO metadata for posts."""
    
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    schema_markup: Optional[Dict[str, Any]] = None


class RelatedPostResponse(BaseModel):
    """Related post for post detail."""
    
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image_path: Optional[str] = None
    published_at: datetime
    reading_time: Optional[int] = None
    author: AuthorSummaryResponse
    category: Optional[CategorySummaryResponse] = None
    similarity_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class PostDetailResponse(BaseModel):
    """Detailed post response for individual post view."""
    
    id: UUID
    title: str
    slug: str
    body: str  # Full formatted content
    excerpt: Optional[str] = None
    featured_image_path: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: datetime
    updated_at: datetime
    reading_time: Optional[int] = None
    view_count: int = 0
    author: AuthorSummaryResponse
    category: Optional[CategorySummaryResponse] = None
    tags: List[TagSummaryResponse] = []
    comments: List[CommentThreadResponse] = []
    related_posts: List[RelatedPostResponse] = []
    interaction_counts: InteractionCountsResponse
    interaction_status: Optional[UserInteractionStatusResponse] = None
    seo_data: SEODataResponse
    
    class Config:
        from_attributes = True


class SearchSuggestionResponse(BaseModel):
    """Search suggestion response."""
    
    query: str
    suggestions: List[str]
    popular_searches: List[str]
    category_suggestions: List[CategorySummaryResponse]
    tag_suggestions: List[TagSummaryResponse]


class PostSearchResponse(BaseModel):
    """Advanced search response for posts."""
    
    posts: List[PostSummaryResponse]
    pagination: PaginationResponse
    search_query: str
    search_results_count: int
    search_time: float  # in seconds
    filters_applied: Dict[str, Any]
    suggestions: List[str] = []
    
    class Config:
        from_attributes = True


# Update CommentThreadResponse to handle recursive references
CommentThreadResponse.model_rebuild() 