import os
import json
import logging
from typing import Dict, Any, Optional, Union, Type
from pathlib import Path

from pydantic import ValidationError
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from .environments.base import BaseEnvironmentConfig
from .environments.development import DevelopmentConfig
from .environments.staging import StagingConfig
from .environments.production import ProductionConfig


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


class ConfigLoader:
    
    ENVIRONMENT_CONFIGS = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
    }
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self._config: Optional[BaseEnvironmentConfig] = None
        self._config_sources: Dict[str, Any] = {}
    
    def load_config(
        self,
        config_file: Optional[str] = None,
        env_file: Optional[str] = None,
        secrets_file: Optional[str] = None,
        validate: bool = True
    ) -> BaseEnvironmentConfig:
      
        try:
            config_class = self._get_config_class()
            
            config_data = {}
            
        
            if config_file:
                config_data.update(self._load_config_file(config_file))
                self._config_sources["config_file"] = config_file
            
            if env_file:
                config_data.update(self._load_env_file(env_file))
                self._config_sources["env_file"] = env_file
            
            if secrets_file:
                config_data.update(self._load_secrets_file(secrets_file))
                self._config_sources["secrets_file"] = secrets_file
            
            config_data.update(self._load_environment_variables())
            self._config_sources["environment"] = True
            
            if config_data:
                self._config = config_class(**config_data)
            else:
                self._config = config_class()
            
            if validate:
                self._validate_config()
            
            logger.info(
                f"Configuration loaded successfully for environment: {self.environment}",
                extra={"sources": list(self._config_sources.keys())}
            )
            
            return self._config
            
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e
    
    def get_config(self) -> BaseEnvironmentConfig:
        
        if self._config is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        return self._config
    
    def reload_config(self, **kwargs) -> BaseEnvironmentConfig:
        self._config = None
        self._config_sources.clear()
        return self.load_config(**kwargs)
    
    def _get_config_class(self) -> Type[BaseEnvironmentConfig]:
        if self.environment not in self.ENVIRONMENT_CONFIGS:
            raise ConfigurationError(
                f"Unsupported environment: {self.environment}. "
                f"Available: {list(self.ENVIRONMENT_CONFIGS.keys())}"
            )
        return self.ENVIRONMENT_CONFIGS[self.environment]
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        config_path = Path(config_file)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_file}")
            return {}
        
        try:
            with config_path.open("r", encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yml", ".yaml"]:
                    import yaml
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if isinstance(data, dict) and self.environment in data:
                data = data[self.environment]
            
            logger.debug(f"Loaded config from file: {config_file}")
            return data or {}
            
        except Exception as e:
            logger.error(f"Failed to load config file {config_file}: {e}")
            return {}
    
    def _load_env_file(self, env_file: str) -> Dict[str, Any]:
        env_path = Path(env_file)
        if not env_path.exists():
            logger.warning(f"Env file not found: {env_file}")
            return {}
        
        try:
            from dotenv import dotenv_values
            env_data = dotenv_values(env_file)
            
            converted_data = {}
            for key, value in env_data.items():
                if value is not None:
                    converted_data[key.lower()] = self._convert_env_value(value)
            
            logger.debug(f"Loaded env from file: {env_file}")
            return converted_data
            
        except Exception as e:
            logger.error(f"Failed to load env file {env_file}: {e}")
            return {}
    
    def _load_secrets_file(self, secrets_file: str) -> Dict[str, Any]:
        secrets_path = Path(secrets_file)
        if not secrets_path.exists():
            logger.warning(f"Secrets file not found: {secrets_file}")
            return {}
        
        try:
            with secrets_path.open("r", encoding="utf-8") as f:
                if secrets_path.suffix.lower() == ".json":
                    secrets_data = json.load(f)
                else:
                    # Assume key=value format
                    secrets_data = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                secrets_data[key.strip().lower()] = value.strip()
            
            logger.debug(f"Loaded secrets from file: {secrets_file}")
            return secrets_data
            
        except Exception as e:
            logger.error(f"Failed to load secrets file {secrets_file}: {e}")
            return {}
    
    def _load_environment_variables(self) -> Dict[str, Any]:
        env_data = {}
        for key, value in os.environ.items():
            env_data[key.lower()] = self._convert_env_value(value)
        
        logger.debug("Loaded configuration from environment variables")
        return env_data
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool, list]:
      
        if not value:
            return value
        
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False
        
        if "," in value:
            return [item.strip() for item in value.split(",") if item.strip()]
        
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        return value
    
    def _validate_config(self) -> None:
      
        if not self._config:
            raise ConfigurationError("No configuration to validate")
        
        errors = []
        
        if self.environment == "production":
            required_fields = [
                "secret_key", "database_url", "redis_url",
                "jwt_private_key", "jwt_public_key"
            ]
            for field in required_fields:
                if not getattr(self._config, field, None):
                    errors.append(f"Missing required field for production: {field}")
        
        if hasattr(self._config, "secret_key"):
            secret_key = getattr(self._config, "secret_key", "")
            if len(secret_key) < 32:
                errors.append("Secret key must be at least 32 characters long")
        
        if hasattr(self._config, "database_url"):
            db_url = getattr(self._config, "database_url", "")
            if self.environment == "production" and "localhost" in db_url:
                errors.append("Production database cannot use localhost")
        
        if hasattr(self._config, "is_production_ready"):
            if self.environment == "production" and not self._config.is_production_ready():
                errors.append("Configuration is not production ready")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        logger.info("Configuration validation passed")
    
    def get_config_summary(self) -> Dict[str, Any]:
        if not self._config:
            return {"error": "Configuration not loaded"}
        
        config_dict = self._config.dict()
        
        sensitive_fields = [
            "secret_key", "password", "api_key", "token", "private_key",
            "jwt_private_key", "smtp_password", "database_url", "redis_url"
        ]
        
        masked_config = {}
        for key, value in config_dict.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                if value:
                    masked_config[key] = f"{'*' * (len(str(value)) - 4)}{str(value)[-4:]}"
                else:
                    masked_config[key] = None
            else:
                masked_config[key] = value
        
        return {
            "environment": self.environment,
            "sources": self._config_sources,
            "config": masked_config,
            "validation_passed": True
        }


config_loader = ConfigLoader()


def load_config(
    environment: Optional[str] = None,
    config_file: Optional[str] = None,
    env_file: Optional[str] = None,
    secrets_file: Optional[str] = None,
    validate: bool = True
) -> BaseEnvironmentConfig:
   
    if environment:
        global config_loader
        config_loader = ConfigLoader(environment)
    
    return config_loader.load_config(
        config_file=config_file,
        env_file=env_file,
        secrets_file=secrets_file,
        validate=validate
    )


def get_config() -> BaseEnvironmentConfig:
    return config_loader.get_config()


def reload_config(**kwargs) -> BaseEnvironmentConfig:
    return config_loader.reload_config(**kwargs) 