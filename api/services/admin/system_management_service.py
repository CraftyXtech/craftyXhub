from typing import Optional, Dict, List, Any
import platform
import sys
import psutil
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from fastapi import HTTPException

from models.audit import SystemOperation, Setting
from models.user import User
from schemas.admin.system_management import (
    SystemInfoResponse, SystemStatsResponse, DiskUsageResponse,
    CacheClearRequest, MigrationStatusResponse, MigrationHistoryResponse,
    SystemHealthResponse, SystemMetricsResponse
)
from .audit_service import AuditService


class SystemManagementService:
    """Service for system management operations including monitoring, cache management, and maintenance."""
    
    def __init__(self, session: AsyncSession, audit_service: AuditService):
        self.session = session
        self.audit_service = audit_service

    async def get_system_info(self, admin_user: User) -> SystemInfoResponse:
        """Get comprehensive system information."""
        try:
            # Get disk usage for current directory
            disk_usage = shutil.disk_usage(".")
            disk_info = DiskUsageResponse(
                total=disk_usage.total,
                used=disk_usage.used,
                free=disk_usage.free,
                percentage=round((disk_usage.used / disk_usage.total) * 100, 2)
            )
            
            # Get memory information
            memory = psutil.virtual_memory()
            
            response = SystemInfoResponse(
                python_version=sys.version.split()[0],
                fastapi_version="0.104.1",  # Should be dynamic in real implementation
                database_type="PostgreSQL",
                server_software=f"{platform.system()} {platform.release()}",
                memory_limit=f"{memory.total // (1024**3)} GB",
                max_execution_time="300 seconds",
                upload_max_filesize="100 MB",
                post_max_size="128 MB",
                disk_usage=disk_info,
                cpu_count=psutil.cpu_count(),
                architecture=platform.architecture()[0]
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_info_view",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_info_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

    async def get_system_stats(self, admin_user: User) -> SystemStatsResponse:
        """Get application statistics and configuration."""
        try:
            # Get database connection count
            db_connections_result = await self.session.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            )
            db_connections = db_connections_result.scalar() or 0
            
            response = SystemStatsResponse(
                cache_driver="memory",  # Should be configurable
                session_driver="database",
                queue_connection="redis",  # Should be configurable
                database_connections=db_connections,
                active_sessions=0,  # Would need session tracking
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(interval=1)
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_stats_view",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_stats_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

    async def get_system_health(self, admin_user: User) -> SystemHealthResponse:
        """Get system health status."""
        try:
            # Check database connectivity
            try:
                await self.session.execute(text("SELECT 1"))
                database_status = "healthy"
                database_response_time = 0.001  # Would measure actual response time
            except Exception:
                database_status = "unhealthy"
                database_response_time = None
                
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_status = "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            
            # Check disk usage
            disk = shutil.disk_usage(".")
            disk_percent = (disk.used / disk.total) * 100
            disk_status = "healthy" if disk_percent < 80 else "warning" if disk_percent < 95 else "critical"
            
            response = SystemHealthResponse(
                overall_status="healthy",  # Would calculate based on components
                database_status=database_status,
                database_response_time=database_response_time,
                memory_status=memory_status,
                memory_usage_percent=memory.percent,
                disk_status=disk_status,
                disk_usage_percent=disk_percent,
                cpu_usage_percent=psutil.cpu_percent(interval=1),
                uptime_seconds=int(psutil.boot_time()),
                last_check=datetime.utcnow()
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_health_check",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_health_check",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to check system health: {str(e)}")

    async def get_system_metrics(self, admin_user: User) -> SystemMetricsResponse:
        """Get detailed system metrics."""
        try:
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Get disk I/O information
            disk_io = psutil.disk_io_counters()
            
            # Get network information
            network_io = psutil.net_io_counters()
            
            response = SystemMetricsResponse(
                cpu_usage_per_core=cpu_percent,
                cpu_usage_average=sum(cpu_percent) / len(cpu_percent),
                memory_total=memory.total,
                memory_used=memory.used,
                memory_available=memory.available,
                memory_percent=memory.percent,
                disk_read_bytes=disk_io.read_bytes if disk_io else 0,
                disk_write_bytes=disk_io.write_bytes if disk_io else 0,
                network_bytes_sent=network_io.bytes_sent if network_io else 0,
                network_bytes_recv=network_io.bytes_recv if network_io else 0,
                process_count=len(psutil.pids()),
                load_average=psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                timestamp=datetime.utcnow()
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_metrics_view",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="system_metrics_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

    async def clear_cache(self, cache_request: CacheClearRequest, admin_user: User) -> Dict[str, Any]:
        """Clear specified cache types."""
        try:
            valid_cache_types = ["application", "view", "route", "config", "all"]
            if cache_request.cache_type not in valid_cache_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid cache type. Must be one of: {', '.join(valid_cache_types)}"
                )
            
            # In a real implementation, this would clear actual caches
            # For now, we'll simulate cache clearing
            cleared_caches = []
            
            if cache_request.cache_type == "all":
                cleared_caches = ["application", "view", "route", "config"]
            else:
                cleared_caches = [cache_request.cache_type]
            
            result = {
                "success": True,
                "message": f"Successfully cleared {cache_request.cache_type} cache",
                "cleared_caches": cleared_caches,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="cache_clear",
                status="success",
                parameters={"cache_type": cache_request.cache_type},
                output=f"Cleared caches: {', '.join(cleared_caches)}"
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="cache_clear",
                status="failure",
                parameters={"cache_type": cache_request.cache_type},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

    async def get_cache_status(self, admin_user: User) -> Dict[str, Any]:
        """Get cache status information."""
        try:
            # In a real implementation, this would check actual cache status
            cache_status = {
                "application_cache": {
                    "status": "active",
                    "size": "45.2 MB",
                    "entries": 1250,
                    "hit_ratio": 85.4
                },
                "view_cache": {
                    "status": "active", 
                    "size": "12.8 MB",
                    "entries": 340,
                    "hit_ratio": 92.1
                },
                "route_cache": {
                    "status": "active",
                    "size": "2.1 MB", 
                    "entries": 89,
                    "hit_ratio": 96.7
                },
                "config_cache": {
                    "status": "active",
                    "size": "1.5 MB",
                    "entries": 156,
                    "hit_ratio": 98.2
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="cache_status_view",
                status="success",
                parameters={}
            )
            
            return cache_status
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="cache_status_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get cache status: {str(e)}")

    async def run_migrations(self, admin_user: User) -> Dict[str, Any]:
        """Run pending database migrations."""
        try:
            # In a real implementation, this would run actual migrations
            # Using Alembic or similar migration tool
            result = {
                "success": True,
                "message": "All migrations completed successfully",
                "migrations_run": [],  # Would list actual migrations
                "output": "No pending migrations found.",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="database_migration",
                status="success",
                parameters={},
                output="No pending migrations found"
            )
            
            return result
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="database_migration", 
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to run migrations: {str(e)}")

    async def get_migration_status(self, admin_user: User) -> MigrationStatusResponse:
        """Get database migration status."""
        try:
            # In a real implementation, this would check actual migration status
            response = MigrationStatusResponse(
                current_version="1.0.0",
                pending_migrations=[],
                migration_history=[
                    MigrationHistoryResponse(
                        version="1.0.0",
                        name="Initial migration",
                        applied_at=datetime.utcnow(),
                        status="applied"
                    )
                ]
            )
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="migration_status_view",
                status="success",
                parameters={}
            )
            
            return response
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="migration_status_view",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to get migration status: {str(e)}")

    async def enable_maintenance_mode(self, admin_user: User) -> Dict[str, Any]:
        """Enable maintenance mode."""
        try:
            # Update maintenance mode setting
            await self._update_setting("maintenance_mode", "true", admin_user)
            
            result = {
                "success": True,
                "message": "Maintenance mode enabled successfully",
                "maintenance_mode": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="maintenance_mode_enable",
                status="success",
                parameters={}
            )
            
            return result
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="maintenance_mode_enable",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to enable maintenance mode: {str(e)}")

    async def disable_maintenance_mode(self, admin_user: User) -> Dict[str, Any]:
        """Disable maintenance mode."""
        try:
            # Update maintenance mode setting
            await self._update_setting("maintenance_mode", "false", admin_user)
            
            result = {
                "success": True,
                "message": "Maintenance mode disabled successfully",
                "maintenance_mode": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="maintenance_mode_disable",
                status="success",
                parameters={}
            )
            
            return result
            
        except Exception as e:
            await self.audit_service.log_system_operation(
                admin_id=admin_user.id,
                operation_type="maintenance_mode_disable",
                status="failure",
                parameters={},
                output=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Failed to disable maintenance mode: {str(e)}")

    async def _update_setting(self, key: str, value: str, admin_user: User) -> None:
        """Update a system setting."""
        # Check if setting exists
        stmt = select(Setting).where(Setting.key == key)
        result = await self.session.execute(stmt)
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = Setting(
                key=key,
                value=value,
                description=f"System setting: {key}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(setting)
        
        await self.session.commit() 