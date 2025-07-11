 

import os
import logging
from typing import Dict, Any, Optional

from config.loader import load_config, get_config, ConfigLoader
from config.secret_manager import setup_secret_providers, get_secret
from config.validator import validate_config, ValidationResult
from config.environments.base import BaseEnvironmentConfig

logger = logging.getLogger(__name__)


class Settings:
   
    
    def __init__(self):
        """Initialize settings."""
        self._config: Optional[BaseEnvironmentConfig] = None
        self._environment: str = os.getenv("ENVIRONMENT", "development")
        self._config_loaded: bool = False
    
    def load(
        self,
        environment: Optional[str] = None,
        config_file: Optional[str] = None,
        env_file: Optional[str] = None,
        secrets_file: Optional[str] = None,
        validate: bool = True
    ) -> None:
        """Load configuration from various sources.
        
        Args:
            environment: Target environment
            config_file: Path to configuration file
            env_file: Path to .env file
            secrets_file: Path to secrets file
            validate: Whether to validate configuration
        """
        if environment:
            self._environment = environment
        
        
        setup_secret_providers(
            environment=self._environment,
            secrets_dir=os.getenv("SECRETS_DIR"),
            aws_region=os.getenv("AWS_REGION"),
            vault_url=os.getenv("VAULT_URL"),
            vault_token=os.getenv("VAULT_TOKEN")
        )
        
       
        self._config = load_config(
            environment=environment,
            config_file=config_file,
            env_file=env_file,
            secrets_file=secrets_file,
            validate=validate
        )
        
        self._config_loaded = True
        logger.info(f"Configuration loaded for environment: {self._environment}")
    
    @property
    def config(self) -> BaseEnvironmentConfig:
        
        if not self._config_loaded or not self._config:
           
            try:
                # Look for .env file in parent directory (project root)
                import os
                from pathlib import Path
                current_dir = Path(__file__).parent.parent
                env_file_path = current_dir.parent / ".env"
                
                if env_file_path.exists():
                    self.load(env_file=str(env_file_path))
                else:
                    self.load()
            except Exception as e:
                raise RuntimeError(f"Configuration not loaded and auto-load failed: {e}")
        
        return self._config
    
    @property
    def environment(self) -> str:
       
        return self._environment
    
    @property
    def is_development(self) -> bool:
       
        return self._environment == "development"
    
    @property
    def is_staging(self) -> bool:
       
        return self._environment == "staging"
    
    @property
    def is_production(self) -> bool:
       
        return self._environment == "production"
    
    @property
    def debug(self) -> bool:
       
        return getattr(self.config, "debug", False)
    
    @property
    def secret_key(self) -> str:
       
        return getattr(self.config, "secret_key", "")
    
    @property
    def database_url(self) -> str:
       
        return getattr(self.config, "database_url", "")
    
    @property
    def redis_url(self) -> Optional[str]:
       
        return getattr(self.config, "redis_url", None)
    
    def get_database_config(self) -> Dict[str, Any]:
       
        if hasattr(self.config, "get_database_config"):
            return self.config.get_database_config()
        
        
        return {
            "url": self.database_url,
            "echo": self.debug,
            "pool_size": getattr(self.config, "database_pool_size", 5),
            "max_overflow": getattr(self.config, "database_max_overflow", 10),
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        
        if hasattr(self.config, "get_cache_config"):
            return self.config.get_cache_config()
        
        
        return {
            "backend": getattr(self.config, "cache_backend", "memory"),
            "location": self.redis_url,
            "options": {}
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        
        if hasattr(self.config, "get_security_config"):
            return self.config.get_security_config()
        
        
        return {
            "secret_key": self.secret_key,
            "algorithm": getattr(self.config, "jwt_algorithm", "HS256"),
            "access_token_expire_minutes": getattr(self.config, "jwt_access_token_expire_minutes", 15),
        }
    
    def get_email_config(self) -> Dict[str, Any]:
        
        if hasattr(self.config, "get_email_config"):
            return self.config.get_email_config()
        
        
        return {
            "backend": getattr(self.config, "email_backend", "console"),
            "host": getattr(self.config, "smtp_host", ""),
            "port": getattr(self.config, "smtp_port", 587),
            "username": getattr(self.config, "smtp_username", ""),
            "password": getattr(self.config, "smtp_password", ""),
            "use_tls": getattr(self.config, "smtp_use_tls", True),
        }
    
    def validate(self) -> ValidationResult:
        
        
        if not self._config:
            raise RuntimeError("Configuration not loaded")
        
        config_dict = self._config.dict()
        return validate_config(config_dict, self._environment)
    
    def reload(self, **kwargs) -> None:
        
        
        self._config = None
        self._config_loaded = False
        self.load(**kwargs)
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        
        
        return await get_secret(secret_name)
    
    def get_feature_flags(self) -> Dict[str, bool]:
        
        
        feature_flags = {}
        
        
        for attr_name in dir(self.config):
            if attr_name.startswith("enable_") and not attr_name.startswith("_"):
                try:
                    value = getattr(self.config, attr_name)
                    if isinstance(value, bool):
                        feature_flags[attr_name] = value
                except AttributeError:
                    continue
        
        return feature_flags
    
    def is_feature_enabled(self, feature_name: str) -> bool:

        
        if not feature_name.startswith("enable_"):
            feature_name = f"enable_{feature_name}"
        
        return getattr(self.config, feature_name, False)
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        
        if hasattr(self.config, "get_monitoring_config"):
            return self.config.get_monitoring_config()
        
        
        return {
            "sentry": {
                "dsn": getattr(self.config, "sentry_dsn", None),
                "environment": self._environment,
            },
            "metrics": {
                "enabled": getattr(self.config, "enable_metrics", False),
            },
            "logging": {
                "level": getattr(self.config, "log_level", "INFO"),
                "format": getattr(self.config, "log_format", "text"),
            }
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        
        return {
            "origins": getattr(self.config, "cors_origins", ["*"]),
            "methods": getattr(self.config, "cors_methods", ["GET", "POST", "PUT", "DELETE"]),
            "headers": getattr(self.config, "cors_headers", ["*"]),
            "credentials": getattr(self.config, "cors_allow_credentials", False),
        }
    
    def get_rate_limit_config(self) -> Dict[str, str]:
        
        return {
            "login": getattr(self.config, "rate_limit_login", "5/15minutes"),
            "api": getattr(self.config, "rate_limit_api", "1000/hour"),
            "registration": getattr(self.config, "rate_limit_registration", "3/hour"),
            "password_reset": getattr(self.config, "rate_limit_password_reset", "3/hour"),
        }
    
    def get_file_upload_config(self) -> Dict[str, Any]:
        
        return {
            "max_size": getattr(self.config, "max_upload_size", 5_242_880), 
            "upload_path": getattr(self.config, "upload_path", "/tmp/uploads"),
            "allowed_extensions": getattr(self.config, "allowed_file_extensions", [
                ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"
            ]),
            "use_cdn": getattr(self.config, "use_cdn", False),
            "cdn_url": getattr(self.config, "cdn_url", None),
        }



settings = Settings()



def get_settings() -> Settings:
    
    return settings


def load_settings(**kwargs) -> None:
    
    settings.load(**kwargs)


def get_database_config() -> Dict[str, Any]:
    
    return settings.get_database_config()


def get_cache_config() -> Dict[str, Any]:
    
    return settings.get_cache_config()


def get_security_config() -> Dict[str, Any]:

    return settings.get_security_config()


def is_development() -> bool:
    
    return settings.is_development


def is_production() -> bool:
    
    return settings.is_production


def is_feature_enabled(feature_name: str) -> bool:
    
    return settings.is_feature_enabled(feature_name)


    
if os.getenv("AUTO_LOAD_CONFIG", "").lower() in ("true", "1", "yes"):
    try:
        settings.load()
        logger.info("Configuration auto-loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to auto-load configuration: {e}") 