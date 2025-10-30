from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .user import UserResponse
from .comment import CommentResponse
from .base import BaseSchema, TimestampMixin


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class CategoryChildResponse(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase, BaseSchema):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    post_count: Optional[int] = 0
    subcategories: List['CategoryChildResponse'] = []

CategoryResponse.model_rebuild()


class CategoryCreateResponse(CategoryBase, BaseSchema):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    post_count: Optional[int] = 0

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase, BaseSchema):
    id: int
    created_at: datetime
    post_count: Optional[int] = 0

class TagListResponse(BaseModel):
    tags: List[TagResponse]

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    content_blocks: Optional[Dict[str, Any]] = None
    excerpt: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)

    @classmethod
    def validate_content(cls, values):
        content = values.get('content')
        content_blocks = values.get('content_blocks')
        
        if not content and not content_blocks:
            raise ValueError('Either content or content_blocks must be provided')
        
        return values


class PostCreate(PostBase):
    slug: str = Field(..., min_length=1, max_length=200)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []
    featured_image: Optional[str] = None
    reading_time: Optional[int] = None
    is_published: Optional[bool] = False
    is_featured: Optional[bool] = False


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    content_blocks: Optional[Dict[str, Any]] = None
    excerpt: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    featured_image: Optional[str] = None
    reading_time: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)
    is_published: Optional[bool] = None

    
class PostResponse(BaseModel):
    uuid: str
    title: str
    slug: str
    content: str
    content_blocks: Optional[Dict[str, Any]]
    excerpt: Optional[str]
    featured_image: Optional[str]
    is_published: bool
    is_featured: bool
    view_count: int
    reading_time: Optional[int]
    meta_title: Optional[str]
    meta_description: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    is_reviewed: bool
    review_comments: Optional[str]
    is_flagged: bool
    author: Optional[UserResponse]
    category: Optional[CategoryCreateResponse]
    tags: List[TagResponse]
    comments: List[CommentResponse]
    liked_by: List[UserResponse]
    bookmarked_by: List[UserResponse]  

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    size: int


class PostStatsResponse(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    total_views: int
    total_likes: int
    
class ReportCreate(BaseModel):
    reason: str
    description: Optional[str] = None

class ReportResponse(BaseModel):
    uuid: str
    post: Optional[PostResponse]
    user_id: Optional[UserResponse]
    reason: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True