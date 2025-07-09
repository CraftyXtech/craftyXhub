from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from enum import Enum
import os

class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"
    TWITTER = "twitter"

class AuthConfig(BaseSettings):
    """Authentication and security configuration."""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="dev-jwt-secret-key-change-me-please-1234567890", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="RS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    JWT_TOKEN_ISSUER: str = Field(default="craftyhub", env="JWT_TOKEN_ISSUER")
    JWT_TOKEN_AUDIENCE: str = Field(default="craftyhub-users", env="JWT_TOKEN_AUDIENCE")
    
    # RSA Keys for RS256
    JWT_PRIVATE_KEY_PATH: Optional[str] = Field(default=None, env="JWT_PRIVATE_KEY_PATH")
    JWT_PUBLIC_KEY_PATH: Optional[str] = Field(default=None, env="JWT_PUBLIC_KEY_PATH")
    JWT_PRIVATE_KEY: Optional[str] = Field(default=None, env="JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: Optional[str] = Field(default=None, env="JWT_PUBLIC_KEY")
    
    # Session Configuration
    SESSION_SECRET_KEY: str = Field(default="dev-session-secret-key-change-me-please-1234567890", env="SESSION_SECRET_KEY")
    SESSION_COOKIE_NAME: str = Field(default="craftyx_session", env="SESSION_COOKIE_NAME")
    SESSION_COOKIE_DOMAIN: Optional[str] = Field(default=None, env="SESSION_COOKIE_DOMAIN")
    SESSION_COOKIE_SECURE: bool = Field(default=True, env="SESSION_COOKIE_SECURE")
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, env="SESSION_COOKIE_HTTPONLY")
    SESSION_COOKIE_SAMESITE: str = Field(default="lax", env="SESSION_COOKIE_SAMESITE")
    SESSION_EXPIRE_SECONDS: int = Field(default=86400, env="SESSION_EXPIRE_SECONDS")  # 24 hours
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True, env="PASSWORD_REQUIRE_DIGITS")
    PASSWORD_REQUIRE_SYMBOLS: bool = Field(default=True, env="PASSWORD_REQUIRE_SYMBOLS")
    PASSWORD_HASH_ROUNDS: int = Field(default=12, env="PASSWORD_HASH_ROUNDS")
    
    # Rate Limiting
    LOGIN_RATE_LIMIT_ATTEMPTS: int = Field(default=5, env="LOGIN_RATE_LIMIT_ATTEMPTS")
    LOGIN_RATE_LIMIT_WINDOW: int = Field(default=900, env="LOGIN_RATE_LIMIT_WINDOW")  # 15 minutes
    REGISTER_RATE_LIMIT_ATTEMPTS: int = Field(default=3, env="REGISTER_RATE_LIMIT_ATTEMPTS")
    REGISTER_RATE_LIMIT_WINDOW: int = Field(default=3600, env="REGISTER_RATE_LIMIT_WINDOW")  # 1 hour
    PASSWORD_RESET_RATE_LIMIT_ATTEMPTS: int = Field(default=3, env="PASSWORD_RESET_RATE_LIMIT_ATTEMPTS")
    PASSWORD_RESET_RATE_LIMIT_WINDOW: int = Field(default=3600, env="PASSWORD_RESET_RATE_LIMIT_WINDOW")
    
    # Account Security
    ACCOUNT_LOCKOUT_ENABLED: bool = Field(default=True, env="ACCOUNT_LOCKOUT_ENABLED")
    ACCOUNT_LOCKOUT_ATTEMPTS: int = Field(default=5, env="ACCOUNT_LOCKOUT_ATTEMPTS")
    ACCOUNT_LOCKOUT_DURATION: int = Field(default=1800, env="ACCOUNT_LOCKOUT_DURATION")  # 30 minutes
    
    # Email Verification
    EMAIL_VERIFICATION_REQUIRED: bool = Field(default=True, env="EMAIL_VERIFICATION_REQUIRED")
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = Field(default=24, env="EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS")
    EMAIL_VERIFICATION_RATE_LIMIT: int = Field(default=3, env="EMAIL_VERIFICATION_RATE_LIMIT")
    
    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = Field(default=1, env="PASSWORD_RESET_TOKEN_EXPIRE_HOURS")
    PASSWORD_RESET_TOKEN_LENGTH: int = Field(default=32, env="PASSWORD_RESET_TOKEN_LENGTH")
    
    # Two-Factor Authentication
    TWO_FACTOR_ENABLED: bool = Field(default=False, env="TWO_FACTOR_ENABLED")
    TWO_FACTOR_ISSUER: str = Field(default="CraftyXhub", env="TWO_FACTOR_ISSUER")
    TWO_FACTOR_BACKUP_CODES_COUNT: int = Field(default=8, env="TWO_FACTOR_BACKUP_CODES_COUNT")
    
    # OAuth Providers
    OAUTH_ENABLED: bool = Field(default=False, env="OAUTH_ENABLED")
    OAUTH_PROVIDERS: List[AuthProvider] = Field(default=[], env="OAUTH_PROVIDERS")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None, env="GOOGLE_REDIRECT_URI")
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI: Optional[str] = Field(default=None, env="GITHUB_REDIRECT_URI")
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")
    HSTS_MAX_AGE: int = Field(default=31536000, env="HSTS_MAX_AGE")  # 1 year
    CONTENT_SECURITY_POLICY: Optional[str] = Field(default=None, env="CONTENT_SECURITY_POLICY")
    
    # Token Blacklisting
    TOKEN_BLACKLIST_ENABLED: bool = Field(default=True, env="TOKEN_BLACKLIST_ENABLED")
    TOKEN_BLACKLIST_GRACE_PERIOD: int = Field(default=300, env="TOKEN_BLACKLIST_GRACE_PERIOD")  # 5 minutes
    
    # API Key Authentication
    API_KEY_ENABLED: bool = Field(default=False, env="API_KEY_ENABLED")
    API_KEY_HEADER_NAME: str = Field(default="X-API-Key", env="API_KEY_HEADER_NAME")
    API_KEY_QUERY_PARAM: str = Field(default="api_key", env="API_KEY_QUERY_PARAM")
    
    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, v):
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]
        if v not in valid_algorithms:
            raise ValueError(f"JWT_ALGORITHM must be one of: {valid_algorithms}")
        return v
    
    @field_validator("JWT_SECRET_KEY", "SESSION_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v):
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters long")
        return v
    
    @field_validator("SESSION_COOKIE_SAMESITE")
    @classmethod
    def validate_samesite(cls, v):
        valid_values = ["strict", "lax", "none"]
        if v.lower() not in valid_values:
            raise ValueError(f"SESSION_COOKIE_SAMESITE must be one of: {valid_values}")
        return v.lower()
    
    @field_validator("PASSWORD_MIN_LENGTH")
    @classmethod
    def validate_password_length(cls, v):
        if v < 6:
            raise ValueError("PASSWORD_MIN_LENGTH must be at least 6")
        return v
    
    @field_validator("PASSWORD_HASH_ROUNDS")
    @classmethod
    def validate_hash_rounds(cls, v):
        if v < 10 or v > 16:
            raise ValueError("PASSWORD_HASH_ROUNDS must be between 10 and 16")
        return v
    
    @field_validator("OAUTH_PROVIDERS", mode="before")
    @classmethod
    def parse_oauth_providers(cls, v):
        if isinstance(v, str):
            return [provider.strip() for provider in v.split(",") if provider.strip()]
        return v
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration dictionary."""
        config = {
            "algorithm": self.JWT_ALGORITHM,
            "access_token_expire_minutes": self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
            "issuer": self.JWT_TOKEN_ISSUER,
            "audience": self.JWT_TOKEN_AUDIENCE,
        }
        
        if self.JWT_ALGORITHM.startswith("RS"):
            # RSA algorithms need public/private keys
            config["private_key"] = self.get_private_key()
            config["public_key"] = self.get_public_key()
        else:
            # HMAC algorithms use secret key
            config["secret_key"] = self.JWT_SECRET_KEY
        
        return config
    
    def get_private_key(self) -> Optional[str]:
        """Get JWT private key from file or environment."""
        if self.JWT_PRIVATE_KEY:
            return self.JWT_PRIVATE_KEY
        
        if self.JWT_PRIVATE_KEY_PATH and os.path.exists(self.JWT_PRIVATE_KEY_PATH):
            with open(self.JWT_PRIVATE_KEY_PATH, 'r') as f:
                return f.read()
        
        return None
    
    def get_public_key(self) -> Optional[str]:
        """Get JWT public key from file or environment."""
        if self.JWT_PUBLIC_KEY:
            return self.JWT_PUBLIC_KEY
        
        if self.JWT_PUBLIC_KEY_PATH and os.path.exists(self.JWT_PUBLIC_KEY_PATH):
            with open(self.JWT_PUBLIC_KEY_PATH, 'r') as f:
                return f.read()
        
        return None
    
    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration dictionary."""
        return {
            "secret_key": self.SESSION_SECRET_KEY,
            "cookie_name": self.SESSION_COOKIE_NAME,
            "cookie_domain": self.SESSION_COOKIE_DOMAIN,
            "cookie_secure": self.SESSION_COOKIE_SECURE,
            "cookie_httponly": self.SESSION_COOKIE_HTTPONLY,
            "cookie_samesite": self.SESSION_COOKIE_SAMESITE,
            "expire_seconds": self.SESSION_EXPIRE_SECONDS,
        }
    
    def get_password_policy(self) -> Dict[str, Any]:
        """Get password policy configuration."""
        return {
            "min_length": self.PASSWORD_MIN_LENGTH,
            "require_uppercase": self.PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": self.PASSWORD_REQUIRE_LOWERCASE,
            "require_digits": self.PASSWORD_REQUIRE_DIGITS,
            "require_symbols": self.PASSWORD_REQUIRE_SYMBOLS,
            "hash_rounds": self.PASSWORD_HASH_ROUNDS,
        }
    
    def get_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Get rate limiting configuration."""
        return {
            "login": {
                "attempts": self.LOGIN_RATE_LIMIT_ATTEMPTS,
                "window": self.LOGIN_RATE_LIMIT_WINDOW,
            },
            "register": {
                "attempts": self.REGISTER_RATE_LIMIT_ATTEMPTS,
                "window": self.REGISTER_RATE_LIMIT_WINDOW,
            },
            "password_reset": {
                "attempts": self.PASSWORD_RESET_RATE_LIMIT_ATTEMPTS,
                "window": self.PASSWORD_RESET_RATE_LIMIT_WINDOW,
            },
        }
    
    def is_oauth_enabled(self, provider: AuthProvider) -> bool:
        """Check if OAuth provider is enabled."""
        return self.OAUTH_ENABLED and provider in self.OAUTH_PROVIDERS
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global auth configuration instance
auth_config = AuthConfig() 