import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pydantic import BaseModel, EmailStr, Field
import aiosmtplib

from core.config import get_settings
from core.exceptions import EmailServiceError, TemplateNotFoundError

logger = logging.getLogger(__name__)


class EmailTemplate(BaseModel):
    subject: str
    html_body: str
    text_body: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)


class EmailMessage(BaseModel):
    to_email: EmailStr
    subject: str
    html_body: str
    text_body: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)


class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.template_dir = Path(__file__).parent.parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send email using SMTP configuration."""
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.settings.SMTP_FROM_EMAIL
            msg["To"] = message.to_email
            msg["Subject"] = message.subject

            if message.text_body:
                text_part = MIMEText(message.text_body, "plain")
                msg.attach(text_part)

            html_part = MIMEText(message.html_body, "html")
            msg.attach(html_part)

            await aiosmtplib.send(
                msg,
                hostname=self.settings.SMTP_HOST,
                port=self.settings.SMTP_PORT,
                username=self.settings.SMTP_USERNAME,
                password=self.settings.SMTP_PASSWORD,
                use_tls=self.settings.SMTP_USE_TLS,
            )
            
            logger.info(f"Email sent successfully to {message.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {message.to_email}: {str(e)}")
            raise EmailServiceError(f"Failed to send email: {str(e)}")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> EmailTemplate:
        """Render email template with context."""
        try:
            html_template = self.jinja_env.get_template(f"{template_name}.html")
            html_body = html_template.render(context)
            
            subject_template = self.jinja_env.get_template(f"{template_name}_subject.txt")
            subject = subject_template.render(context).strip()
            
            text_body = None
            try:
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                text_body = text_template.render(context)
            except TemplateNotFound:
                pass

            return EmailTemplate(
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except TemplateNotFound as e:
            raise TemplateNotFoundError(f"Template not found: {template_name}")

    async def send_verification_email(self, email: str, token: str, user_name: str) -> bool:
        """Send email verification email."""
        context = {
            "user_name": user_name,
            "verification_url": f"{self.settings.FRONTEND_URL}/verify-email?token={token}",
            "app_name": self.settings.APP_NAME,
            "support_email": self.settings.SMTP_FROM_EMAIL
        }
        
        template = self.render_template("verification", context)
        message = EmailMessage(
            to_email=email,
            subject=template.subject,
            html_body=template.html_body,
            text_body=template.text_body
        )
        
        return await self.send_email(message)

    async def send_welcome_email(self, email: str, user_name: str) -> bool:
        """Send welcome email after successful verification."""
        context = {
            "user_name": user_name,
            "app_name": self.settings.APP_NAME,
            "login_url": f"{self.settings.FRONTEND_URL}/login",
            "support_email": self.settings.SMTP_FROM_EMAIL
        }
        
        template = self.render_template("welcome", context)
        message = EmailMessage(
            to_email=email,
            subject=template.subject,
            html_body=template.html_body,
            text_body=template.text_body
        )
        
        return await self.send_email(message)

    async def send_password_reset_email(self, email: str, token: str, user_name: str) -> bool:
        """Send password reset email."""
        context = {
            "user_name": user_name,
            "reset_url": f"{self.settings.FRONTEND_URL}/reset-password?token={token}",
            "app_name": self.settings.APP_NAME,
            "support_email": self.settings.SMTP_FROM_EMAIL
        }
        
        template = self.render_template("password_reset", context)
        message = EmailMessage(
            to_email=email,
            subject=template.subject,
            html_body=template.html_body,
            text_body=template.text_body
        )
        
        return await self.send_email(message)


# Dependency injection
async def get_email_service() -> EmailService:
    return EmailService() 