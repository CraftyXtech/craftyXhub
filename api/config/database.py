from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os

class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    # Primary Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:root@localhost:5432/xhub", env="DATABASE_URL")
    DB_DRIVER: str = Field(default="postgresql+asyncpg", env="DB_DRIVER")
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_NAME: str = Field(default="xhub", env="DB_NAME")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="root", env="DB_PASSWORD")
    
    # Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=0, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    DB_POOL_PRE_PING: bool = Field(default=True, env="DB_POOL_PRE_PING")
    
    # Connection Settings
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    DB_ECHO_POOL: bool = Field(default=False, env="DB_ECHO_POOL")
    DB_CONNECT_TIMEOUT: int = Field(default=10, env="DB_CONNECT_TIMEOUT")
    DB_COMMAND_TIMEOUT: int = Field(default=30, env="DB_COMMAND_TIMEOUT")
    
    # SSL Settings
    DB_SSL_MODE: str = Field(default="prefer", env="DB_SSL_MODE")
    DB_SSL_CERT: Optional[str] = Field(default=None, env="DB_SSL_CERT")
    DB_SSL_KEY: Optional[str] = Field(default=None, env="DB_SSL_KEY")
    DB_SSL_CA: Optional[str] = Field(default=None, env="DB_SSL_CA")
    DB_SSL_CHECK_HOSTNAME: bool = Field(default=True, env="DB_SSL_CHECK_HOSTNAME")
    
    # Read Replica Configuration
    READ_REPLICA_URL: Optional[str] = Field(default=None, env="READ_REPLICA_URL")
    READ_REPLICA_ENABLED: bool = Field(default=False, env="READ_REPLICA_ENABLED")
    READ_REPLICA_POOL_SIZE: int = Field(default=10, env="READ_REPLICA_POOL_SIZE")
    
    # Migration Settings
    MIGRATION_TABLE: str = Field(default="alembic_version", env="MIGRATION_TABLE")
    AUTO_MIGRATE: bool = Field(default=False, env="AUTO_MIGRATE")
    MIGRATION_TIMEOUT: int = Field(default=300, env="MIGRATION_TIMEOUT")
    
    # Performance Settings
    DB_STATEMENT_CACHE_SIZE: int = Field(default=100, env="DB_STATEMENT_CACHE_SIZE")
    DB_PREPARED_STATEMENT_CACHE_SIZE: int = Field(default=100, env="DB_PREPARED_STATEMENT_CACHE_SIZE")
    
    # Backup and Maintenance
    BACKUP_ENABLED: bool = Field(default=False, env="BACKUP_ENABLED")
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    VACUUM_ENABLED: bool = Field(default=True, env="VACUUM_ENABLED")
    ANALYZE_ENABLED: bool = Field(default=True, env="ANALYZE_ENABLED")
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v, info):
        if v and v != "":
            return v
        
        # Build URL from components if DATABASE_URL not provided
        values = info.data if hasattr(info, 'data') else {}
        driver = values.get("DB_DRIVER", "postgresql+asyncpg")
        user = values.get("DB_USER", "postgres")
        password = values.get("DB_PASSWORD", "root")
        host = values.get("DB_HOST", "localhost")
        port = values.get("DB_PORT", 5432)
        database = values.get("DB_NAME", "xhub")
        
        return f"{driver}://{user}:{password}@{host}:{port}/{database}"
    
    @field_validator("DB_SSL_MODE")
    @classmethod
    def validate_ssl_mode(cls, v):
        valid_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if v not in valid_modes:
            raise ValueError(f"DB_SSL_MODE must be one of: {valid_modes}")
        return v
    
    @field_validator("DB_POOL_SIZE", "DB_MAX_OVERFLOW", "READ_REPLICA_POOL_SIZE")
    @classmethod
    def validate_positive_integers(cls, v):
        if v < 0:
            raise ValueError("Pool size values must be non-negative")
        return v
    
    @field_validator("DB_POOL_TIMEOUT", "DB_POOL_RECYCLE", "DB_CONNECT_TIMEOUT", "DB_COMMAND_TIMEOUT")
    @classmethod
    def validate_timeout_values(cls, v):
        if v <= 0:
            raise ValueError("Timeout values must be positive")
        return v
    
    def get_engine_config(self) -> Dict[str, Any]:
        """Get SQLAlchemy engine configuration."""
        config = {
            "url": self.DATABASE_URL,
            "echo": self.DB_ECHO,
            "echo_pool": self.DB_ECHO_POOL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "pool_pre_ping": self.DB_POOL_PRE_PING,
        }
        
        # Add SSL configuration if specified
        if self.DB_SSL_MODE != "disable":
            ssl_config = {"sslmode": self.DB_SSL_MODE}
            
            if self.DB_SSL_CERT:
                ssl_config["sslcert"] = self.DB_SSL_CERT
            if self.DB_SSL_KEY:
                ssl_config["sslkey"] = self.DB_SSL_KEY
            if self.DB_SSL_CA:
                ssl_config["sslrootcert"] = self.DB_SSL_CA
            
            config["connect_args"] = ssl_config
        
        return config
    
    def get_read_replica_config(self) -> Optional[Dict[str, Any]]:
        """Get read replica configuration if enabled."""
        if not self.READ_REPLICA_ENABLED or not self.READ_REPLICA_URL:
            return None
        
        return {
            "url": self.READ_REPLICA_URL,
            "echo": self.DB_ECHO,
            "pool_size": self.READ_REPLICA_POOL_SIZE,
            "max_overflow": 0,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "pool_pre_ping": True,
        }
    
    def get_alembic_config(self) -> Dict[str, Any]:
        """Get Alembic migration configuration."""
        return {
            "script_location": "alembic",
            "sqlalchemy.url": self.DATABASE_URL,
            "version_table": self.MIGRATION_TABLE,
            "compare_type": True,
            "compare_server_default": True,
            "render_as_batch": True,
        }
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global database configuration instance
database_config = DatabaseConfig() 