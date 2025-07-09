from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseEnvironmentConfig(BaseModel, ABC):
    """Base environment configuration with common settings."""
    
    # Environment Identification
    environment: EnvironmentType
    environment_name: str
    deployment_id: Optional[str] = None
    deployment_timestamp: Optional[str] = None
    deployment_version: Optional[str] = None
    
    # Core Application Settings
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = False
    enable_profiling: bool = False
    
    # Performance Settings
    worker_count: int = 1
    max_connections: int = 100
    request_timeout: int = 30
    keepalive_timeout: int = 5
    
    # Security Settings
    cors_enabled: bool = True
    cors_origins: List[str] = ["*"]
    rate_limiting_enabled: bool = True
    security_headers_enabled: bool = True
    csrf_protection_enabled: bool = True
    
    # Session and Authentication
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    jwt_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Database Settings
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 0
    database_pool_timeout: int = 30
    auto_migration: bool = False
    
    # Cache Settings
    cache_enabled: bool = True
    cache_default_ttl: int = 3600
    cache_max_memory: Optional[str] = None
    
    # Email Settings
    email_queue_enabled: bool = True
    email_rate_limit_enabled: bool = True
    email_development_mode: bool = False
    
    # Feature Flags
    feature_flags: Dict[str, bool] = {}
    
    # Monitoring and Alerting
    monitoring_enabled: bool = True
    alerting_enabled: bool = False
    health_check_interval: int = 30
    error_tracking_enabled: bool = False
    
    # File Upload Settings
    max_file_size: int = 10485760  # 10MB
    allowed_file_types: List[str] = ["jpg", "jpeg", "png", "gif", "pdf"]
    file_storage_backend: str = "local"
    
    # API Settings
    api_rate_limit: str = "100/minute"
    api_pagination_default_size: int = 20
    api_pagination_max_size: int = 100
    
    # Background Jobs
    job_queue_enabled: bool = True
    job_retry_attempts: int = 3
    job_retry_delay: int = 60
    
    @abstractmethod
    def get_database_config(self) -> Dict[str, Any]:
        """Get environment-specific database configuration."""
        pass
    
    @abstractmethod
    def get_cache_config(self) -> Dict[str, Any]:
        """Get environment-specific cache configuration."""
        pass
    
    @abstractmethod
    def get_external_services(self) -> Dict[str, Any]:
        """Get environment-specific external service configurations."""
        pass
    
    @abstractmethod
    def get_security_config(self) -> Dict[str, Any]:
        """Get environment-specific security configuration."""
        pass
    
    def validate_configuration(self) -> bool:
        """Validate environment configuration."""
        # Basic validation - can be overridden in subclasses
        if self.worker_count <= 0:
            raise ValueError("worker_count must be positive")
        
        if self.max_connections <= 0:
            raise ValueError("max_connections must be positive")
        
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        
        return True
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration for this environment."""
        return {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": ["console"],
            "disable_existing_loggers": False,
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for this environment."""
        return {
            "enabled": self.cors_enabled,
            "origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        }
    
    def get_rate_limiting_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            "enabled": self.rate_limiting_enabled,
            "api_limit": self.api_rate_limit,
            "login_limit": "5/15minutes",
            "register_limit": "3/hour",
            "password_reset_limit": "3/hour",
        }
    
    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration."""
        return {
            "cookie_secure": self.session_cookie_secure,
            "cookie_httponly": self.session_cookie_httponly,
            "cookie_samesite": self.session_cookie_samesite,
            "expire_seconds": 86400,  # 24 hours
        }
    
    def get_file_upload_config(self) -> Dict[str, Any]:
        """Get file upload configuration."""
        return {
            "max_size": self.max_file_size,
            "allowed_types": self.allowed_file_types,
            "storage_backend": self.file_storage_backend,
            "upload_path": "uploads",
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            "rate_limit": self.api_rate_limit,
            "pagination": {
                "default_size": self.api_pagination_default_size,
                "max_size": self.api_pagination_max_size,
            },
            "timeout": self.request_timeout,
        }
    
    def get_background_job_config(self) -> Dict[str, Any]:
        """Get background job configuration."""
        return {
            "enabled": self.job_queue_enabled,
            "retry_attempts": self.job_retry_attempts,
            "retry_delay": self.job_retry_delay,
            "backend": "redis",
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.feature_flags.get(feature, False)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return {
            "environment": {
                "name": self.environment_name,
                "type": self.environment,
                "debug": self.debug_mode,
                "deployment_id": self.deployment_id,
                "deployment_version": self.deployment_version,
            },
            "database": self.get_database_config(),
            "cache": self.get_cache_config(),
            "security": self.get_security_config(),
            "external_services": self.get_external_services(),
            "logging": self.get_logging_config(),
            "cors": self.get_cors_config(),
            "rate_limiting": self.get_rate_limiting_config(),
            "session": self.get_session_config(),
            "file_upload": self.get_file_upload_config(),
            "api": self.get_api_config(),
            "background_jobs": self.get_background_job_config(),
            "feature_flags": self.feature_flags,
            "monitoring": {
                "enabled": self.monitoring_enabled,
                "alerting": self.alerting_enabled,
                "health_check_interval": self.health_check_interval,
                "error_tracking": self.error_tracking_enabled,
            }
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True 