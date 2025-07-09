"""
Comment API Schemas for CraftyXhub

Request and response schemas for comment API endpoints following SubPRD-CommentAPI.md specifications.
"""

from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum

from .post import PaginationMeta


class CommentSortBy(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    MOST_LIKED = "most_liked"


class CommentModerationAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


class CommentCreateRequest(BaseModel):
    """Request model for creating a new comment"""
    body: str = Field(min_length=1, max_length=2000, description="Comment content")
    parent_id: Optional[UUID] = Field(None, description="Parent comment ID for replies")

    @validator('body')
    def validate_body(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Comment body cannot be empty')
        return v

    class Config:
        from_attributes = True


class CommentUpdateRequest(BaseModel):
    """Request model for updating a comment"""
    body: str = Field(min_length=1, max_length=2000, description="Updated comment content")

    @validator('body')
    def validate_body(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Comment body cannot be empty')
        return v

    class Config:
        from_attributes = True


class GuestCommentRequest(BaseModel):
    """Request model for guest comments"""
    body: str = Field(min_length=1, max_length=2000, description="Comment content")
    guest_name: str = Field(min_length=1, max_length=100, description="Guest name")
    guest_email: EmailStr = Field(description="Guest email address")
    parent_id: Optional[UUID] = Field(None, description="Parent comment ID for replies")

    @validator('body')
    def validate_body(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Comment body cannot be empty')
        return v

    @validator('guest_name')
    def validate_guest_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Guest name cannot be empty')
        return v

    class Config:
        from_attributes = True


class CommentModerationRequest(BaseModel):
    """Request model for comment moderation"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for moderation action")

    class Config:
        from_attributes = True


class BulkCommentModerationRequest(BaseModel):
    """Request model for bulk comment moderation"""
    comment_ids: List[UUID] = Field(max_items=100, description="List of comment IDs to moderate")
    action: CommentModerationAction = Field(description="Moderation action to perform")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for moderation action")

    class Config:
        from_attributes = True


class CommentListQuery(BaseModel):
    """Query parameters for comment listing"""
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    per_page: int = Field(default=20, ge=1, le=100, description="Number of comments per page")
    sort_by: CommentSortBy = Field(default=CommentSortBy.NEWEST, description="Sort order")
    include_replies: bool = Field(default=True, description="Include nested replies")
    max_depth: int = Field(default=5, ge=1, le=10, description="Maximum reply depth to load")

    class Config:
        from_attributes = True


class CommentUserResponse(BaseModel):
    """User information in comment responses"""
    id: UUID
    name: str
    avatar: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response model"""
    id: UUID
    body: str
    user: Optional[CommentUserResponse] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    parent_id: Optional[UUID] = None
    replies: List['CommentResponse'] = []
    reply_count: int = 0
    like_count: int = 0
    is_liked: Optional[bool] = None  # Only if authenticated
    created_at: datetime
    updated_at: datetime
    is_approved: bool = False
    is_guest: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_reply: bool = True
    depth: int = 0
    is_deleted: bool = False

    class Config:
        from_attributes = True


# Forward reference for nested replies
CommentResponse.model_rebuild()


class CommentStatsResponse(BaseModel):
    """Comment statistics response"""
    total_comments: int
    approved_comments: int
    pending_comments: int
    rejected_comments: int
    reply_count: int
    guest_comments: int
    user_comments: int

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Paginated comment list response"""
    comments: List[CommentResponse]
    pagination: PaginationMeta
    stats: CommentStatsResponse
    post_id: UUID

    class Config:
        from_attributes = True


class CommentModerationResponse(BaseModel):
    """Response for comment moderation actions"""
    comment_id: UUID
    action: CommentModerationAction
    success: bool
    message: str
    moderator_id: UUID
    moderated_at: datetime

    class Config:
        from_attributes = True


class BulkCommentModerationResponse(BaseModel):
    """Response for bulk comment moderation"""
    results: List[CommentModerationResponse]
    success_count: int
    failure_count: int
    total_count: int

    class Config:
        from_attributes = True


class CommentHistoryResponse(BaseModel):
    """Comment edit history response"""
    id: UUID
    comment_id: UUID
    old_body: str
    new_body: str
    editor_id: UUID
    edited_at: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class CommentNotificationResponse(BaseModel):
    """Comment notification response"""
    id: UUID
    comment_id: UUID
    post_id: UUID
    post_title: str
    commenter_name: str
    comment_excerpt: str
    notification_type: str  # 'new_comment', 'reply', 'mention'
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class CommentReportRequest(BaseModel):
    """Request model for reporting comments"""
    reason: str = Field(min_length=1, max_length=500, description="Reason for reporting")
    category: str = Field(description="Report category (spam, abuse, inappropriate, etc.)")

    class Config:
        from_attributes = True


class CommentReportResponse(BaseModel):
    """Response for comment reports"""
    id: UUID
    comment_id: UUID
    reporter_id: Optional[UUID] = None
    reason: str
    category: str
    status: str  # 'pending', 'reviewed', 'resolved'
    created_at: datetime

    class Config:
        from_attributes = True 