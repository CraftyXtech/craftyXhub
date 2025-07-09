"""Post schemas for editor module."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from schemas.auth import AuthorResponse
from schemas.post import CategoryResponse, TagResponse


class PostCreateRequest(BaseModel):
    """Request schema for creating a new post."""
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    excerpt: Optional[str] = Field(max_length=500, default=None)
    featured_image_path: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: List[UUID] = []
    status: str = Field(default="draft", pattern="^(draft|under_review|scheduled)$")
    published_at: Optional[datetime] = None
    comments_enabled: bool = Field(default=True)
    
    @validator('published_at')
    def validate_scheduled_date(cls, v, values):
        if values.get('status') == 'scheduled' and not v:
            raise ValueError('Published date required for scheduled posts')
        return v


class PostUpdateRequest(BaseModel):
    """Request schema for updating an existing post."""
    title: Optional[str] = Field(max_length=255, default=None)
    body: Optional[str] = None
    excerpt: Optional[str] = Field(max_length=500, default=None)
    featured_image_path: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None
    status: Optional[str] = Field(pattern="^(draft|under_review|scheduled)$", default=None)
    published_at: Optional[datetime] = None
    comments_enabled: Optional[bool] = None
    
    @validator('published_at')
    def validate_scheduled_date(cls, v, values):
        if values.get('status') == 'scheduled' and not v:
            raise ValueError('Published date required for scheduled posts')
        return v


class PostListRequest(BaseModel):
    """Request schema for listing posts."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=50)
    search: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[UUID] = None
    tag_id: Optional[UUID] = None
    sort_by: str = Field(default="updated_at")
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$")


class PostResponse(BaseModel):
    """Response schema for post data."""
    id: UUID
    title: str
    slug: str
    body: str
    excerpt: Optional[str]
    featured_image_path: Optional[str]
    status: str
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    author: AuthorResponse
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    comments_enabled: bool
    view_count: int
    like_count: int
    comment_count: int
    can_edit: bool
    can_delete: bool
    can_publish: bool

    class Config:
        from_attributes = True


class PostSummaryResponse(BaseModel):
    """Response schema for post summary data."""
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image_path: Optional[str]
    status: str
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    author: AuthorResponse
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    view_count: int
    like_count: int
    comment_count: int

    class Config:
        from_attributes = True


class BulkPostRequest(BaseModel):
    """Request schema for bulk post operations."""
    post_ids: List[UUID] = Field(max_items=100)
    action: str = Field(pattern="^(submit_review|delete|update_category|update_tags)$")
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None


class PostRevisionResponse(BaseModel):
    """Response schema for post revision data."""
    id: UUID
    revision_number: int
    title: str
    body: str
    excerpt: Optional[str]
    changes_summary: str
    editor: AuthorResponse
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowHistoryResponse(BaseModel):
    """Response schema for workflow history."""
    id: UUID
    from_status: str
    to_status: str
    changed_by: AuthorResponse
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AutoSaveRequest(BaseModel):
    """Request schema for auto-save functionality."""
    content: Dict[str, Any]  # JSON representation of current post state


class PostSubmitReviewRequest(BaseModel):
    """Request schema for submitting post for review."""
    message: Optional[str] = Field(max_length=500, default=None)


class PostResubmitRequest(BaseModel):
    """Request schema for resubmitting post after rejection."""
    message: Optional[str] = Field(max_length=500, default=None)
    changes_made: str = Field(min_length=1, max_length=1000) 