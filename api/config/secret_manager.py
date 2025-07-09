"""
Secret Manager Utility

This module provides secure handling of secrets from various sources including
environment variables, files, AWS Secrets Manager, HashiCorp Vault, and Azure Key Vault.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class SecretManagerError(Exception):
    """Secret manager error."""
    pass


class BaseSecretProvider(ABC):
    """Abstract base class for secret providers."""
    
    @abstractmethod
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a secret value by name.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            Secret value or None if not found
        """
        pass
    
    @abstractmethod
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets by names.
        
        Args:
            secret_names: List of secret names
            
        Returns:
            Dictionary mapping secret names to values
        """
        pass
    
    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set a secret value.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            True if successful, False otherwise
        """
        pass


class EnvironmentSecretProvider(BaseSecretProvider):
    """Secret provider that reads from environment variables."""
    
    def __init__(self, prefix: str = ""):
        """Initialize environment secret provider.
        
        Args:
            prefix: Optional prefix for environment variable names
        """
        self.prefix = prefix
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from environment variable."""
        env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
        return os.getenv(env_name)
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets from environment variables."""
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set environment variable (for current process only)."""
        try:
            env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
            os.environ[env_name] = secret_value
            return True
        except Exception as e:
            logger.error(f"Failed to set environment secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete environment variable."""
        try:
            env_name = f"{self.prefix}{secret_name.upper()}" if self.prefix else secret_name.upper()
            if env_name in os.environ:
                del os.environ[env_name]
            return True
        except Exception as e:
            logger.error(f"Failed to delete environment secret {secret_name}: {e}")
            return False


class FileSecretProvider(BaseSecretProvider):
    """Secret provider that reads from files."""
    
    def __init__(self, secrets_dir: str):
        """Initialize file secret provider.
        
        Args:
            secrets_dir: Directory containing secret files
        """
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from file."""
        try:
            secret_file = self.secrets_dir / secret_name
            if secret_file.exists():
                return secret_file.read_text(encoding="utf-8").strip()
            return None
        except Exception as e:
            logger.error(f"Failed to read secret file {secret_name}: {e}")
            return None
    
    async def get_secrets(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets from files."""
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Write secret to file."""
        try:
            secret_file = self.secrets_dir / secret_name
            secret_file.write_text(secret_value, encoding="utf-8")
            secret_file.chmod(0o600)  # Restrict permissions
            return True
        except Exception as e:
            logger.error(f"Failed to write secret file {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret file."""
        try:
            secret_file = self.secrets_dir / secret_name
            if secret_file.exists():
                secret_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret file {secret_name}: {e}")
            return False


class AWSSecretsManagerProvider(BaseSecretProvider):
    """Secret provider for AWS Secrets Manager."""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize AWS Secrets Manager provider.
        
        Args:
            region_name: AWS region name
        """
        self.region_name = region_name
        self._client = None
    
    @property
    def client(self):
        """Get or create AWS Secrets Manager client."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("secretsmanager", region_name=self.region_name)
            except ImportError:
                raise SecretManagerError("boto3 is required for AWS Secrets Manager")
        return self._client
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
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
        """Get multiple secrets from AWS Secrets Manager."""
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Create or update secret in AWS Secrets Manager."""
        try:
            # Try to update existing secret
            try:
                self.client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_value
                )
            except self.client.exceptions.ResourceNotFoundException:
                # Create new secret
                self.client.create_secret(
                    Name=secret_name,
                    SecretString=secret_value
                )
            return True
        except Exception as e:
            logger.error(f"Failed to set AWS secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from AWS Secrets Manager."""
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
    """Secret provider for HashiCorp Vault."""
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        """Initialize HashiCorp Vault provider.
        
        Args:
            vault_url: Vault server URL
            vault_token: Vault authentication token
            mount_point: KV secrets engine mount point
        """
        self.vault_url = vault_url.rstrip("/")
        self.vault_token = vault_token
        self.mount_point = mount_point
        self._client = None
    
    @property
    def client(self):
        """Get or create Vault client."""
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.vault_url, token=self.vault_token)
            except ImportError:
                raise SecretManagerError("hvac is required for HashiCorp Vault")
        return self._client
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from HashiCorp Vault."""
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
        """Get multiple secrets from HashiCorp Vault."""
        result = {}
        for name in secret_names:
            result[name] = await self.get_secret(name)
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in HashiCorp Vault."""
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
        """Delete secret from HashiCorp Vault."""
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
    """Main secret manager that coordinates multiple secret providers."""
    
    def __init__(self):
        """Initialize secret manager."""
        self.providers: list[BaseSecretProvider] = []
        self._cache: Dict[str, str] = {}
        self.cache_enabled = True
    
    def add_provider(self, provider: BaseSecretProvider) -> None:
        """Add a secret provider.
        
        Args:
            provider: Secret provider to add
        """
        self.providers.append(provider)
        logger.debug(f"Added secret provider: {provider.__class__.__name__}")
    
    def clear_providers(self) -> None:
        """Clear all secret providers."""
        self.providers.clear()
        self.clear_cache()
    
    def enable_cache(self, enabled: bool = True) -> None:
        """Enable or disable secret caching.
        
        Args:
            enabled: Whether to enable caching
        """
        self.cache_enabled = enabled
        if not enabled:
            self.clear_cache()
    
    def clear_cache(self) -> None:
        """Clear the secret cache."""
        self._cache.clear()
    
    async def get_secret(self, secret_name: str, use_cache: bool = True) -> Optional[str]:
        """Get a secret value from configured providers.
        
        Args:
            secret_name: Name of the secret
            use_cache: Whether to use cached value
            
        Returns:
            Secret value or None if not found
        """
        # Check cache first
        if use_cache and self.cache_enabled and secret_name in self._cache:
            return self._cache[secret_name]
        
        # Try each provider in order
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
        """Get multiple secrets from configured providers.
        
        Args:
            secret_names: List of secret names
            use_cache: Whether to use cached values
            
        Returns:
            Dictionary mapping secret names to values
        """
        result = {}
        
        for secret_name in secret_names:
            result[secret_name] = await self.get_secret(secret_name, use_cache)
        
        return result
    
    async def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set a secret value using the first provider.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            
        Returns:
            True if successful, False otherwise
        """
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
        """Delete a secret using the first provider.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            True if successful, False otherwise
        """
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
        """Replace secret references in configuration with actual values.
        
        Args:
            config_dict: Configuration dictionary with potential secret references
            
        Returns:
            Configuration with secrets resolved
        """
        import asyncio
        
        async def resolve_secrets():
            result = {}
            for key, value in config_dict.items():
                if isinstance(value, str) and value.startswith("secret://"):
                    secret_name = value[9:]  # Remove "secret://" prefix
                    secret_value = await self.get_secret(secret_name)
                    result[key] = secret_value if secret_value is not None else value
                elif isinstance(value, dict):
                    result[key] = self.get_config_with_secrets(value)
                else:
                    result[key] = value
            return result
        
        return asyncio.run(resolve_secrets())


# Global secret manager instance
secret_manager = SecretManager()


def setup_secret_providers(
    environment: str = "development",
    secrets_dir: Optional[str] = None,
    aws_region: Optional[str] = None,
    vault_url: Optional[str] = None,
    vault_token: Optional[str] = None
) -> None:
    """Setup secret providers based on environment.
    
    Args:
        environment: Current environment
        secrets_dir: Directory for file-based secrets
        aws_region: AWS region for Secrets Manager
        vault_url: HashiCorp Vault URL
        vault_token: HashiCorp Vault token
    """
    secret_manager.clear_providers()
    
    # Always add environment provider as fallback
    secret_manager.add_provider(EnvironmentSecretProvider())
    
    # Add file provider for development
    if environment == "development" and secrets_dir:
        secret_manager.add_provider(FileSecretProvider(secrets_dir))
    
    # Add cloud providers for staging/production
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
    """Get a secret using the global secret manager.
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        Secret value or None if not found
    """
    return await secret_manager.get_secret(secret_name)


async def get_secrets(secret_names: list[str]) -> Dict[str, Optional[str]]:
    """Get multiple secrets using the global secret manager.
    
    Args:
        secret_names: List of secret names
        
    Returns:
        Dictionary mapping secret names to values
    """
    return await secret_manager.get_secrets(secret_names) 