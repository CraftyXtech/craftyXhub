"""Category schemas for editor module."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
import re

from schemas.post import AuthorResponse


class CategoryCreateRequest(BaseModel):
    """Request schema for creating a new category."""
    name: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    
    @validator('slug')
    def validate_slug(cls, v, values):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class CategoryUpdateRequest(BaseModel):
    """Request schema for updating an existing category."""
    name: Optional[str] = Field(max_length=255, default=None)
    slug: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    
    @validator('slug')
    def validate_slug(cls, v, values):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class CategoryResponse(BaseModel):
    """Response schema for category data."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[UUID]
    parent: Optional['CategoryResponse'] = None
    children: List['CategoryResponse'] = []
    hierarchy_path: str
    post_count: int
    created_by: AuthorResponse
    created_at: datetime
    updated_at: datetime
    can_edit: bool
    can_delete: bool

    class Config:
        from_attributes = True


class CategoryListRequest(BaseModel):
    """Request schema for listing categories."""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_by: str = Field(default="name")
    sort_direction: str = Field(default="asc", pattern="^(asc|desc)$")


class CategoryUsageResponse(BaseModel):
    """Response schema for category usage statistics."""
    category: CategoryResponse
    post_count: int
    usage_percentage: float
    recent_growth: int


class CategoryStatsResponse(BaseModel):
    """Response schema for category statistics."""
    total_categories: int
    categories_with_posts: int
    unused_categories: int
    most_used_categories: List[CategoryUsageResponse]
    recent_categories: List[CategoryResponse]
    hierarchy_depth: int


class BulkCategoryRequest(BaseModel):
    """Request schema for bulk category operations."""
    category_ids: List[UUID] = Field(max_items=100)
    action: str = Field(pattern="^(delete|merge|update)$")
    target_id: Optional[UUID] = None  # For merge operations
    updates: Optional[Dict[str, Any]] = None  # For bulk updates


class CategoryMergeRequest(BaseModel):
    """Request schema for merging categories."""
    source_category_ids: List[UUID] = Field(min_items=2, max_items=10)
    target_category_id: UUID
    delete_source_categories: bool = Field(default=True)


# Enable forward references
CategoryResponse.model_rebuild() 