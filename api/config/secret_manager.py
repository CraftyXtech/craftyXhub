
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class SecretManagerError(Exception):
    pass


class BaseSecretProvider(ABC):
    
    @abstractmethod
    async def get_secret(self, secret_name: str) -> Optional[str]:
        pass
    
    @abstractmethod
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        pass
    
    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_name: str) -> bool:
        pass


class EnvironmentSecretProvider(BaseSecretProvider):
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
        return os.getenv(env_name)
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:    
        try:
            env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
            os.environ[env_name] = secret_value
            return True
        except Exception as e:
            logger.error(f"Failed to set environment secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        try:
            env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
            if env_name in os.environ:
                del os.environ[env_name]
            return True
        except Exception as e:
            logger.error(f"Failed to delete environment secret {secret_name}: {e}")
            return False


class FileSecretProvider(BaseSecretProvider):
    
    def __init__(self, secrets_dir: str):
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        try:
            secret_file = self.secrets_dir / secret_name
            if secret_file.exists():
                return secret_file.read_text(encoding="utf-8").strip()
            return None
        except Exception as e:
            logger.error(f"Failed to read secret file {secret_name}: {e}")
            return None
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        try:
            secret_file = self.secrets_dir / secret_name
            secret_file.write_text(secret_value, encoding="utf-8")
            secret_file.chmod(0o600)
            return True
        except Exception as e:
            logger.error(f"Failed to write secret file {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        try:
            secret_file = self.secrets_dir / secret_name
            if secret_file.exists():
                secret_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret file {secret_name}: {e}")
            return False


class AWSSecretsManagerProvider(BaseSecretProvider):
    
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("secretsmanager", region_name=self.region_name)
            except ImportError:
                raise SecretManagerError("boto3 is required for AWS Secrets Manager")
        return self._client
    
    async def get_secret(self, secret_name: str) -> Optional[str]:      
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except self.client.exceptions.ResourceNotFoundException:
            logger.warning(f"Secret not found in AWS Secrets Manager: {secret_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to get AWS secret {secret_name}: {e}")
            return None
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        try:
            try:
                self.client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_value
                )
            except self.client.exceptions.ResourceNotFoundException:
                self.client.create_secret(
                    Name=secret_name,
                    SecretString=secret_value
                )
            return True
        except Exception as e:
            logger.error(f"Failed to set AWS secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        try:
            self.client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete AWS secret {secret_name}: {e}")
            return False


class HashiCorpVaultProvider(BaseSecretProvider):
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        
        self.vault_url = vault_url.rstrip("/")
        self.vault_token = vault_token
        self.mount_point = mount_point
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.vault_url, token=self.vault_token)
            except ImportError:
                raise SecretManagerError("hvac is required for HashiCorp Vault")
        return self._client
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_name,
                mount_point=self.mount_point
            )
            return response["data"]["data"].get("value")
        except Exception as e:
            logger.error(f"Failed to get Vault secret {secret_name}: {e}")
            return None
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=secret_name,
                secret={"value": secret_value},
                mount_point=self.mount_point
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set Vault secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=secret_name,
                mount_point=self.mount_point
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete Vault secret {secret_name}: {e}")
            return False


class SecretManager:
    
    def __init__(self):
        self.providers: list[BaseSecretProvider] = []
        self._cache: Dict[str, str] = {}
        self.cache_enabled = True
    
    def add_provider(self, provider: BaseSecretProvider) -> None:
        self.providers.append(provider)
        logger.debug(f"Added secret provider: {provider.__class__.__name__}")
    
    def clear_providers(self) -> None:
        self.providers.clear()
        self.clear_cache()
    
    def enable_cache(self, enabled: bool = True) -> None:
        self.cache_enabled = enabled
        if not enabled:
            self.clear_cache()
    
    def clear_cache(self) -> None:
        self._cache.clear()
    
    async def get_secret(self, secret_name: str, use_cache: bool = True) -> Optional[str]:
        
        if use_cache and self.cache_enabled and secret_name in self._cache:
            return self._cache[secret_name]
        
        for provider in self.providers:
            try:
                secret_value = await provider.get_secret(secret_name)
                if secret_value is not None:
                    # Cache the value
                    if self.cache_enabled:
                        self._cache[secret_name] = secret_value
                    return secret_value
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed for secret {secret_name}: {e}")
                continue
        
        logger.warning(f"Secret not found in any provider: {secret_name}")
        return None
    
    async def get_secrets(
        self,
        secret_names: list[str],
        use_cache: bool = True
    ) -> Dict[str, Optional[str]]:
        
        result = {}
        
        for secret_name in secret_names:
            result[secret_name] = await self.get_secret(secret_name, use_cache)
        
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        
        if not self.providers:
            logger.error("No secret providers configured")
            return False
        
        try:
            success = await self.providers[0].set_secret(secret_name, secret_value)
            if success and self.cache_enabled:
                self._cache[secret_name] = secret_value
            return success
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        
        if not self.providers:
            logger.error("No secret providers configured")
            return False
        
        try:
            success = await self.providers[0].delete_secret(secret_name)
            if success and secret_name in self._cache:
                del self._cache[secret_name]
            return success
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False
    
    def get_config_with_secrets(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        
        import asyncio
        
        async def resolve_secrets():
            result = {}
            for key, value in config_dict.items():
                if isinstance(value, str) and value.startswith("secret://"):
                    secret_name = value[9:]
                    secret_value = await self.get_secret(secret_name)
                    result[key] = secret_value if secret_value is not None else value
                elif isinstance(value, dict):
                    result[key] = self.get_config_with_secrets(value)
                else:
                    result[key] = value
            return result
        
        return asyncio.run(resolve_secrets())


secret_manager = SecretManager()


def setup_secret_providers(
    environment: str = "development",
    secrets_dir: Optional[str] = None,
    aws_region: Optional[str] = None,
    vault_url: Optional[str] = None,
    vault_token: Optional[str] = None
) -> None:

    secret_manager.clear_providers()
    
    secret_manager.add_provider(EnvironmentSecretProvider())
    
    if environment == "development" and secrets_dir:
        secret_manager.add_provider(FileSecretProvider(secrets_dir))
    
    if environment in ["staging", "production"]:
        if aws_region:
            try:
                secret_manager.add_provider(AWSSecretsManagerProvider(aws_region))
            except Exception as e:
                logger.warning(f"Failed to setup AWS Secrets Manager: {e}")
        
        if vault_url and vault_token:
            try:
                secret_manager.add_provider(HashiCorpVaultProvider(vault_url, vault_token))
            except Exception as e:
                logger.warning(f"Failed to setup HashiCorp Vault: {e}")


async def get_secret(secret_name: str) -> Optional[str]:
    
    return await secret_manager.get_secret(secret_name)


async def get_secrets(secret_names: list[str]) -> Dict[str, Optional[str]]:
    
    return await secret_manager.get_secrets(secret_names) 