from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
from enum import Enum
import os

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    """Base configuration class with common settings."""
    
    # Application Settings
    APP_NAME: str = Field(default="CraftyXhub", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, env="APP_ENV")
    DEBUG: bool = Field(default=False, env="APP_DEBUG")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=False, env="RELOAD")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Application URLs
    APP_URL: str = Field(default="http://localhost:8000", env="APP_URL")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Security Settings
    SECRET_KEY: str = Field(default="dev-secret-key-change-me-please-1234567890", env="SECRET_KEY")
    ALGORITHM: str = Field(default="RS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    TOKEN_ISSUER: str = Field(default="craftyhub", env="TOKEN_ISSUER")
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    CIPHER_ALGORITHM: str = Field(default="AES-256-CBC", env="CIPHER_ALGORITHM")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    LOGIN_RATE_LIMIT: str = Field(default="5/15minutes", env="LOGIN_RATE_LIMIT")
    API_RATE_LIMIT: str = Field(default="100/minute", env="API_RATE_LIMIT")
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_PATH: str = Field(default="uploads", env="UPLOAD_PATH")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_ROTATION: str = Field(default="1 day", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", env="LOG_RETENTION")
    
    # Timezone and Localization
    TIMEZONE: str = Field(default="UTC", env="TIMEZONE")
    LOCALE: str = Field(default="en", env="APP_LOCALE")
    FALLBACK_LOCALE: str = Field(default="en", env="APP_FALLBACK_LOCALE")
    
    # Performance Settings
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    MAX_CONNECTIONS: int = Field(default=100, env="MAX_CONNECTIONS")
    KEEPALIVE_TIMEOUT: int = Field(default=5, env="KEEPALIVE_TIMEOUT")
    
    # Maintenance Mode
    MAINTENANCE_MODE: bool = Field(default=False, env="MAINTENANCE_MODE")
    MAINTENANCE_MESSAGE: str = Field(
        default="Application is under maintenance",
        env="MAINTENANCE_MESSAGE"
    )
    
    # Feature Flags
    ENABLE_REGISTRATION: bool = Field(default=True, env="ENABLE_REGISTRATION")
    ENABLE_EMAIL_VERIFICATION: bool = Field(default=True, env="ENABLE_EMAIL_VERIFICATION")
    ENABLE_PASSWORD_RESET: bool = Field(default=True, env="ENABLE_PASSWORD_RESET")
    ENABLE_COMMENTS: bool = Field(default=True, env="ENABLE_COMMENTS")
    ENABLE_LIKES: bool = Field(default=True, env="ENABLE_LIKES")
    ENABLE_BOOKMARKS: bool = Field(default=True, env="ENABLE_BOOKMARKS")
    
    # Monitoring and Health
    HEALTH_CHECK_ENABLED: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    TRACING_ENABLED: bool = Field(default=False, env="TRACING_ENABLED")
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("APP_URL", "FRONTEND_URL")
    def validate_urls(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URLs must start with http:// or https://")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in Environment:
            raise ValueError(f"ENVIRONMENT must be one of: {list(Environment)}")
        return v
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT == Environment.STAGING
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == Environment.TESTING
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
        extra = "ignore"

# Global settings instance
settings = BaseConfig() 