"""
Web comment schemas for public-facing API endpoints.

Contains Pydantic models for comment submission and management
in the public web interface.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

from schemas.user import UserSummaryResponse


class CommentCreateRequest(BaseModel):
    """Request schema for creating a new comment."""
    
    body: str = Field(min_length=1, max_length=2500, description="Comment content")
    parent_id: Optional[UUID] = Field(None, description="Parent comment ID for replies")
    
    @validator('body')
    def validate_body(cls, v):
        if not v.strip():
            raise ValueError('Comment body cannot be empty')
        
        # Check for minimum meaningful content
        if len(v.strip()) < 3:
            raise ValueError('Comment must be at least 3 characters long')
        
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "body": "Great article! Thanks for sharing this information.",
                "parent_id": None
            }
        }


class CommentUpdateRequest(BaseModel):
    """Request schema for updating an existing comment."""
    
    body: str = Field(min_length=1, max_length=2500, description="Updated comment content")
    
    @validator('body')
    def validate_body(cls, v):
        if not v.strip():
            raise ValueError('Comment body cannot be empty')
        
        if len(v.strip()) < 3:
            raise ValueError('Comment must be at least 3 characters long')
        
        return v.strip()


class CommentResponse(BaseModel):
    """Basic comment response schema."""
    
    id: UUID
    user_id: UUID
    post_id: UUID
    parent_id: Optional[UUID] = None
    body: str
    status: str = "approved"  # pending, approved, rejected
    created_at: datetime
    updated_at: datetime
    user: UserSummaryResponse
    replies_count: int = 0
    can_edit: bool = False
    can_delete: bool = False
    
    class Config:
        from_attributes = True


class CommentThreadResponse(BaseModel):
    """Comment thread response with nested replies."""
    
    id: UUID
    user_id: UUID
    post_id: UUID
    parent_id: Optional[UUID] = None
    body: str
    status: str = "approved"
    created_at: datetime
    updated_at: datetime
    user: UserSummaryResponse
    replies: List['CommentThreadResponse'] = []
    replies_count: int = 0
    depth: int = 0  # Thread depth for UI rendering
    can_reply: bool = True
    can_edit: bool = False
    can_delete: bool = False
    
    class Config:
        from_attributes = True


class CommentSubmissionResponse(BaseModel):
    """Response after comment submission."""
    
    success: bool
    message: str
    comment: Optional[CommentResponse] = None
    redirect_url: str
    requires_moderation: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Comment submitted successfully",
                "comment": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "body": "Great article!",
                    "status": "approved"
                },
                "redirect_url": "/posts/example-post#comment-123",
                "requires_moderation": False
            }
        }


class CommentListRequest(BaseModel):
    """Request schema for listing comments."""
    
    post_id: UUID
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Comments per page")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_direction: str = Field(default="asc", description="Sort direction")
    status: Optional[str] = Field(None, description="Filter by status")
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_sorts = ['created_at', 'updated_at']
        if v not in allowed_sorts:
            raise ValueError(f'sort_by must be one of {allowed_sorts}')
        return v
    
    @validator('sort_direction')
    def validate_sort_direction(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_direction must be asc or desc')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'approved', 'rejected']:
            raise ValueError('status must be pending, approved, or rejected')
        return v


class CommentListResponse(BaseModel):
    """Response for comment listing."""
    
    comments: List[CommentThreadResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    post_id: UUID
    
    class Config:
        from_attributes = True


class CommentModerationRequest(BaseModel):
    """Request schema for comment moderation."""
    
    action: str = Field(description="Moderation action")
    reason: Optional[str] = Field(None, max_length=500, description="Moderation reason")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['approve', 'reject', 'flag', 'unflag']
        if v not in allowed_actions:
            raise ValueError(f'action must be one of {allowed_actions}')
        return v


class CommentModerationResponse(BaseModel):
    """Response for comment moderation actions."""
    
    success: bool
    message: str
    comment: CommentResponse
    previous_status: str
    new_status: str
    moderated_by: UserSummaryResponse
    moderated_at: datetime


class CommentStatsResponse(BaseModel):
    """Comment statistics for a post."""
    
    total_comments: int
    approved_comments: int
    pending_comments: int
    rejected_comments: int
    unique_commenters: int
    average_comment_length: float
    most_active_commenter: Optional[UserSummaryResponse] = None
    recent_activity: List[CommentResponse] = []


class CommentReportRequest(BaseModel):
    """Request schema for reporting a comment."""
    
    reason: str = Field(description="Report reason")
    description: Optional[str] = Field(None, max_length=1000, description="Additional details")
    
    @validator('reason')
    def validate_reason(cls, v):
        allowed_reasons = [
            'spam', 'harassment', 'hate_speech', 'inappropriate_content', 
            'misinformation', 'copyright', 'other'
        ]
        if v not in allowed_reasons:
            raise ValueError(f'reason must be one of {allowed_reasons}')
        return v


class CommentReportResponse(BaseModel):
    """Response for comment reporting."""
    
    success: bool
    message: str
    report_id: UUID
    comment_id: UUID
    reported_by: UUID
    reported_at: datetime
    status: str = "pending"  # pending, reviewed, resolved


# Update CommentThreadResponse to handle recursive references
CommentThreadResponse.model_rebuild() 