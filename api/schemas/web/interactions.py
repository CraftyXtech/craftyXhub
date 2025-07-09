"""
Web interaction schemas for public-facing API endpoints.

Contains Pydantic models for user interactions (likes, bookmarks)
in the public web interface.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from schemas.user import UserSummaryResponse


class InteractionCountsResponse(BaseModel):
    """Response schema for interaction counts."""
    
    likes_count: int = 0
    bookmarks_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    shares_count: int = 0
    
    class Config:
        from_attributes = True


class InteractionResponse(BaseModel):
    """Response schema for interaction operations."""
    
    success: bool
    action: str  # 'liked', 'unliked', 'bookmarked', 'unbookmarked'
    message: str
    post_id: UUID
    user_id: UUID
    interaction_counts: InteractionCountsResponse
    redirect_url: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action": "liked",
                "message": "Post liked successfully",
                "post_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e7890-e12b-34c5-d678-901234567890",
                "interaction_counts": {
                    "likes_count": 15,
                    "bookmarks_count": 8,
                    "comments_count": 3,
                    "views_count": 120
                },
                "redirect_url": "/posts/example-post",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class InteractionStatusResponse(BaseModel):
    """Response schema for user interaction status with a post."""
    
    post_id: UUID
    user_id: Optional[UUID] = None
    user_has_liked: bool = False
    user_has_bookmarked: bool = False
    user_has_commented: bool = False
    user_has_viewed: bool = False
    can_like: bool = True
    can_bookmark: bool = True
    can_comment: bool = True
    interaction_counts: InteractionCountsResponse
    last_interaction: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BulkInteractionRequest(BaseModel):
    """Request schema for bulk interaction operations."""
    
    post_ids: List[UUID] = Field(max_items=50, description="List of post IDs")
    action: str = Field(description="Interaction action")
    
    @validator('post_ids')
    def validate_post_ids(cls, v):
        if not v:
            raise ValueError('At least one post ID is required')
        if len(v) != len(set(v)):
            raise ValueError('Duplicate post IDs are not allowed')
        return v
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['like', 'unlike', 'bookmark', 'unbookmark']
        if v not in allowed_actions:
            raise ValueError(f'action must be one of {allowed_actions}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e12b-34c5-d678-901234567890"
                ],
                "action": "like"
            }
        }


class BulkInteractionResponse(BaseModel):
    """Response schema for bulk interaction operations."""
    
    success: bool
    message: str
    processed_count: int
    failed_count: int
    results: List[InteractionResponse]
    errors: List[Dict[str, Any]] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Bulk operation completed",
                "processed_count": 2,
                "failed_count": 0,
                "results": [],
                "errors": []
            }
        }


class UserInteractionHistoryRequest(BaseModel):
    """Request schema for user interaction history."""
    
    interaction_type: Optional[str] = Field(None, description="Filter by interaction type")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @validator('interaction_type')
    def validate_interaction_type(cls, v):
        if v and v not in ['like', 'bookmark', 'comment', 'view', 'share']:
            raise ValueError('interaction_type must be like, bookmark, comment, view, or share')
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class UserInteractionHistoryResponse(BaseModel):
    """Response schema for user interaction history."""
    
    interactions: List[Dict[str, Any]]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    summary: Dict[str, int]  # Count by interaction type
    
    class Config:
        from_attributes = True


class InteractionAnalyticsRequest(BaseModel):
    """Request schema for interaction analytics."""
    
    post_id: Optional[UUID] = Field(None, description="Filter by post ID")
    time_period: str = Field(default="7d", description="Time period for analytics")
    group_by: str = Field(default="day", description="Group results by time unit")
    
    @validator('time_period')
    def validate_time_period(cls, v):
        allowed_periods = ['1d', '7d', '30d', '90d', '1y']
        if v not in allowed_periods:
            raise ValueError(f'time_period must be one of {allowed_periods}')
        return v
    
    @validator('group_by')
    def validate_group_by(cls, v):
        allowed_groups = ['hour', 'day', 'week', 'month']
        if v not in allowed_groups:
            raise ValueError(f'group_by must be one of {allowed_groups}')
        return v


class InteractionAnalyticsResponse(BaseModel):
    """Response schema for interaction analytics."""
    
    post_id: Optional[UUID] = None
    time_period: str
    group_by: str
    total_interactions: int
    analytics_data: List[Dict[str, Any]]
    trending_posts: List[Dict[str, Any]] = []
    top_interactors: List[UserSummaryResponse] = []
    interaction_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True


class PostInteractionSummaryResponse(BaseModel):
    """Summary of all interactions for a specific post."""
    
    post_id: UUID
    total_interactions: int
    interaction_counts: InteractionCountsResponse
    recent_interactions: List[Dict[str, Any]]
    top_interactors: List[UserSummaryResponse]
    interaction_timeline: List[Dict[str, Any]]
    engagement_rate: float
    virality_score: float
    
    class Config:
        from_attributes = True


class InteractionNotificationRequest(BaseModel):
    """Request schema for interaction notifications."""
    
    notification_type: str = Field(description="Type of notification")
    enabled: bool = Field(description="Enable or disable notification")
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = [
            'like_received', 'bookmark_received', 'comment_received',
            'post_trending', 'milestone_reached'
        ]
        if v not in allowed_types:
            raise ValueError(f'notification_type must be one of {allowed_types}')
        return v


class InteractionNotificationResponse(BaseModel):
    """Response schema for interaction notification settings."""
    
    success: bool
    message: str
    notification_settings: Dict[str, bool]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InteractionRateLimitResponse(BaseModel):
    """Response schema for interaction rate limit information."""
    
    user_id: UUID
    interaction_type: str
    current_count: int
    limit: int
    reset_time: datetime
    remaining: int
    is_limited: bool
    
    class Config:
        from_attributes = True


class PopularContentResponse(BaseModel):
    """Response schema for popular content analytics."""
    
    time_period: str
    total_posts: int
    popular_posts: List[Dict[str, Any]]
    trending_tags: List[str]
    top_categories: List[str]
    engagement_summary: Dict[str, int]
    growth_metrics: Dict[str, float]
    
    class Config:
        from_attributes = True


class TrendingPostsResponse(BaseModel):
    """Response schema for trending posts."""
    
    timeframe: str
    total_posts: int
    trending_posts: List[Dict[str, Any]]
    trending_score_explanation: str
    category_trends: Dict[str, int]
    
    class Config:
        from_attributes = True


class EngagementStatsResponse(BaseModel):
    """Response schema for engagement statistics."""
    
    timeframe: str
    total_interactions: int
    likes_count: int
    bookmarks_count: int
    comments_count: int
    views_count: int
    shares_count: int
    engagement_rate: float
    top_posts: List[Dict[str, Any]]
    user_engagement_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True


class InteractionTypeStats(BaseModel):
    """Response schema for interaction type statistics."""
    
    timeframe: str
    interaction_breakdown: Dict[str, int]
    percentage_breakdown: Dict[str, float]
    growth_rates: Dict[str, float]
    most_popular_interaction: str
    total_interactions: int
    
    class Config:
        from_attributes = True 