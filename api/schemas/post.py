from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .user import UserResponse
from .base import BaseSchema, TimestampMixin


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(CategoryBase, BaseSchema):
    id: int
    created_at: datetime
    post_count: Optional[int] = 0


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase, BaseSchema):
    id: int
    created_at: datetime
    post_count: Optional[int] = 0


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)


class PostCreate(PostBase):
    slug: str = Field(..., min_length=1, max_length=200)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []
    is_published: bool = False
    is_featured: bool = False
    featured_image: Optional[str] = None
    reading_time: Optional[int] = None


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    featured_image: Optional[str] = None
    reading_time: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)


class PostResponse(PostBase, TimestampMixin, BaseSchema):
    id: int
    slug: str
    author_id: int
    category_id: Optional[int] = None
    is_published: bool
    is_featured: bool
    view_count: int
    reading_time: Optional[int] = None
    featured_image: Optional[str] = None
    published_at: Optional[datetime] = None
    author: UserResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    comment_count: Optional[int] = 0
    like_count: Optional[int] = 0
    is_liked: Optional[bool] = False


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