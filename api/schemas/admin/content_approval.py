from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

from schemas.post import TagResponse, CategoryResponse


class PostStatus(str, Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class CommentStatus(str, Enum):
    """Comment status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SPAM = "spam"


class AuthorResponse(BaseModel):
    """Author information for content."""
    id: UUID
    name: str
    email: str
    avatar: Optional[str] = None
    role: str


class PostApprovalRequest(BaseModel):
    """Request to approve a post."""
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional feedback for the author")


class PostRejectionRequest(BaseModel):
    """Request to reject a post."""
    feedback: str = Field(..., min_length=10, max_length=1000, description="Required feedback explaining rejection reason")


class CommentApprovalRequest(BaseModel):
    """Request to approve a comment."""
    feedback: Optional[str] = Field(None, max_length=500)


class CommentRejectionRequest(BaseModel):
    """Request to reject a comment."""
    feedback: str = Field(..., min_length=5, max_length=500)
    reason: str = Field(..., description="Reason for rejection: spam, inappropriate, etc.")


class PostReviewResponse(BaseModel):
    """Detailed post information for review."""
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    body: str
    status: PostStatus
    difficulty_level: Optional[str] = None
    featured: bool
    comments_enabled: bool
    feedback: Optional[str] = None
    generated_image_path: Optional[str] = None
    
    # Author and categorization
    author: AuthorResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None  # When submitted for review
    
    # Engagement metrics (for context)
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    estimated_reading_time: int = 0


class CommentReviewResponse(BaseModel):
    """Comment information for moderation."""
    id: UUID
    content: str
    status: CommentStatus
    post_id: UUID
    post_title: str
    
    # Author information
    author: Optional[AuthorResponse] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    
    # Threading
    parent_id: Optional[UUID] = None
    replies_count: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Engagement
    likes_count: int = 0


class ContentApprovalHistoryResponse(BaseModel):
    """Content approval history entry."""
    id: UUID
    content_type: str  # 'post' or 'comment'
    content_id: UUID
    admin: AuthorResponse
    action: str  # 'approved', 'rejected', 'pending'
    feedback: Optional[str] = None
    created_at: datetime


class PendingContentResponse(BaseModel):
    """Response for pending content endpoint."""
    posts: List[PostReviewResponse]
    comments: List[CommentReviewResponse]
    pagination: "PaginationResponse"
    total_pending_posts: int
    total_pending_comments: int


class ApprovalOperationResponse(BaseModel):
    """Response for approval/rejection operations."""
    success: bool
    message: str
    content_id: UUID
    content_type: str
    new_status: str
    feedback: Optional[str] = None
    updated_at: datetime


class BulkApprovalRequest(BaseModel):
    """Request for bulk approval operations."""
    content_ids: List[UUID] = Field(min_items=1, max_items=50)
    content_type: str = Field(..., pattern="^(post|comment)$")
    action: str = Field(..., pattern="^(approve|reject)$")
    feedback: Optional[str] = None


class BulkApprovalResult(BaseModel):
    """Result for single item in bulk operation."""
    content_id: UUID
    success: bool
    message: str
    new_status: Optional[str] = None


class BulkApprovalResponse(BaseModel):
    """Response for bulk approval operations."""
    total_requested: int
    successful: int
    failed: int
    results: List[BulkApprovalResult]


class ContentModerationStats(BaseModel):
    """Content moderation statistics."""
    pending_posts: int
    pending_comments: int
    approved_posts_today: int
    rejected_posts_today: int
    approved_comments_today: int
    rejected_comments_today: int
    spam_comments_today: int
    average_approval_time_hours: float


class ContentFilterRequest(BaseModel):
    """Request parameters for content filtering."""
    status: Optional[str] = None
    author_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    content_type: str = Field(default="post", pattern="^(post|comment)$")
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = Field(default="created_at")
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)


class RejectedContentResponse(BaseModel):
    """Response for rejected content listing."""
    posts: List[PostReviewResponse]
    comments: List[CommentReviewResponse]
    pagination: "PaginationResponse"
    total_rejected_posts: int
    total_rejected_comments: int


class ContentStatusUpdateRequest(BaseModel):
    """Request to update content status."""
    status: str = Field(..., pattern="^(draft|under_review|published|rejected|archived)$")
    feedback: Optional[str] = None
    notify_author: bool = Field(default=True)


# Import PaginationResponse to avoid circular imports
class PaginationResponse(BaseModel):
    """Pagination information."""
    page: int
    per_page: int
    total: int
    pages: int
    has_prev: bool
    has_next: bool


# Update forward references
PendingContentResponse.model_rebuild()
RejectedContentResponse.model_rebuild() 