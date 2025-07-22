from pydantic import BaseModel, Field
from typing import Optional, List
from .base import  TimestampMixin, BaseSchema
from enum import Enum
from .user import  UserResponse


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    is_approved: Optional[bool] = None


class CommentResponse(CommentBase, TimestampMixin, BaseSchema):
    uuid: str
    post_id: int
    parent_id: Optional[int] = None
    is_approved: bool

    author: UserResponse
    replies: List['CommentResponse'] = []
    
class CommentListResponse(BaseModel):
    comments: List[CommentResponse]

class PaginatedCommentResponse(BaseModel):
    items: List[CommentResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool