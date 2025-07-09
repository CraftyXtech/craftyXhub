"""Tag schemas for editor module."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
import re

from schemas.auth import AuthorResponse


class TagCreateRequest(BaseModel):
    """Request schema for creating a new tag."""
    name: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = Field(max_length=255, default=None)
    
    @validator('slug')
    def validate_slug(cls, v, values):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class TagUpdateRequest(BaseModel):
    """Request schema for updating an existing tag."""
    name: Optional[str] = Field(max_length=255, default=None)
    slug: Optional[str] = Field(max_length=255, default=None)
    
    @validator('slug')
    def validate_slug(cls, v, values):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class TagResponse(BaseModel):
    """Response schema for tag data."""
    id: UUID
    name: str
    slug: str
    post_count: int
    usage_trend: float
    created_by: AuthorResponse
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    can_edit: bool
    can_delete: bool

    class Config:
        from_attributes = True


class TagListRequest(BaseModel):
    """Request schema for listing tags."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    sort_by: str = Field(default="name")
    sort_direction: str = Field(default="asc", pattern="^(asc|desc)$")
    min_usage: Optional[int] = Field(default=None, ge=0)
    max_usage: Optional[int] = Field(default=None, ge=0)


class TagUsageResponse(BaseModel):
    """Response schema for tag usage statistics."""
    tag: TagResponse
    post_count: int
    usage_percentage: float
    trend_score: float


class TagStatsResponse(BaseModel):
    """Response schema for tag statistics."""
    total_tags: int
    tags_with_posts: int
    unused_tags: int
    trending_tags: List[TagUsageResponse]
    popular_tags: List[TagUsageResponse]
    recent_tags: List[TagResponse]


class BulkTagRequest(BaseModel):
    """Request schema for bulk tag operations."""
    tag_ids: List[UUID] = Field(max_items=100)
    action: str = Field(pattern="^(delete|merge|update)$")
    target_id: Optional[UUID] = None  # For merge operations
    updates: Optional[Dict[str, Any]] = None  # For bulk updates


class TagMergeRequest(BaseModel):
    """Request schema for merging tags."""
    source_tag_ids: List[UUID] = Field(min_items=2, max_items=10)
    target_tag_id: UUID
    delete_source_tags: bool = Field(default=True)


class TaxonomySuggestionsResponse(BaseModel):
    """Response schema for taxonomy suggestions."""
    category_suggestions: List[str]
    tag_suggestions: List[str]
    similar_categories: List['CategoryResponse']
    similar_tags: List[TagResponse]


# Import CategoryResponse for suggestions
from .categories import CategoryResponse
TaxonomySuggestionsResponse.model_rebuild() 