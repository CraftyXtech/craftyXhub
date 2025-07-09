from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from enum import Enum
import os

class CacheBackend(str, Enum):
    REDIS = "redis"
    MEMORY = "memory"
    MEMCACHED = "memcached"
    DUMMY = "dummy"

class CacheConfig(BaseSettings):
    """Cache configuration settings."""
    
    # Cache Backend
    CACHE_BACKEND: CacheBackend = Field(default=CacheBackend.REDIS, env="CACHE_BACKEND")
    CACHE_URL: Optional[str] = Field(default=None, env="CACHE_URL")
    
    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_USERNAME: Optional[str] = Field(default=None, env="REDIS_USERNAME")
    
    # Redis Connection Pool
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="REDIS_HEALTH_CHECK_INTERVAL")
    
    # Redis SSL Configuration
    REDIS_SSL: bool = Field(default=False, env="REDIS_SSL")
    REDIS_SSL_CERT_REQS: str = Field(default="required", env="REDIS_SSL_CERT_REQS")
    REDIS_SSL_CA_CERTS: Optional[str] = Field(default=None, env="REDIS_SSL_CA_CERTS")
    REDIS_SSL_CERTFILE: Optional[str] = Field(default=None, env="REDIS_SSL_CERTFILE")
    REDIS_SSL_KEYFILE: Optional[str] = Field(default=None, env="REDIS_SSL_KEYFILE")
    
    # Timeout Settings
    REDIS_SOCKET_TIMEOUT: float = Field(default=5.0, env="REDIS_SOCKET_TIMEOUT")
    REDIS_SOCKET_CONNECT_TIMEOUT: float = Field(default=5.0, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    REDIS_CONNECTION_TIMEOUT: float = Field(default=5.0, env="REDIS_CONNECTION_TIMEOUT")
    
    # TTL Settings (in seconds)
    CACHE_DEFAULT_TTL: int = Field(default=3600, env="CACHE_DEFAULT_TTL")  # 1 hour
    CACHE_SESSION_TTL: int = Field(default=86400, env="CACHE_SESSION_TTL")  # 24 hours
    CACHE_USER_TTL: int = Field(default=1800, env="CACHE_USER_TTL")  # 30 minutes
    CACHE_POST_TTL: int = Field(default=3600, env="CACHE_POST_TTL")  # 1 hour
    CACHE_CATEGORY_TTL: int = Field(default=7200, env="CACHE_CATEGORY_TTL")  # 2 hours
    CACHE_TAG_TTL: int = Field(default=7200, env="CACHE_TAG_TTL")  # 2 hours
    CACHE_SEARCH_TTL: int = Field(default=900, env="CACHE_SEARCH_TTL")  # 15 minutes
    
    # Cache Key Prefixes
    CACHE_KEY_PREFIX: str = Field(default="craftyx", env="CACHE_KEY_PREFIX")
    CACHE_SESSION_PREFIX: str = Field(default="session", env="CACHE_SESSION_PREFIX")
    CACHE_USER_PREFIX: str = Field(default="user", env="CACHE_USER_PREFIX")
    CACHE_POST_PREFIX: str = Field(default="post", env="CACHE_POST_PREFIX")
    CACHE_RATE_LIMIT_PREFIX: str = Field(default="ratelimit", env="CACHE_RATE_LIMIT_PREFIX")
    
    # Serialization
    CACHE_SERIALIZER: str = Field(default="json", env="CACHE_SERIALIZER")
    CACHE_COMPRESSION: bool = Field(default=True, env="CACHE_COMPRESSION")
    CACHE_COMPRESSION_LEVEL: int = Field(default=6, env="CACHE_COMPRESSION_LEVEL")
    
    # Memory Cache Settings (for in-memory backend)
    MEMORY_CACHE_MAX_SIZE: int = Field(default=1000, env="MEMORY_CACHE_MAX_SIZE")
    MEMORY_CACHE_TTL: int = Field(default=3600, env="MEMORY_CACHE_TTL")
    
    # Performance Settings
    CACHE_MAX_KEY_LENGTH: int = Field(default=250, env="CACHE_MAX_KEY_LENGTH")
    CACHE_MAX_VALUE_SIZE: int = Field(default=1048576, env="CACHE_MAX_VALUE_SIZE")  # 1MB
    CACHE_BATCH_SIZE: int = Field(default=100, env="CACHE_BATCH_SIZE")
    
    # Cache Strategy
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_WRITE_THROUGH: bool = Field(default=False, env="CACHE_WRITE_THROUGH")
    CACHE_WRITE_BEHIND: bool = Field(default=False, env="CACHE_WRITE_BEHIND")
    CACHE_READ_FROM_REPLICA: bool = Field(default=False, env="CACHE_READ_FROM_REPLICA")
    
    # Eviction and Cleanup
    CACHE_EVICTION_POLICY: str = Field(default="lru", env="CACHE_EVICTION_POLICY")
    CACHE_CLEANUP_INTERVAL: int = Field(default=300, env="CACHE_CLEANUP_INTERVAL")  # 5 minutes
    CACHE_MAX_MEMORY_USAGE: Optional[str] = Field(default=None, env="CACHE_MAX_MEMORY_USAGE")
    
    @field_validator("CACHE_URL", mode="before")
    @classmethod
    def build_cache_url(cls, v, info):
        if v:
            return v
        
        values = info.data if hasattr(info, 'data') else {}
        backend = values.get("CACHE_BACKEND", CacheBackend.REDIS)
        
        if backend == CacheBackend.REDIS:
            host = values.get("REDIS_HOST", "localhost")
            port = values.get("REDIS_PORT", 6379)
            db = values.get("REDIS_DB", 0)
            password = values.get("REDIS_PASSWORD")
            username = values.get("REDIS_USERNAME")
            
            # Build Redis URL
            if username and password:
                auth = f"{username}:{password}"
            elif password:
                auth = f":{password}"
            else:
                auth = ""
            
            auth_part = f"{auth}@" if auth else ""
            return f"redis://{auth_part}{host}:{port}/{db}"
        
        elif backend == CacheBackend.MEMORY:
            return "memory://"
        
        elif backend == CacheBackend.DUMMY:
            return "dummy://"
        
        return v
    
    @field_validator("CACHE_SERIALIZER")
    @classmethod
    def validate_serializer(cls, v):
        valid_serializers = ["json", "pickle", "msgpack"]
        if v not in valid_serializers:
            raise ValueError(f"CACHE_SERIALIZER must be one of: {valid_serializers}")
        return v
    
    @field_validator("CACHE_EVICTION_POLICY")
    @classmethod
    def validate_eviction_policy(cls, v):
        valid_policies = ["lru", "lfu", "fifo", "random"]
        if v not in valid_policies:
            raise ValueError(f"CACHE_EVICTION_POLICY must be one of: {valid_policies}")
        return v
    
    @field_validator("REDIS_SSL_CERT_REQS")
    @classmethod
    def validate_ssl_cert_reqs(cls, v):
        valid_reqs = ["none", "optional", "required"]
        if v not in valid_reqs:
            raise ValueError(f"REDIS_SSL_CERT_REQS must be one of: {valid_reqs}")
        return v
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis client configuration."""
        config = {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD,
            "username": self.REDIS_USERNAME,
            "socket_timeout": self.REDIS_SOCKET_TIMEOUT,
            "socket_connect_timeout": self.REDIS_SOCKET_CONNECT_TIMEOUT,
            "connection_pool_kwargs": {
                "max_connections": self.REDIS_MAX_CONNECTIONS,
                "retry_on_timeout": self.REDIS_RETRY_ON_TIMEOUT,
                "health_check_interval": self.REDIS_HEALTH_CHECK_INTERVAL,
            }
        }
        
        # Add SSL configuration if enabled
        if self.REDIS_SSL:
            config.update({
                "ssl": True,
                "ssl_cert_reqs": self.REDIS_SSL_CERT_REQS,
                "ssl_ca_certs": self.REDIS_SSL_CA_CERTS,
                "ssl_certfile": self.REDIS_SSL_CERTFILE,
                "ssl_keyfile": self.REDIS_SSL_KEYFILE,
            })
        
        return config
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key with prefix and arguments."""
        key_parts = [self.CACHE_KEY_PREFIX, prefix] + [str(arg) for arg in args]
        key = ":".join(key_parts)
        
        # Truncate key if too long
        if len(key) > self.CACHE_MAX_KEY_LENGTH:
            import hashlib
            hash_suffix = hashlib.md5(key.encode()).hexdigest()[:8]
            max_prefix_len = self.CACHE_MAX_KEY_LENGTH - len(hash_suffix) - 1
            key = key[:max_prefix_len] + ":" + hash_suffix
        
        return key
    
    def get_ttl_for_type(self, cache_type: str) -> int:
        """Get TTL for specific cache type."""
        ttl_mapping = {
            "session": self.CACHE_SESSION_TTL,
            "user": self.CACHE_USER_TTL,
            "post": self.CACHE_POST_TTL,
            "category": self.CACHE_CATEGORY_TTL,
            "tag": self.CACHE_TAG_TTL,
            "search": self.CACHE_SEARCH_TTL,
        }
        return ttl_mapping.get(cache_type, self.CACHE_DEFAULT_TTL)
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.CACHE_ENABLED and self.CACHE_BACKEND != CacheBackend.DUMMY
    
    model_config = {
        "env_file": "../.env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global cache configuration instance
cache_config = CacheConfig() 