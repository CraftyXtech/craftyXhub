from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import require_admin, require_editor_or_admin
from models.user import User
from services.admin import (
    AnalyticsService, UserManagementService, ContentApprovalService,
    SystemManagementService, SettingsService, AuditService
)
from schemas.admin.dashboard import (
    DashboardResponse, UserStatsResponse, ContentStatsResponse,
    SystemStatsResponse, RecentActivityResponse, GrowthMetricsResponse
)
from schemas.admin.user_management import (
    UserListResponse, UserDetailResponse, UserCreateRequest,
    UserUpdateRequest, RoleUpdateRequest, BulkUserActionRequest
)
from schemas.admin.content_approval import (
    PostApprovalResponse, CommentApprovalResponse, PostApprovalRequest,
    CommentApprovalRequest, BulkApprovalRequest, ModerationStatsResponse
)
from schemas.admin.system_management import (
    SystemInfoResponse, SystemHealthResponse, SystemMetricsResponse,
    CacheClearRequest, SettingsResponse, SettingsUpdateRequest,
    MigrationStatusResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_admin_services(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get all admin services."""
    audit_service = AuditService(db)
    
    return {
        "analytics": AnalyticsService(db, audit_service),
        "user_management": UserManagementService(db, audit_service),
        "content_approval": ContentApprovalService(db, audit_service),
        "system_management": SystemManagementService(db, audit_service),
        "settings": SettingsService(db, audit_service),
        "audit": audit_service
    }


# =============================================================================
# DASHBOARD ENDPOINTS
# =============================================================================

@router.get("/dashboard", response_model=DashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> DashboardResponse:
    """Get admin dashboard with role-based analytics."""
    analytics_service = services["analytics"]
    return await analytics_service.get_dashboard_data(current_user)


@router.get("/dashboard/user-stats", response_model=UserStatsResponse)
async def get_user_statistics(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserStatsResponse:
    """Get detailed user statistics."""
    analytics_service = services["analytics"]
    return await analytics_service.get_user_statistics(current_user)


@router.get("/dashboard/content-stats", response_model=ContentStatsResponse)
async def get_content_statistics(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> ContentStatsResponse:
    """Get detailed content statistics."""
    analytics_service = services["analytics"]
    return await analytics_service.get_content_statistics(current_user)


@router.get("/dashboard/growth-metrics", response_model=GrowthMetricsResponse)
async def get_growth_metrics(
    period: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> GrowthMetricsResponse:
    """Get growth metrics for specified period."""
    analytics_service = services["analytics"]
    return await analytics_service.get_growth_metrics(period, current_user)


@router.get("/dashboard/recent-activity", response_model=List[RecentActivityResponse])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> List[RecentActivityResponse]:
    """Get recent admin activity."""
    analytics_service = services["analytics"]
    return await analytics_service.get_recent_activity(limit, current_user)


# =============================================================================
# USER MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at", pattern="^(name|email|role|created_at)$"),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserListResponse:
    """Get paginated list of users with filtering and sorting."""
    user_service = services["user_management"]
    return await user_service.get_users(
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        status=status,
        sort_by=sort_by,
        sort_direction=sort_direction,
        admin_user=current_user
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserDetailResponse:
    """Get detailed user information."""
    user_service = services["user_management"]
    return await user_service.get_user_detail(user_id, current_user)


@router.post("/users", response_model=UserDetailResponse)
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserDetailResponse:
    """Create a new user."""
    user_service = services["user_management"]
    return await user_service.create_user(user_data, current_user)


@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserDetailResponse:
    """Update user information."""
    user_service = services["user_management"]
    return await user_service.update_user(user_id, user_data, current_user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Delete a user."""
    user_service = services["user_management"]
    return await user_service.delete_user(user_id, current_user)


@router.patch("/users/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role(
    user_id: UUID,
    role_data: RoleUpdateRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> UserDetailResponse:
    """Update user role."""
    user_service = services["user_management"]
    return await user_service.update_user_role(user_id, role_data, current_user)


@router.post("/users/bulk-action")
async def bulk_user_action(
    action_data: BulkUserActionRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Perform bulk actions on users."""
    user_service = services["user_management"]
    return await user_service.bulk_user_action(action_data, current_user)


# =============================================================================
# CONTENT APPROVAL ENDPOINTS
# =============================================================================

@router.get("/content/posts/pending", response_model=List[PostApprovalResponse])
async def get_pending_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> List[PostApprovalResponse]:
    """Get posts pending approval."""
    content_service = services["content_approval"]
    return await content_service.get_pending_posts(page, per_page, current_user)


@router.get("/content/posts/{post_id}/approval", response_model=PostApprovalResponse)
async def get_post_approval_details(
    post_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> PostApprovalResponse:
    """Get post approval details."""
    content_service = services["content_approval"]
    return await content_service.get_post_approval_details(post_id, current_user)


@router.post("/content/posts/{post_id}/approve")
async def approve_post(
    post_id: UUID,
    approval_data: PostApprovalRequest,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Approve a post."""
    content_service = services["content_approval"]
    return await content_service.approve_post(post_id, approval_data, current_user)


@router.post("/content/posts/{post_id}/reject")
async def reject_post(
    post_id: UUID,
    approval_data: PostApprovalRequest,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Reject a post."""
    content_service = services["content_approval"]
    return await content_service.reject_post(post_id, approval_data, current_user)


@router.get("/content/comments/pending", response_model=List[CommentApprovalResponse])
async def get_pending_comments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> List[CommentApprovalResponse]:
    """Get comments pending approval."""
    content_service = services["content_approval"]
    return await content_service.get_pending_comments(page, per_page, current_user)


@router.post("/content/comments/{comment_id}/approve")
async def approve_comment(
    comment_id: UUID,
    approval_data: CommentApprovalRequest,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Approve a comment."""
    content_service = services["content_approval"]
    return await content_service.approve_comment(comment_id, approval_data, current_user)


@router.post("/content/comments/{comment_id}/reject")
async def reject_comment(
    comment_id: UUID,
    approval_data: CommentApprovalRequest,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Reject a comment."""
    content_service = services["content_approval"]
    return await content_service.reject_comment(comment_id, approval_data, current_user)


@router.post("/content/bulk-approve")
async def bulk_approve_content(
    bulk_data: BulkApprovalRequest,
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Bulk approve content."""
    content_service = services["content_approval"]
    return await content_service.bulk_approve(bulk_data, current_user)


@router.get("/content/moderation-stats", response_model=ModerationStatsResponse)
async def get_moderation_stats(
    current_user: User = Depends(require_editor_or_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> ModerationStatsResponse:
    """Get content moderation statistics."""
    content_service = services["content_approval"]
    return await content_service.get_moderation_stats(current_user)


# =============================================================================
# SYSTEM MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SystemInfoResponse:
    """Get system information."""
    system_service = services["system_management"]
    return await system_service.get_system_info(current_user)


@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SystemHealthResponse:
    """Get system health status."""
    system_service = services["system_management"]
    return await system_service.get_system_health(current_user)


@router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SystemMetricsResponse:
    """Get system metrics."""
    system_service = services["system_management"]
    return await system_service.get_system_metrics(current_user)


@router.post("/system/cache/clear")
async def clear_cache(
    cache_request: CacheClearRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Clear system cache."""
    system_service = services["system_management"]
    return await system_service.clear_cache(cache_request, current_user)


@router.get("/system/cache/status")
async def get_cache_status(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Get cache status."""
    system_service = services["system_management"]
    return await system_service.get_cache_status(current_user)


@router.post("/system/migrate")
async def run_migrations(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Run database migrations."""
    system_service = services["system_management"]
    return await system_service.run_migrations(current_user)


@router.get("/system/migrations", response_model=MigrationStatusResponse)
async def get_migration_status(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> MigrationStatusResponse:
    """Get migration status."""
    system_service = services["system_management"]
    return await system_service.get_migration_status(current_user)


@router.post("/system/maintenance/enable")
async def enable_maintenance_mode(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Enable maintenance mode."""
    system_service = services["system_management"]
    return await system_service.enable_maintenance_mode(current_user)


@router.post("/system/maintenance/disable")
async def disable_maintenance_mode(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Disable maintenance mode."""
    system_service = services["system_management"]
    return await system_service.disable_maintenance_mode(current_user)


# =============================================================================
# SETTINGS ENDPOINTS
# =============================================================================

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SettingsResponse:
    """Get site settings."""
    settings_service = services["settings"]
    return await settings_service.get_settings(current_user)


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdateRequest,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SettingsResponse:
    """Update site settings."""
    settings_service = services["settings"]
    return await settings_service.update_settings(settings_data, current_user)


@router.patch("/settings/{key}")
async def update_single_setting(
    key: str,
    value: str,
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Update a single setting."""
    settings_service = services["settings"]
    return await settings_service.update_single_setting(key, value, current_user)


@router.post("/settings/reset", response_model=SettingsResponse)
async def reset_settings(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> SettingsResponse:
    """Reset settings to default values."""
    settings_service = services["settings"]
    return await settings_service.reset_settings_to_default(current_user)


@router.get("/settings/export")
async def export_settings(
    current_user: User = Depends(require_admin),
    services: Dict[str, Any] = Depends(get_admin_services)
) -> Dict[str, Any]:
    """Export settings for backup."""
    settings_service = services["settings"]
    return await settings_service.export_settings(current_user) 