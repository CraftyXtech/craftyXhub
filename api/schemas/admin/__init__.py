"""
Admin Schemas

This module contains Pydantic request/response schemas for admin operations,
implementing the specifications from PRDs/04-Admin-Modules/.

Schemas:
- Dashboard: Analytics and dashboard data schemas
- User Management: User CRUD and role management schemas  
- Content Approval: Post and comment moderation schemas
- System Management: Settings and system operation schemas
"""

# Import specific classes to avoid conflicts
from .dashboard import (
    DashboardResponse, UserStatsResponse, ContentOverviewResponse, 
    ViewTrendsResponse, ApprovalQueueResponse, FiltersResponse,
    DashboardQueryParams, GrowthMetricsResponse
)
from .user_management import (
    UserListResponse, UserSummaryResponse, RoleUpdateRequest,
    BulkRoleUpdateRequest, UserManagementLogResponse, UserDetailResponse,
    PaginationResponse, UserFiltersResponse, RoleUpdateResponse,
    BulkOperationResponse, UserDeletionRequest, UserActivationRequest
)
from .content_approval import (
    PostApprovalRequest, PostRejectionRequest, PendingContentResponse,
    PostReviewResponse, ContentApprovalHistoryResponse, CommentReviewResponse,
    ApprovalOperationResponse, BulkApprovalRequest, ContentModerationStats
)
from .system_management import (
    SystemInfoResponse, CacheClearRequest, SettingsResponse,
    SettingsUpdateRequest, MigrationStatusResponse, SystemHealthResponse,
    SystemOperationResponse, MaintenanceModeRequest
)

__all__ = [
    # Dashboard schemas
    "DashboardResponse",
    "UserStatsResponse", 
    "ContentOverviewResponse",
    "ViewTrendsResponse",
    "ApprovalQueueResponse",
    "FiltersResponse",
    
    # User management schemas
    "UserListResponse",
    "UserSummaryResponse",
    "RoleUpdateRequest",
    "UserStatsResponse",
    "BulkRoleUpdateRequest",
    "UserManagementLogResponse",
    
    # Content approval schemas
    "PostApprovalRequest",
    "PostRejectionRequest", 
    "PendingContentResponse",
    "PostReviewResponse",
    "ContentApprovalHistoryResponse",
    
    # System management schemas
    "SystemInfoResponse",
    "CacheClearRequest",
    "SettingsResponse",
    "SettingsUpdateRequest",
    "MigrationStatusResponse"
] 