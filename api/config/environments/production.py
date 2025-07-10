"""
Production Environment Configuration

This module provides production-specific configuration settings for CraftyXhub.
All settings are optimized for security, performance, and reliability in production.
"""

from typing import Dict, Any, Optional
from pydantic import Field, validator

from .base import BaseEnvironmentConfig


class ProductionConfig(BaseEnvironmentConfig):
    """Production environment configuration with maximum security and performance."""
    
    # Environment identification
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security settings - maximum security for production
    secret_key: str = Field(..., env="SECRET_KEY", min_length=32)
    allowed_hosts: list[str] = Field(
        default=["craftyhub.com", "www.craftyhub.com", "api.craftyhub.com"],
        env="ALLOWED_HOSTS"
    )
    cors_origins: list[str] = Field(
        default=["https://craftyhub.com", "https://www.craftyhub.com"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Database settings - production database with SSL
    database_url: str = Field(..., env="DATABASE_URL")
    database_ssl_mode: str = Field(default="require", env="DATABASE_SSL_MODE")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=40, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Cache settings - Redis cluster for production
    cache_backend: str = Field(default="redis", env="CACHE_BACKEND")
    redis_url: str = Field(..., env="REDIS_URL")
    redis_ssl: bool = Field(default=True, env="REDIS_SSL")
    redis_ssl_cert_reqs: str = Field(default="required", env="REDIS_SSL_CERT_REQS")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_cluster_mode: bool = Field(default=True, env="REDIS_CLUSTER_MODE")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    
    # JWT settings - production security
    jwt_algorithm: str = Field(default="RS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    jwt_private_key: str = Field(..., env="JWT_PRIVATE_KEY")
    jwt_public_key: str = Field(..., env="JWT_PUBLIC_KEY")
    jwt_issuer: str = Field(default="craftyhub", env="JWT_ISSUER")
    
    # Rate limiting - strict production limits
    rate_limit_login: str = Field(default="5/15minutes", env="RATE_LIMIT_LOGIN")
    rate_limit_api: str = Field(default="1000/hour", env="RATE_LIMIT_API")
    rate_limit_registration: str = Field(default="3/hour", env="RATE_LIMIT_REGISTRATION")
    rate_limit_password_reset: str = Field(default="3/hour", env="RATE_LIMIT_PASSWORD_RESET")
    
    # Email settings - production email service
    email_backend: str = Field(default="smtp", env="EMAIL_BACKEND")
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(..., env="SMTP_USERNAME")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    smtp_use_ssl: bool = Field(default=False, env="SMTP_USE_SSL")
    default_from_email: str = Field(default="noreply@craftyhub.com", env="DEFAULT_FROM_EMAIL")
    
    # File upload settings - CDN integration
    max_upload_size: int = Field(default=10_485_760, env="MAX_UPLOAD_SIZE")  # 10MB
    upload_path: str = Field(default="/var/uploads/craftyhub", env="UPLOAD_PATH")
    use_cdn: bool = Field(default=True, env="USE_CDN")
    cdn_url: Optional[str] = Field(default=None, env="CDN_URL")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Logging settings - comprehensive production logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default="/var/log/craftyhub/app.log", env="LOG_FILE")
    log_max_size: int = Field(default=100_000_000, env="LOG_MAX_SIZE")  # 100MB
    log_backup_count: int = Field(default=10, env="LOG_BACKUP_COUNT")
    log_rotation: str = Field(default="daily", env="LOG_ROTATION")
    
    # Monitoring and observability
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    enable_profiling: bool = Field(default=True, env="ENABLE_PROFILING")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="production", env="SENTRY_ENVIRONMENT")
    sentry_sample_rate: float = Field(default=0.1, env="SENTRY_SAMPLE_RATE")
    
    # Performance settings
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    worker_connections: int = Field(default=1000, env="WORKER_CONNECTIONS")
    keepalive_timeout: int = Field(default=65, env="KEEPALIVE_TIMEOUT")
    max_requests: int = Field(default=1000, env="MAX_REQUESTS")
    max_requests_jitter: int = Field(default=50, env="MAX_REQUESTS_JITTER")
    
    # Security headers and policies
    enable_security_headers: bool = Field(default=True, env="ENABLE_SECURITY_HEADERS")
    content_security_policy: str = Field(
        default="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        env="CONTENT_SECURITY_POLICY"
    )
    x_frame_options: str = Field(default="DENY", env="X_FRAME_OPTIONS")
    x_content_type_options: str = Field(default="nosniff", env="X_CONTENT_TYPE_OPTIONS")
    
    # Feature flags - production features
    enable_ai_features: bool = Field(default=True, env="ENABLE_AI_FEATURES")
    enable_social_features: bool = Field(default=True, env="ENABLE_SOCIAL_FEATURES")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_search: bool = Field(default=True, env="ENABLE_SEARCH")
    enable_recommendations: bool = Field(default=True, env="ENABLE_RECOMMENDATIONS")
    enable_push_notifications: bool = Field(default=True, env="ENABLE_PUSH_NOTIFICATIONS")
    
    # Background job settings
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    celery_worker_concurrency: int = Field(default=4, env="CELERY_WORKER_CONCURRENCY")
    celery_task_routes: Dict[str, str] = Field(
        default={
            "email.*": "email",
            "ai.*": "ai",
            "search.*": "search",
            "analytics.*": "analytics"
        },
        env="CELERY_TASK_ROUTES"
    )
    
    # External service integrations
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_analytics_id: Optional[str] = Field(default=None, env="GOOGLE_ANALYTICS_ID")
    stripe_api_key: Optional[str] = Field(default=None, env="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Health check settings
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    
    # Backup and maintenance
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    maintenance_mode: bool = Field(default=False, env="MAINTENANCE_MODE")
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL for production."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Production must use PostgreSQL database")
        if "localhost" in v or "127.0.0.1" in v:
            raise ValueError("Production database cannot use localhost")
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v):
        """Validate Redis URL for production."""
        if "localhost" in v or "127.0.0.1" in v:
            raise ValueError("Production Redis cannot use localhost")
        return v
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v):
        """Validate CORS origins for production."""
        for origin in v:
            if not origin.startswith("https://"):
                raise ValueError("Production CORS origins must use HTTPS")
        return v
    
    @validator("secret_key")
    def validate_secret_key_strength(cls, v):
        """Validate secret key strength for production."""
        if len(v) < 64:
            raise ValueError("Production secret key must be at least 64 characters")
        return v
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get production database configuration."""
        return {
            "url": self.database_url,
            "echo": False,  # No SQL logging in production
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,
            "pool_pre_ping": True,
            "connect_args": {
                "sslmode": self.database_ssl_mode,
                "sslcert": "/etc/ssl/certs/client-cert.pem",
                "sslkey": "/etc/ssl/private/client-key.pem",
                "sslrootcert": "/etc/ssl/certs/ca-cert.pem",
            }
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get production cache configuration."""
        return {
            "backend": self.cache_backend,
            "location": self.redis_url,
            "options": {
                "ssl": self.redis_ssl,
                "ssl_cert_reqs": self.redis_ssl_cert_reqs,
                "password": self.redis_password,
                "max_connections": self.redis_max_connections,
                "health_check_interval": 30,
                "socket_keepalive": True,
                "socket_keepalive_options": {},
                "retry_on_timeout": True,
                "decode_responses": True,
            }
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get production security configuration."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.jwt_access_token_expire_minutes,
            "refresh_token_expire_days": self.jwt_refresh_token_expire_days,
            "private_key": self.jwt_private_key,
            "public_key": self.jwt_public_key,
            "issuer": self.jwt_issuer,
            "security_headers": {
                "X-Content-Type-Options": self.x_content_type_options,
                "X-Frame-Options": self.x_frame_options,
                "Content-Security-Policy": self.content_security_policy,
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get production monitoring configuration."""
        return {
            "sentry": {
                "dsn": self.sentry_dsn,
                "environment": self.sentry_environment,
                "sample_rate": self.sentry_sample_rate,
                "traces_sample_rate": 0.1,
                "profiles_sample_rate": 0.1,
            },
            "metrics": {
                "enabled": self.enable_metrics,
                "prometheus_port": 9090,
                "health_check_port": 8080,
            },
            "logging": {
                "level": self.log_level,
                "format": self.log_format,
                "file": self.log_file,
                "max_size": self.log_max_size,
                "backup_count": self.log_backup_count,
                "rotation": self.log_rotation,
            }
        }
    
    def is_production_ready(self) -> bool:
        """Check if configuration is production ready."""
        required_vars = [
            self.secret_key,
            self.database_url,
            self.redis_url,
            self.jwt_private_key,
            self.jwt_public_key,
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
        ]
        
        return all(var for var in required_vars) and not self.debug
    
    class Config:
        env_file = "../../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True 