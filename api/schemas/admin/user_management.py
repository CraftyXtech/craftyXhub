from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum

from schemas.auth import UserRole


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"


class UserSummaryResponse(BaseModel):
    """User summary for listing and management."""
    id: UUID
    name: str
    email: str
    role: UserRole
    avatar: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login_at: Optional[datetime] = None
    post_count: int = 0
    comment_count: int = 0
    followers_count: int = 0
    following_count: int = 0


class UserDetailResponse(BaseModel):
    """Detailed user information for admin review."""
    id: UUID
    name: str
    email: str
    role: UserRole
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    # Statistics
    post_count: int = 0
    published_post_count: int = 0
    draft_post_count: int = 0
    comment_count: int = 0
    approved_comment_count: int = 0
    likes_given: int = 0
    likes_received: int = 0
    followers_count: int = 0
    following_count: int = 0
    
    # Engagement metrics
    total_views_received: int = 0
    average_post_views: float = 0.0
    last_post_date: Optional[datetime] = None
    last_comment_date: Optional[datetime] = None


class PaginationResponse(BaseModel):
    """Pagination information."""
    page: int
    per_page: int
    total: int
    pages: int
    has_prev: bool
    has_next: bool


class UserFiltersResponse(BaseModel):
    """Current filters applied to user list."""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    sort_by: str = "created_at"
    sort_direction: str = "desc"


class UserListResponse(BaseModel):
    """Response for user listing endpoint."""
    users: List[UserSummaryResponse]
    pagination: PaginationResponse
    filters: UserFiltersResponse


class RoleUpdateRequest(BaseModel):
    """Request to update user role."""
    role: UserRole
    reason: Optional[str] = None


class RoleUpdateResponse(BaseModel):
    """Response for role update operation."""
    success: bool
    message: str
    user: UserSummaryResponse
    old_role: UserRole
    new_role: UserRole


class BulkRoleUpdateRequest(BaseModel):
    """Request for bulk role updates."""
    user_ids: List[UUID] = Field(min_items=1, max_items=100)
    new_role: UserRole
    reason: Optional[str] = None


class BulkOperationResult(BaseModel):
    """Result for a single user in bulk operation."""
    user_id: UUID
    success: bool
    message: str
    user_name: Optional[str] = None


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    total_requested: int
    successful: int
    failed: int
    results: List[BulkOperationResult]


class UserDeletionRequest(BaseModel):
    """Request to delete user."""
    confirm: bool = Field(True, description="Confirmation flag")
    reason: Optional[str] = None
    soft_delete: bool = Field(False, description="Perform soft delete instead of hard delete")


class UserDeletionResponse(BaseModel):
    """Response for user deletion."""
    success: bool
    message: str
    user_id: UUID
    deletion_type: str  # "soft" or "hard"


class UserActivationRequest(BaseModel):
    """Request to activate/deactivate user."""
    active: bool
    reason: Optional[str] = None


class GrowthMetricsResponse(BaseModel):
    """User growth metrics."""
    daily_growth: float
    weekly_growth: float
    monthly_growth: float
    yearly_growth: float


class UserStatsResponse(BaseModel):
    """Comprehensive user statistics."""
    total: int
    admins: int
    editors: int
    regular_users: int
    active_users: int
    inactive_users: int
    verified_users: int
    unverified_users: int
    recent_signups: List[UserSummaryResponse]
    growth_metrics: GrowthMetricsResponse


class UserManagementLogResponse(BaseModel):
    """User management operation log entry."""
    id: UUID
    admin: UserSummaryResponse
    target_user_id: Optional[UUID]
    action: str
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class RoleHistoryResponse(BaseModel):
    """Role change history for a user."""
    logs: List[UserManagementLogResponse]
    current_role: UserRole
    role_changes_count: int


class UserSearchRequest(BaseModel):
    """Request parameters for user search."""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    verified: Optional[bool] = None
    sort_by: str = Field(default="created_at")
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None 


# ---------------------------------------------------------------------------
# Additional schema definitions required by services.admin.user_management_service
# ---------------------------------------------------------------------------


class UserFilters(UserSearchRequest):
    """Alias for user filtering parameters used by service."""


class UserContributorResponse(BaseModel):
    """Basic contributor statistics for dashboard purposes."""
    id: UUID
    name: str
    avatar: Optional[str] = None
    post_count: int
    comment_count: int
    like_count: int


class UserGrowthMetricsResponse(BaseModel):
    """Metrics representing user growth over time."""
    daily_growth: float
    weekly_growth: float
    monthly_growth: float
    yearly_growth: float


class BulkUserUpdate(BaseModel):
    """Update payload for a single user in bulk operations."""
    user_id: UUID
    new_role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    reason: Optional[str] = None


class UserAuditLogResponse(BaseModel):
    """Audit log entry for user activity."""
    id: UUID
    action: str
    admin_id: Optional[UUID] = None
    target_user_id: UUID
    description: Optional[str] = None
    created_at: datetime


class DailySignupResponse(BaseModel):
    """Sign-up statistics per day for charting growth."""
    date: datetime
    count: int


class UserRoleUpdateRequest(BaseModel):
    """Request model for updating a user's role individually via service."""
    new_role: UserRole
    reason: Optional[str] = None


class PaginatedUsersResponse(BaseModel):
    """Paginated users list with additional metadata."""
    users: List[UserSummaryResponse]
    pagination: PaginationResponse
    filters: UserSearchRequest
    total_count: int
    role_counts: Optional[dict] = None 