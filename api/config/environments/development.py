from typing import Dict, Any, List
from .base import BaseEnvironmentConfig, EnvironmentType

class DevelopmentConfig(BaseEnvironmentConfig):
    """Development environment configuration."""
    
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    environment_name: str = "development"
    
    # Development-specific settings
    debug_mode: bool = True
    log_level: str = "DEBUG"
    enable_tracing: bool = True
    enable_profiling: bool = True
    hot_reload: bool = True
    auto_migration: bool = True
    
    # Development database
    use_local_database: bool = True
    database_echo: bool = False  # SQL logging disabled
    database_reset_on_start: bool = False
    seed_data_on_start: bool = True
    
    # Development cache
    cache_enabled: bool = True
    cache_default_ttl: int = 60  # Short TTL for development
    cache_max_memory: str = "100MB"
    
    # Development security (relaxed)
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"]
    rate_limiting_enabled: bool = False
    session_cookie_secure: bool = False
    csrf_protection_enabled: bool = False
    
    # Development email
    email_development_mode: bool = True
    email_queue_enabled: bool = False  # Send immediately in dev
    email_rate_limit_enabled: bool = False
    
    # Development features
    feature_flags: Dict[str, bool] = {
        "enable_debug_toolbar": True,
        "enable_mock_services": True,
        "enable_test_data": True,
        "skip_email_verification": True,
        "enable_sql_logging": True,
        "enable_request_logging": True,
        "enable_performance_monitoring": True,
        "enable_hot_reload": True,
    }
    
    # Development monitoring
    monitoring_enabled: bool = True
    alerting_enabled: bool = False
    error_tracking_enabled: bool = False
    
    # Development file handling
    max_file_size: int = 52428800  # 50MB for development
    file_storage_backend: str = "local"
    
    # Development API settings
    api_rate_limit: str = "1000/minute"  # Very generous for development
    api_pagination_default_size: int = 10
    api_pagination_max_size: int = 50
    
    # Development job queue
    job_queue_enabled: bool = True
    job_retry_attempts: int = 1  # Quick failure for development
    job_retry_delay: int = 5
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get development database configuration."""
        return {
            "url": "postgresql+asyncpg://morvin:Babyna3***.@localhost:5432/xhub" if self.use_local_database else None,
            "echo": self.database_echo,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_pre_ping": True,  # Validate connections before use
            "connect_args": {},
            "reset_on_start": self.database_reset_on_start,
            "seed_data": self.seed_data_on_start,
            "auto_migrate": self.auto_migration,
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get development cache configuration."""
        return {
            "enabled": self.cache_enabled,
            "backend": "memory",  # Simple in-memory cache for development
            "url": "memory://",
            "default_ttl": self.cache_default_ttl,
            "max_memory": self.cache_max_memory,
            "key_prefix": "dev_craftyx",
            "serializer": "json",
            "compression": False,  # No compression in development
        }
    
    def get_external_services(self) -> Dict[str, Any]:
        """Get development external service configurations."""
        return {
            "email": {
                "enabled": True,
                "backend": "console",  # Print emails to console
                "development_mode": self.email_development_mode,
                "queue_enabled": self.email_queue_enabled,
                "file_path": "./dev_emails/",
            },
            "ai": {
                "enabled": False,  # Disabled by default in development
                "mock_responses": True,
                "content_generation": False,
                "image_generation": False,
                "embedding_generation": False,
            },
            "storage": {
                "enabled": True,
                "backend": "local",
                "upload_path": "./dev_uploads/",
                "max_size": self.max_file_size,
            },
            "search": {
                "enabled": False,  # Use simple database search in development
                "backend": "database",
            },
            "analytics": {
                "enabled": False,  # No analytics in development
            },
            "error_tracking": {
                "enabled": self.error_tracking_enabled,
                "sample_rate": 1.0,  # Track all errors in development
            },
            "cdn": {
                "enabled": False,  # No CDN in development
            },
            "push_notifications": {
                "enabled": False,  # No push notifications in development
            },
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get development security configuration."""
        return {
            "secret_key": "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
            "cors": {
                "enabled": self.cors_enabled,
                "origins": self.cors_origins,
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
            "rate_limiting": {
                "enabled": self.rate_limiting_enabled,
                "api_limit": self.api_rate_limit,
                "login_limit": "100/minute",  # Very relaxed in development
                "register_limit": "50/minute",
            },
            "session": {
                "cookie_secure": self.session_cookie_secure,
                "cookie_httponly": self.session_cookie_httponly,
                "cookie_samesite": self.session_cookie_samesite,
                "expire_seconds": 86400,
            },
            "csrf": {
                "enabled": self.csrf_protection_enabled,
            },
            "headers": {
                "enabled": False,  # Relaxed security headers in development
                "hsts": False,
                "content_security_policy": None,
            },
            "authentication": {
                "jwt_expire_minutes": 60,  # Longer token expiry in development
                "refresh_expire_days": 30,
                "algorithm": "HS256",  # Simpler algorithm for development
            },
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get development logging configuration."""
        return {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            "handlers": ["console", "file"],
            "disable_existing_loggers": False,
            "loggers": {
                "uvicorn": {"level": "WARNING"},
                "sqlalchemy.engine": {"level": "WARNING"},
                "sqlalchemy.pool": {"level": "WARNING"},
                "fastapi": {"level": "WARNING"},
                "craftyx": {"level": "WARNING"},
            },
            "file_config": {
                "filename": "./logs/development.log",
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5,
            }
        }
    
    def validate_configuration(self) -> bool:
        """Validate development configuration."""
        super().validate_configuration()
        
        # Development-specific validations
        if not self.debug_mode:
            raise ValueError("debug_mode should be True in development")
        
        if self.session_cookie_secure:
            print("Warning: session_cookie_secure is True in development - may cause issues with HTTP")
        
        return True
    
    def get_development_tools_config(self) -> Dict[str, Any]:
        """Get development tools configuration."""
        return {
            "debug_toolbar": self.is_feature_enabled("enable_debug_toolbar"),
            "sql_logging": self.is_feature_enabled("enable_sql_logging"),
            "request_logging": self.is_feature_enabled("enable_request_logging"),
            "performance_monitoring": self.is_feature_enabled("enable_performance_monitoring"),
            "hot_reload": self.is_feature_enabled("enable_hot_reload"),
            "mock_services": self.is_feature_enabled("enable_mock_services"),
            "test_data": self.is_feature_enabled("enable_test_data"),
        }

# Global development configuration instance  
development_config = DevelopmentConfig() 