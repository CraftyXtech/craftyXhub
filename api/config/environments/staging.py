from typing import Dict, Any, List
from .base import BaseEnvironmentConfig, EnvironmentType

class StagingConfig(BaseEnvironmentConfig):
    """Staging environment configuration."""
    
    environment: EnvironmentType = EnvironmentType.STAGING
    environment_name: str = "staging"
    
    # Staging-specific settings
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_tracing: bool = True
    enable_profiling: bool = False
    auto_migration: bool = True
    
    # Staging database
    database_echo: bool = False
    database_pool_size: int = 15
    database_max_overflow: int = 5
    database_pool_timeout: int = 30
    
    # Staging cache
    cache_enabled: bool = True
    cache_default_ttl: int = 1800  # 30 minutes
    cache_max_memory: str = "512MB"
    
    # Staging security (moderate)
    cors_origins: List[str] = [
        "https://staging.craftyhub.com",
        "https://staging-app.craftyhub.com",
        "http://localhost:3000",  # For testing
    ]
    rate_limiting_enabled: bool = True
    session_cookie_secure: bool = True
    csrf_protection_enabled: bool = True
    security_headers_enabled: bool = True
    
    # Staging email
    email_development_mode: bool = False
    email_queue_enabled: bool = True
    email_rate_limit_enabled: bool = True
    
    # Staging features
    feature_flags: Dict[str, bool] = {
        "enable_debug_toolbar": False,
        "enable_mock_services": False,
        "enable_test_data": True,
        "skip_email_verification": False,
        "enable_sql_logging": False,
        "enable_request_logging": True,
        "enable_performance_monitoring": True,
        "enable_beta_features": True,
        "enable_load_testing": True,
    }
    
    # Staging monitoring
    monitoring_enabled: bool = True
    alerting_enabled: bool = True
    error_tracking_enabled: bool = True
    
    # Staging file handling
    max_file_size: int = 10485760  # 10MB
    file_storage_backend: str = "s3"
    
    # Staging API settings
    api_rate_limit: str = "200/minute"
    api_pagination_default_size: int = 20
    api_pagination_max_size: int = 100
    
    # Staging job queue
    job_queue_enabled: bool = True
    job_retry_attempts: int = 3
    job_retry_delay: int = 60
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get staging database configuration."""
        return {
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": 3600,  # 1 hour
            "pool_pre_ping": True,
            "auto_migrate": self.auto_migration,
            "backup_enabled": True,
            "backup_schedule": "0 2 * * *",  # Daily at 2 AM
            "connection_timeout": 30,
            "command_timeout": 60,
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get staging cache configuration."""
        return {
            "enabled": self.cache_enabled,
            "backend": "redis",
            "default_ttl": self.cache_default_ttl,
            "max_memory": self.cache_max_memory,
            "key_prefix": "staging_craftyx",
            "serializer": "json",
            "compression": True,
            "compression_level": 6,
            "connection_pool_size": 10,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }
    
    def get_external_services(self) -> Dict[str, Any]:
        """Get staging external service configurations."""
        return {
            "email": {
                "enabled": True,
                "backend": "smtp",
                "development_mode": self.email_development_mode,
                "queue_enabled": self.email_queue_enabled,
                "rate_limit_enabled": self.email_rate_limit_enabled,
                "template_cache": True,
                "track_opens": True,
                "track_clicks": True,
            },
            "ai": {
                "enabled": True,
                "content_generation": True,
                "image_generation": False,  # Expensive, disabled in staging
                "embedding_generation": True,
                "rate_limiting": True,
                "usage_tracking": True,
            },
            "storage": {
                "enabled": True,
                "backend": self.file_storage_backend,
                "max_size": self.max_file_size,
                "cdn_enabled": True,
                "backup_enabled": True,
                "virus_scanning": True,
            },
            "search": {
                "enabled": True,
                "backend": "elasticsearch",
                "index_prefix": "staging_",
                "real_time_indexing": True,
            },
            "analytics": {
                "enabled": True,
                "sampling_rate": 0.1,  # 10% sampling in staging
                "privacy_mode": True,
            },
            "error_tracking": {
                "enabled": self.error_tracking_enabled,
                "sample_rate": 1.0,
                "environment": "staging",
                "release_tracking": True,
            },
            "cdn": {
                "enabled": True,
                "cache_control": "max-age=3600",
                "compression": True,
            },
            "push_notifications": {
                "enabled": True,
                "test_mode": True,
                "rate_limiting": True,
            },
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get staging security configuration."""
        return {
            "cors": {
                "enabled": self.cors_enabled,
                "origins": self.cors_origins,
                "allow_credentials": True,
                "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"],
            },
            "rate_limiting": {
                "enabled": self.rate_limiting_enabled,
                "api_limit": self.api_rate_limit,
                "login_limit": "10/15minutes",
                "register_limit": "5/hour",
                "password_reset_limit": "3/hour",
            },
            "session": {
                "cookie_secure": self.session_cookie_secure,
                "cookie_httponly": self.session_cookie_httponly,
                "cookie_samesite": self.session_cookie_samesite,
                "expire_seconds": 86400,  # 24 hours
            },
            "csrf": {
                "enabled": self.csrf_protection_enabled,
                "cookie_secure": True,
                "cookie_httponly": True,
            },
            "headers": {
                "enabled": self.security_headers_enabled,
                "hsts": True,
                "hsts_max_age": 31536000,  # 1 year
                "content_security_policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
            },
            "authentication": {
                "jwt_expire_minutes": self.jwt_token_expire_minutes,
                "refresh_expire_days": self.refresh_token_expire_days,
                "algorithm": "RS256",
                "token_blacklist": True,
                "account_lockout": True,
            },
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get staging logging configuration."""
        return {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "handlers": ["console", "file", "syslog"],
            "disable_existing_loggers": False,
            "loggers": {
                "uvicorn": {"level": "INFO"},
                "uvicorn.access": {"level": "INFO"},
                "sqlalchemy.engine": {"level": "WARNING"},
                "fastapi": {"level": "INFO"},
                "craftyx": {"level": "INFO"},
                "celery": {"level": "INFO"},
            },
            "file_config": {
                "filename": "/var/log/craftyx/staging.log",
                "max_bytes": 104857600,  # 100MB
                "backup_count": 10,
                "rotation": "daily",
            },
            "syslog_config": {
                "address": "/dev/log",
                "facility": "local0",
            },
            "structured_logging": True,
            "log_requests": self.is_feature_enabled("enable_request_logging"),
        }
    
    def validate_configuration(self) -> bool:
        """Validate staging configuration."""
        super().validate_configuration()
        
        # Staging-specific validations
        if self.debug_mode:
            raise ValueError("debug_mode should be False in staging")
        
        if not self.session_cookie_secure:
            raise ValueError("session_cookie_secure must be True in staging")
        
        if "localhost" in self.cors_origins and len(self.cors_origins) > 1:
            print("Warning: localhost in CORS origins for staging environment")
        
        return True
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get staging performance configuration."""
        return {
            "connection_pooling": True,
            "query_optimization": True,
            "caching_strategy": "aggressive",
            "compression": True,
            "cdn_enabled": True,
            "static_file_caching": True,
            "database_query_cache": True,
            "api_response_cache": True,
        }
    
    def get_testing_config(self) -> Dict[str, Any]:
        """Get staging testing configuration."""
        return {
            "load_testing_enabled": self.is_feature_enabled("enable_load_testing"),
            "beta_features_enabled": self.is_feature_enabled("enable_beta_features"),
            "test_data_enabled": self.is_feature_enabled("enable_test_data"),
            "performance_monitoring": self.is_feature_enabled("enable_performance_monitoring"),
            "automated_testing": True,
            "test_coverage_tracking": True,
        }

# Global staging configuration instance
staging_config = StagingConfig() 