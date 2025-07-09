from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum
import os

class EmailProvider(str, Enum):
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    SES = "ses"
    POSTMARK = "postmark"

class CloudProvider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITALOCEAN = "digitalocean"

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"

class ServicesConfig(BaseModel):
    """Third-party services configuration."""
    
    # Email Service Configuration
    EMAIL_PROVIDER: EmailProvider = Field(default=EmailProvider.SMTP, env="EMAIL_PROVIDER")
    
    # SMTP Configuration
    SMTP_HOST: str = Field(default="localhost", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    SMTP_USE_SSL: bool = Field(default=False, env="SMTP_USE_SSL")
    SMTP_TIMEOUT: int = Field(default=30, env="SMTP_TIMEOUT")
    
    # Email Settings
    EMAIL_FROM_NAME: str = Field(default="CraftyXhub", env="EMAIL_FROM_NAME")
    EMAIL_FROM_ADDRESS: str = Field(default="noreply@craftyhub.com", env="EMAIL_FROM_ADDRESS")
    EMAIL_REPLY_TO: Optional[str] = Field(default=None, env="EMAIL_REPLY_TO")
    EMAIL_TEMPLATE_DIR: str = Field(default="templates/email", env="EMAIL_TEMPLATE_DIR")
    
    # SendGrid Configuration
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    SENDGRID_TEMPLATE_ID_WELCOME: Optional[str] = Field(default=None, env="SENDGRID_TEMPLATE_ID_WELCOME")
    SENDGRID_TEMPLATE_ID_RESET: Optional[str] = Field(default=None, env="SENDGRID_TEMPLATE_ID_RESET")
    
    # Mailgun Configuration
    MAILGUN_API_KEY: Optional[str] = Field(default=None, env="MAILGUN_API_KEY")
    MAILGUN_DOMAIN: Optional[str] = Field(default=None, env="MAILGUN_DOMAIN")
    MAILGUN_BASE_URL: str = Field(default="https://api.mailgun.net/v3", env="MAILGUN_BASE_URL")
    
    # AWS SES Configuration
    AWS_SES_REGION: Optional[str] = Field(default=None, env="AWS_SES_REGION")
    AWS_SES_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SES_ACCESS_KEY")
    AWS_SES_SECRET_KEY: Optional[str] = Field(default=None, env="AWS_SES_SECRET_KEY")
    
    # AI Services Configuration
    AI_PROVIDER: AIProvider = Field(default=AIProvider.OPENAI, env="AI_PROVIDER")
    AI_ENABLED: bool = Field(default=False, env="AI_ENABLED")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_ORGANIZATION: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    OPENAI_MODEL_TEXT: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL_TEXT")
    OPENAI_MODEL_EMBEDDING: str = Field(default="text-embedding-ada-002", env="OPENAI_MODEL_EMBEDDING")
    OPENAI_MODEL_IMAGE: str = Field(default="dall-e-3", env="OPENAI_MODEL_IMAGE")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    OPENAI_TIMEOUT: int = Field(default=30, env="OPENAI_TIMEOUT")
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    
    # Content Generation
    CONTENT_GENERATION_ENABLED: bool = Field(default=False, env="CONTENT_GENERATION_ENABLED")
    IMAGE_GENERATION_ENABLED: bool = Field(default=False, env="IMAGE_GENERATION_ENABLED")
    EMBEDDING_GENERATION_ENABLED: bool = Field(default=False, env="EMBEDDING_GENERATION_ENABLED")
    
    # Cloud Storage Configuration
    CLOUD_STORAGE_PROVIDER: CloudProvider = Field(default=CloudProvider.AWS, env="CLOUD_STORAGE_PROVIDER")
    CLOUD_STORAGE_ENABLED: bool = Field(default=False, env="CLOUD_STORAGE_ENABLED")
    
    # AWS S3 Configuration
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    AWS_S3_REGION: Optional[str] = Field(default=None, env="AWS_S3_REGION")
    AWS_S3_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_S3_ACCESS_KEY")
    AWS_S3_SECRET_KEY: Optional[str] = Field(default=None, env="AWS_S3_SECRET_KEY")
    AWS_S3_ENDPOINT_URL: Optional[str] = Field(default=None, env="AWS_S3_ENDPOINT_URL")
    AWS_S3_USE_SSL: bool = Field(default=True, env="AWS_S3_USE_SSL")
    AWS_S3_CUSTOM_DOMAIN: Optional[str] = Field(default=None, env="AWS_S3_CUSTOM_DOMAIN")
    
    # Google Cloud Storage
    GCP_STORAGE_BUCKET: Optional[str] = Field(default=None, env="GCP_STORAGE_BUCKET")
    GCP_PROJECT_ID: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    GCP_CREDENTIALS_PATH: Optional[str] = Field(default=None, env="GCP_CREDENTIALS_PATH")
    
    # Analytics and Monitoring
    ANALYTICS_ENABLED: bool = Field(default=False, env="ANALYTICS_ENABLED")
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, env="GOOGLE_ANALYTICS_ID")
    HOTJAR_ID: Optional[str] = Field(default=None, env="HOTJAR_ID")
    
    # Error Tracking
    ERROR_TRACKING_ENABLED: bool = Field(default=False, env="ERROR_TRACKING_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    SENTRY_SAMPLE_RATE: float = Field(default=1.0, env="SENTRY_SAMPLE_RATE")
    
    # Search Service
    SEARCH_SERVICE_ENABLED: bool = Field(default=False, env="SEARCH_SERVICE_ENABLED")
    ELASTICSEARCH_URL: Optional[str] = Field(default=None, env="ELASTICSEARCH_URL")
    ELASTICSEARCH_INDEX: str = Field(default="craftyx_posts", env="ELASTICSEARCH_INDEX")
    ELASTICSEARCH_USERNAME: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    
    # CDN Configuration
    CDN_ENABLED: bool = Field(default=False, env="CDN_ENABLED")
    CDN_URL: Optional[str] = Field(default=None, env="CDN_URL")
    CLOUDFLARE_API_KEY: Optional[str] = Field(default=None, env="CLOUDFLARE_API_KEY")
    CLOUDFLARE_ZONE_ID: Optional[str] = Field(default=None, env="CLOUDFLARE_ZONE_ID")
    
    # Push Notifications
    PUSH_NOTIFICATIONS_ENABLED: bool = Field(default=False, env="PUSH_NOTIFICATIONS_ENABLED")
    FIREBASE_SERVER_KEY: Optional[str] = Field(default=None, env="FIREBASE_SERVER_KEY")
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, env="FIREBASE_PROJECT_ID")
    
    # Social Media Integration
    SOCIAL_SHARING_ENABLED: bool = Field(default=True, env="SOCIAL_SHARING_ENABLED")
    TWITTER_API_KEY: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    FACEBOOK_APP_ID: Optional[str] = Field(default=None, env="FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET: Optional[str] = Field(default=None, env="FACEBOOK_APP_SECRET")
    
    # Payment Processing
    PAYMENTS_ENABLED: bool = Field(default=False, env="PAYMENTS_ENABLED")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Content Moderation
    CONTENT_MODERATION_ENABLED: bool = Field(default=False, env="CONTENT_MODERATION_ENABLED")
    PERSPECTIVE_API_KEY: Optional[str] = Field(default=None, env="PERSPECTIVE_API_KEY")
    
    @validator("SMTP_PORT")
    def validate_smtp_port(cls, v):
        if v not in [25, 465, 587, 2525]:
            raise ValueError("SMTP_PORT must be one of: 25, 465, 587, 2525")
        return v
    
    @validator("OPENAI_TEMPERATURE")
    def validate_temperature(cls, v):
        if v < 0.0 or v > 2.0:
            raise ValueError("OPENAI_TEMPERATURE must be between 0.0 and 2.0")
        return v
    
    @validator("SENTRY_SAMPLE_RATE")
    def validate_sample_rate(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("SENTRY_SAMPLE_RATE must be between 0.0 and 1.0")
        return v
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email service configuration."""
        base_config = {
            "provider": self.EMAIL_PROVIDER,
            "from_name": self.EMAIL_FROM_NAME,
            "from_address": self.EMAIL_FROM_ADDRESS,
            "reply_to": self.EMAIL_REPLY_TO,
            "template_dir": self.EMAIL_TEMPLATE_DIR,
        }
        
        if self.EMAIL_PROVIDER == EmailProvider.SMTP:
            base_config.update({
                "smtp": {
                    "host": self.SMTP_HOST,
                    "port": self.SMTP_PORT,
                    "username": self.SMTP_USERNAME,
                    "password": self.SMTP_PASSWORD,
                    "use_tls": self.SMTP_USE_TLS,
                    "use_ssl": self.SMTP_USE_SSL,
                    "timeout": self.SMTP_TIMEOUT,
                }
            })
        elif self.EMAIL_PROVIDER == EmailProvider.SENDGRID:
            base_config.update({
                "sendgrid": {
                    "api_key": self.SENDGRID_API_KEY,
                    "templates": {
                        "welcome": self.SENDGRID_TEMPLATE_ID_WELCOME,
                        "reset": self.SENDGRID_TEMPLATE_ID_RESET,
                    }
                }
            })
        elif self.EMAIL_PROVIDER == EmailProvider.MAILGUN:
            base_config.update({
                "mailgun": {
                    "api_key": self.MAILGUN_API_KEY,
                    "domain": self.MAILGUN_DOMAIN,
                    "base_url": self.MAILGUN_BASE_URL,
                }
            })
        
        return base_config
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI service configuration."""
        if not self.AI_ENABLED:
            return {"enabled": False}
        
        config = {
            "enabled": True,
            "provider": self.AI_PROVIDER,
            "content_generation": self.CONTENT_GENERATION_ENABLED,
            "image_generation": self.IMAGE_GENERATION_ENABLED,
            "embedding_generation": self.EMBEDDING_GENERATION_ENABLED,
        }
        
        if self.AI_PROVIDER == AIProvider.OPENAI:
            config["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "organization": self.OPENAI_ORGANIZATION,
                "models": {
                    "text": self.OPENAI_MODEL_TEXT,
                    "embedding": self.OPENAI_MODEL_EMBEDDING,
                    "image": self.OPENAI_MODEL_IMAGE,
                },
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "temperature": self.OPENAI_TEMPERATURE,
                "timeout": self.OPENAI_TIMEOUT,
            }
        elif self.AI_PROVIDER == AIProvider.ANTHROPIC:
            config["anthropic"] = {
                "api_key": self.ANTHROPIC_API_KEY,
                "model": self.ANTHROPIC_MODEL,
                "max_tokens": self.ANTHROPIC_MAX_TOKENS,
            }
        
        return config
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get cloud storage configuration."""
        if not self.CLOUD_STORAGE_ENABLED:
            return {"enabled": False}
        
        config = {
            "enabled": True,
            "provider": self.CLOUD_STORAGE_PROVIDER,
        }
        
        if self.CLOUD_STORAGE_PROVIDER == CloudProvider.AWS:
            config["aws_s3"] = {
                "bucket": self.AWS_S3_BUCKET,
                "region": self.AWS_S3_REGION,
                "access_key": self.AWS_S3_ACCESS_KEY,
                "secret_key": self.AWS_S3_SECRET_KEY,
                "endpoint_url": self.AWS_S3_ENDPOINT_URL,
                "use_ssl": self.AWS_S3_USE_SSL,
                "custom_domain": self.AWS_S3_CUSTOM_DOMAIN,
            }
        elif self.CLOUD_STORAGE_PROVIDER == CloudProvider.GCP:
            config["gcp_storage"] = {
                "bucket": self.GCP_STORAGE_BUCKET,
                "project_id": self.GCP_PROJECT_ID,
                "credentials_path": self.GCP_CREDENTIALS_PATH,
            }
        
        return config
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring and analytics configuration."""
        return {
            "analytics": {
                "enabled": self.ANALYTICS_ENABLED,
                "google_analytics_id": self.GOOGLE_ANALYTICS_ID,
                "hotjar_id": self.HOTJAR_ID,
            },
            "error_tracking": {
                "enabled": self.ERROR_TRACKING_ENABLED,
                "sentry": {
                    "dsn": self.SENTRY_DSN,
                    "environment": self.SENTRY_ENVIRONMENT,
                    "sample_rate": self.SENTRY_SAMPLE_RATE,
                }
            }
        }
    
    def is_service_enabled(self, service: str) -> bool:
        """Check if a specific service is enabled."""
        service_flags = {
            "email": True,  # Email is always enabled
            "ai": self.AI_ENABLED,
            "storage": self.CLOUD_STORAGE_ENABLED,
            "analytics": self.ANALYTICS_ENABLED,
            "error_tracking": self.ERROR_TRACKING_ENABLED,
            "search": self.SEARCH_SERVICE_ENABLED,
            "cdn": self.CDN_ENABLED,
            "push_notifications": self.PUSH_NOTIFICATIONS_ENABLED,
            "payments": self.PAYMENTS_ENABLED,
            "content_moderation": self.CONTENT_MODERATION_ENABLED,
        }
        return service_flags.get(service, False)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global services configuration instance
services_config = ServicesConfig() 