from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from enum import Enum
import os

class EmailConfig(BaseSettings):
    
    EMAIL_BACKEND: str = Field(default="smtp", env="EMAIL_BACKEND")
    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_HOST_USER: str = Field(default="noreply@craftyhub.com", env="EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD: str = Field(default="changeme", env="EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS: bool = Field(default=True, env="EMAIL_USE_TLS")
    EMAIL_USE_SSL: bool = Field(default=False, env="EMAIL_USE_SSL")
    
    DEFAULT_FROM_EMAIL: str = Field(default="noreply@craftyhub.com", env="DEFAULT_FROM_EMAIL")
    DEFAULT_FROM_NAME: str = Field(default="CraftyXhub", env="DEFAULT_FROM_NAME")
    DEFAULT_REPLY_TO: Optional[str] = Field(default=None, env="DEFAULT_REPLY_TO")
    
    EMAIL_TIMEOUT: int = Field(default=30, env="EMAIL_TIMEOUT")
    EMAIL_RETRY_ATTEMPTS: int = Field(default=3, env="EMAIL_RETRY_ATTEMPTS")
    EMAIL_RETRY_DELAY: int = Field(default=5, env="EMAIL_RETRY_DELAY")
    
    EMAIL_TEMPLATE_DIR: str = Field(default="templates/email", env="EMAIL_TEMPLATE_DIR")
    EMAIL_TEMPLATE_ENGINE: str = Field(default="jinja2", env="EMAIL_TEMPLATE_ENGINE")
    EMAIL_TEMPLATE_CACHE: bool = Field(default=True, env="EMAIL_TEMPLATE_CACHE")
    
    EMAIL_QUEUE_ENABLED: bool = Field(default=True, env="EMAIL_QUEUE_ENABLED")
    EMAIL_QUEUE_BACKEND: str = Field(default="redis", env="EMAIL_QUEUE_BACKEND")
    EMAIL_QUEUE_MAX_RETRIES: int = Field(default=3, env="EMAIL_QUEUE_MAX_RETRIES")
    EMAIL_QUEUE_RETRY_DELAY: int = Field(default=60, env="EMAIL_QUEUE_RETRY_DELAY")
    
    EMAIL_RATE_LIMIT_ENABLED: bool = Field(default=True, env="EMAIL_RATE_LIMIT_ENABLED")
    EMAIL_RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="EMAIL_RATE_LIMIT_PER_MINUTE")
    EMAIL_RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="EMAIL_RATE_LIMIT_PER_HOUR")
    EMAIL_RATE_LIMIT_PER_DAY: int = Field(default=10000, env="EMAIL_RATE_LIMIT_PER_DAY")
    
    WELCOME_EMAIL_ENABLED: bool = Field(default=True, env="WELCOME_EMAIL_ENABLED")
    VERIFICATION_EMAIL_ENABLED: bool = Field(default=True, env="VERIFICATION_EMAIL_ENABLED")
    PASSWORD_RESET_EMAIL_ENABLED: bool = Field(default=True, env="PASSWORD_RESET_EMAIL_ENABLED")
    NOTIFICATION_EMAIL_ENABLED: bool = Field(default=True, env="NOTIFICATION_EMAIL_ENABLED")
    NEWSLETTER_EMAIL_ENABLED: bool = Field(default=False, env="NEWSLETTER_EMAIL_ENABLED")
    
    WELCOME_EMAIL_TEMPLATE: str = Field(default="welcome.html", env="WELCOME_EMAIL_TEMPLATE")
    VERIFICATION_EMAIL_TEMPLATE: str = Field(default="email_verification.html", env="VERIFICATION_EMAIL_TEMPLATE")
    PASSWORD_RESET_EMAIL_TEMPLATE: str = Field(default="password_reset.html", env="PASSWORD_RESET_EMAIL_TEMPLATE")
    NOTIFICATION_EMAIL_TEMPLATE: str = Field(default="notification.html", env="NOTIFICATION_EMAIL_TEMPLATE")
    
    WELCOME_EMAIL_SUBJECT: str = Field(default="Welcome to CraftyXhub!", env="WELCOME_EMAIL_SUBJECT")
    VERIFICATION_EMAIL_SUBJECT: str = Field(default="Verify your email address", env="VERIFICATION_EMAIL_SUBJECT")
    PASSWORD_RESET_EMAIL_SUBJECT: str = Field(default="Reset your password", env="PASSWORD_RESET_EMAIL_SUBJECT")
    
    EMAIL_INCLUDE_UNSUBSCRIBE: bool = Field(default=True, env="EMAIL_INCLUDE_UNSUBSCRIBE")
    EMAIL_INCLUDE_BRANDING: bool = Field(default=True, env="EMAIL_INCLUDE_BRANDING")
    EMAIL_TRACK_OPENS: bool = Field(default=False, env="EMAIL_TRACK_OPENS")
    EMAIL_TRACK_CLICKS: bool = Field(default=False, env="EMAIL_TRACK_CLICKS")

    BULK_EMAIL_ENABLED: bool = Field(default=False, env="BULK_EMAIL_ENABLED")
    BULK_EMAIL_BATCH_SIZE: int = Field(default=100, env="BULK_EMAIL_BATCH_SIZE")
    BULK_EMAIL_DELAY_BETWEEN_BATCHES: int = Field(default=5, env="BULK_EMAIL_DELAY_BETWEEN_BATCHES")
    
    EMAIL_DKIM_ENABLED: bool = Field(default=False, env="EMAIL_DKIM_ENABLED")
    EMAIL_DKIM_DOMAIN: Optional[str] = Field(default=None, env="EMAIL_DKIM_DOMAIN")
    EMAIL_DKIM_SELECTOR: Optional[str] = Field(default=None, env="EMAIL_DKIM_SELECTOR")
    EMAIL_DKIM_PRIVATE_KEY_PATH: Optional[str] = Field(default=None, env="EMAIL_DKIM_PRIVATE_KEY_PATH")
    
    EMAIL_VALIDATION_ENABLED: bool = Field(default=True, env="EMAIL_VALIDATION_ENABLED")
    EMAIL_DOMAIN_BLACKLIST: List[str] = Field(default=[], env="EMAIL_DOMAIN_BLACKLIST")
    EMAIL_DISPOSABLE_CHECK: bool = Field(default=True, env="EMAIL_DISPOSABLE_CHECK")
    
    EMAIL_LOGGING_ENABLED: bool = Field(default=True, env="EMAIL_LOGGING_ENABLED")
    EMAIL_LOG_LEVEL: str = Field(default="INFO", env="EMAIL_LOG_LEVEL")
    EMAIL_LOG_SENT_EMAILS: bool = Field(default=True, env="EMAIL_LOG_SENT_EMAILS")
    EMAIL_LOG_FAILED_EMAILS: bool = Field(default=True, env="EMAIL_LOG_FAILED_EMAILS")
    
    EMAIL_DEVELOPMENT_MODE: bool = Field(default=False, env="EMAIL_DEVELOPMENT_MODE")
    EMAIL_DEVELOPMENT_RECIPIENT: Optional[str] = Field(default=None, env="EMAIL_DEVELOPMENT_RECIPIENT")
    EMAIL_FILE_PATH: Optional[str] = Field(default=None, env="EMAIL_FILE_PATH")
    
    @field_validator("EMAIL_PORT")
    @classmethod
    def validate_email_port(cls, v):
        if v not in [25, 465, 587, 2525]:
            raise ValueError("EMAIL_PORT must be one of: 25, 465, 587, 2525")
        return v
    
    @field_validator("EMAIL_TEMPLATE_ENGINE")
    @classmethod
    def validate_template_engine(cls, v):
        valid_engines = ["jinja2", "django", "mako"]
        if v not in valid_engines:
            raise ValueError(f"EMAIL_TEMPLATE_ENGINE must be one of: {valid_engines}")
        return v
    
    @field_validator("EMAIL_QUEUE_BACKEND")
    @classmethod
    def validate_queue_backend(cls, v):
        valid_backends = ["redis", "memory", "database", "celery"]
        if v not in valid_backends:
            raise ValueError(f"EMAIL_QUEUE_BACKEND must be one of: {valid_backends}")
        return v
    
    @field_validator("EMAIL_LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"EMAIL_LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("EMAIL_DOMAIN_BLACKLIST", mode="before")
    @classmethod
    def parse_domain_blacklist(cls, v):
        if isinstance(v, str):
            return [domain.strip().lower() for domain in v.split(",") if domain.strip()]
        return v
    
    def get_smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration dictionary."""
        return {
            "host": self.EMAIL_HOST,
            "port": self.EMAIL_PORT,
            "username": self.EMAIL_HOST_USER,
            "password": self.EMAIL_HOST_PASSWORD,
            "use_tls": self.EMAIL_USE_TLS,
            "use_ssl": self.EMAIL_USE_SSL,
            "timeout": self.EMAIL_TIMEOUT,
        }
    
    def get_template_config(self) -> Dict[str, Any]:
        """Get email template configuration."""
        return {
            "template_dir": self.EMAIL_TEMPLATE_DIR,
            "engine": self.EMAIL_TEMPLATE_ENGINE,
            "cache_enabled": self.EMAIL_TEMPLATE_CACHE,
            "templates": {
                "welcome": self.WELCOME_EMAIL_TEMPLATE,
                "verification": self.VERIFICATION_EMAIL_TEMPLATE,
                "password_reset": self.PASSWORD_RESET_EMAIL_TEMPLATE,
                "notification": self.NOTIFICATION_EMAIL_TEMPLATE,
            },
            "subjects": {
                "welcome": self.WELCOME_EMAIL_SUBJECT,
                "verification": self.VERIFICATION_EMAIL_SUBJECT,
                "password_reset": self.PASSWORD_RESET_EMAIL_SUBJECT,
            }
        }
    
    def get_sender_config(self) -> Dict[str, Any]:
        """Get email sender configuration."""
        return {
            "from_email": self.DEFAULT_FROM_EMAIL,
            "from_name": self.DEFAULT_FROM_NAME,
            "reply_to": self.DEFAULT_REPLY_TO,
            "include_unsubscribe": self.EMAIL_INCLUDE_UNSUBSCRIBE,
            "include_branding": self.EMAIL_INCLUDE_BRANDING,
        }
    
    def get_queue_config(self) -> Dict[str, Any]:
        """Get email queue configuration."""
        return {
            "enabled": self.EMAIL_QUEUE_ENABLED,
            "backend": self.EMAIL_QUEUE_BACKEND,
            "max_retries": self.EMAIL_QUEUE_MAX_RETRIES,
            "retry_delay": self.EMAIL_QUEUE_RETRY_DELAY,
            "batch_size": self.BULK_EMAIL_BATCH_SIZE,
            "delay_between_batches": self.BULK_EMAIL_DELAY_BETWEEN_BATCHES,
        }
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get email rate limiting configuration."""
        return {
            "per_minute": self.EMAIL_RATE_LIMIT_PER_MINUTE,
            "per_hour": self.EMAIL_RATE_LIMIT_PER_HOUR,
            "per_day": self.EMAIL_RATE_LIMIT_PER_DAY,
        }
    
    def is_email_type_enabled(self, email_type: str) -> bool:
        """Check if specific email type is enabled."""
        type_flags = {
            "welcome": self.WELCOME_EMAIL_ENABLED,
            "verification": self.VERIFICATION_EMAIL_ENABLED,
            "password_reset": self.PASSWORD_RESET_EMAIL_ENABLED,
            "notification": self.NOTIFICATION_EMAIL_ENABLED,
            "newsletter": self.NEWSLETTER_EMAIL_ENABLED,
        }
        return type_flags.get(email_type, False)
    
    def is_development_mode(self) -> bool:
        """Check if email is in development mode."""
        return self.EMAIL_DEVELOPMENT_MODE
    
    def get_development_recipient(self) -> Optional[str]:
        """Get development recipient email."""
        return self.EMAIL_DEVELOPMENT_RECIPIENT
    
    model_config = {
        "env_file": "../.env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global email configuration instance
email_config = EmailConfig() 