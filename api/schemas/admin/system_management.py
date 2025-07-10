from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class CacheType(str, Enum):
    """Cache types for clearing operations."""
    APPLICATION = "application"
    VIEW = "view" 
    ROUTE = "route"
    CONFIG = "config"
    ALL = "all"


class OperationStatus(str, Enum):
    """System operation status."""
    SUCCESS = "success"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"


class DiskUsageResponse(BaseModel):
    """Disk usage information."""
    total: int
    used: int
    free: int
    percentage: float


class SystemInfoResponse(BaseModel):
    """System information response."""
    python_version: str
    fastapi_version: str
    database_type: str
    server_software: str
    memory_limit: str
    max_execution_time: str
    upload_max_filesize: str
    post_max_size: str
    disk_usage: DiskUsageResponse
    cpu_count: int
    architecture: str


class SystemStatsResponse(BaseModel):
    """System statistics response."""
    cache_driver: str
    session_driver: str
    queue_connection: str
    database_connections: int
    active_sessions: int
    memory_usage: float
    cpu_usage: float


class SystemHealthResponse(BaseModel):
    """System health check response."""
    overall_status: str  # healthy, warning, critical
    database_status: str
    database_response_time: Optional[float] = None
    memory_status: str
    memory_usage_percent: float
    disk_status: str
    disk_usage_percent: float
    cpu_usage_percent: float
    uptime_seconds: int
    last_check: datetime
    
    
class SystemMetricsResponse(BaseModel):
    """Real-time system metrics."""
    cpu_usage_per_core: List[float]
    cpu_usage_average: float
    memory_total: int
    memory_used: int
    memory_available: int
    memory_percent: float
    disk_read_bytes: int
    disk_write_bytes: int
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    load_average: List[float]
    timestamp: datetime


class CacheClearRequest(BaseModel):
    """Request to clear cache."""
    cache_type: CacheType
    confirm: bool = Field(True, description="Confirmation for cache clearing")


class CacheStatusResponse(BaseModel):
    """Cache status information."""
    driver: str
    size: str
    entries: int
    hit_rate: float
    miss_rate: float
    last_clear: Optional[datetime] = None


class MigrationInfo(BaseModel):
    """Migration information."""
    name: str
    status: str  # pending, applied, failed
    applied_at: Optional[datetime] = None
    batch: Optional[int] = None


class MigrationHistoryResponse(BaseModel):
    """Migration history entry."""
    version: str
    name: str
    applied_at: datetime
    status: str


class MigrationStatusResponse(BaseModel):
    """Database migration status."""
    current_version: str
    pending_migrations: List[str]
    migration_history: List[MigrationHistoryResponse]


class MigrationExecutionRequest(BaseModel):
    """Request to execute migrations."""
    target_migration: Optional[str] = None  # If None, run all pending
    confirm: bool = Field(True, description="Confirmation for migration execution")
    dry_run: bool = Field(False, description="Test migration without applying")


class EditorPermissionsResponse(BaseModel):
    """Editor permissions configuration."""
    can_publish: bool
    requires_approval: bool
    can_manage_categories: bool
    can_manage_tags: bool
    can_moderate_comments: bool


class EditorPermissionsRequest(BaseModel):
    """Request to update editor permissions."""
    can_publish: Optional[bool] = None
    requires_approval: Optional[bool] = None
    can_manage_categories: Optional[bool] = None
    can_manage_tags: Optional[bool] = None
    can_moderate_comments: Optional[bool] = None


class SettingsResponse(BaseModel):
    """Site settings response."""
    site_name: str
    site_description: Optional[str] = None
    site_url: str
    maintenance_mode: bool
    allow_user_registration: bool
    default_user_role: str
    require_email_verification: bool
    default_editor_permissions: EditorPermissionsResponse
    max_upload_size: int
    allowed_file_types: List[str]
    posts_per_page: int
    comments_enabled: bool
    guest_comments_enabled: bool
    auto_approve_comments: bool


class SettingsUpdateRequest(BaseModel):
    """Request to update site settings."""
    site_name: Optional[str] = Field(None, min_length=1, max_length=100)
    site_description: Optional[str] = Field(None, max_length=500)
    site_url: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    allow_user_registration: Optional[bool] = None
    default_user_role: Optional[str] = Field(None, pattern="^(user|editor)$")
    require_email_verification: Optional[bool] = None
    default_editor_permissions: Optional[EditorPermissionsRequest] = None
    max_upload_size: Optional[int] = Field(None, ge=1, le=100)  # MB
    allowed_file_types: Optional[List[str]] = None
    posts_per_page: Optional[int] = Field(None, ge=1, le=100)
    comments_enabled: Optional[bool] = None
    guest_comments_enabled: Optional[bool] = None
    auto_approve_comments: Optional[bool] = None


class SystemOperationRequest(BaseModel):
    """Request for system operations."""
    operation_type: str
    parameters: Optional[Dict[str, Any]] = None
    confirm: bool = Field(True, description="Confirmation for operation")


class SystemOperationResponse(BaseModel):
    """Response for system operations."""
    operation_id: UUID
    operation_type: str
    status: OperationStatus
    message: str
    output: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class MaintenanceModeRequest(BaseModel):
    """Request to toggle maintenance mode."""
    enabled: bool
    message: Optional[str] = Field(None, max_length=200, description="Message to display during maintenance")
    allowed_ips: Optional[List[str]] = Field(None, description="IPs allowed during maintenance")


class BackupResponse(BaseModel):
    """Backup information."""
    id: UUID
    type: str  # database, files, full
    size: str
    created_at: datetime
    status: str  # completed, failed, in_progress
    file_path: Optional[str] = None


class BackupListResponse(BaseModel):
    """List of backups."""
    backups: List[BackupResponse]
    total_size: str
    last_backup: Optional[datetime] = None


class BackupCreateRequest(BaseModel):
    """Request to create backup."""
    type: str = Field(default="full", pattern="^(database|files|full)$")
    description: Optional[str] = Field(None, max_length=200)


class LogLevelRequest(BaseModel):
    """Request to change log level."""
    level: str = Field(..., pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Duration to keep this level (max 24h)")


class ServerConfigResponse(BaseModel):
    """Server configuration information."""
    debug_mode: bool
    log_level: str
    timezone: str
    locale: str
    database_url: str  # Masked for security
    redis_url: Optional[str] = None  # Masked for security
    email_driver: str
    queue_driver: str
    session_lifetime: int
    cors_origins: List[str]


class PerformanceMetricsResponse(BaseModel):
    """Performance monitoring metrics."""
    avg_response_time: float
    total_requests: int
    error_rate: float
    slowest_endpoints: List[Dict[str, Any]]
    database_query_time: float
    cache_hit_rate: float
    memory_usage_trend: List[Dict[str, Any]]
    
    
class SystemMaintenanceResponse(BaseModel):
    """System maintenance operations response."""
    maintenance_mode: bool
    last_cache_clear: Optional[datetime] = None
    last_migration: Optional[datetime] = None
    last_backup: Optional[datetime] = None
    pending_operations: List[SystemOperationResponse] 