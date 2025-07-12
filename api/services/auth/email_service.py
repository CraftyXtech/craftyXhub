import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiosmtplib

from core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.smtp_config = self.settings.get_email_config()
    
    def _create_verification_email_content(self, user_name: str, verification_url: str) -> str:
        """Create verification email content."""
        return f"""CraftyXhub - Email Verification
====================================

Hi {user_name},

Welcome to CraftyXhub! We're excited to have you join our community of creators and innovators.

To get started, please verify your email address by clicking the link below:

{verification_url}

This verification link will expire in 24 hours for security reasons.

If you didn't create an account with CraftyXhub, please ignore this email.

Best regards,
The CraftyXhub Team

---
This is an automated email. Please do not reply to this message."""

    def _create_welcome_email_content(self, user_name: str) -> str:
        """Create welcome email content."""
        return f"""CraftyXhub - Welcome to the Community!
=========================================

Hi {user_name},

Congratulations! Your email has been successfully verified and your CraftyXhub account is now active.

Welcome to our community of creators, innovators, and craft enthusiasts! Here's what you can do next:

• Explore featured posts and discover amazing content
• Create your first post and share your projects
• Follow other creators and topics you're interested in
• Join discussions in the comments section
• Customize your profile to showcase your work

We're thrilled to have you as part of the CraftyXhub family. If you have any questions or need help getting started, feel free to reach out to our support team.

Happy crafting!

Best regards,
The CraftyXhub Team

---
This is an automated email. Please do not reply to this message."""

    def _create_password_reset_email_content(self, user_name: str, reset_url: str) -> str:
        """Create password reset email content."""
        return f"""CraftyXhub - Password Reset Request
====================================

Hi {user_name},

We received a request to reset your password for your CraftyXhub account.

To reset your password, click the link below:

{reset_url}

This password reset link will expire in 1 hour for security reasons.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

For security reasons, please ensure you:
• Use a strong, unique password
• Don't share your password with anyone
• Log out from shared devices

Best regards,
The CraftyXhub Team

---
This is an automated email. Please do not reply to this message."""

    async def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send email using SMTP."""
        try:
            message = MIMEText(content, 'plain', 'utf-8')
            message['Subject'] = subject
            message['From'] = self.smtp_config.get('from_email', 'noreply@craftyxhub.com')
            message['To'] = to_email
            
            # Send email using aiosmtplib for async support
            await aiosmtplib.send(
                message,
                hostname=self.smtp_config.get('server', 'localhost'),
                port=self.smtp_config.get('port', 587),
                username=self.smtp_config.get('username'),
                password=self.smtp_config.get('password'),
                start_tls=self.smtp_config.get('use_tls', True)
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_verification_email(self, email: str, token: str, user_name: str) -> bool:
        """Send email verification message."""
        verification_url = f"{self.settings.frontend_url}/verify-email?token={token}"
        content = self._create_verification_email_content(user_name, verification_url)
        
        return await self.send_email(
            to_email=email,
            subject="Verify Your CraftyXhub Account",
            content=content
        )
    
    async def send_welcome_email(self, email: str, user_name: str) -> bool:
        """Send welcome email after successful verification."""
        content = self._create_welcome_email_content(user_name)
        
        return await self.send_email(
            to_email=email,
            subject="Welcome to CraftyXhub!",
            content=content
        )
    
    async def send_password_reset_email(self, email: str, token: str, user_name: str) -> bool:
        """Send password reset email."""
        reset_url = f"{self.settings.frontend_url}/reset-password?token={token}"
        content = self._create_password_reset_email_content(user_name, reset_url)
        
        return await self.send_email(
            to_email=email,
            subject="Reset Your CraftyXhub Password",
            content=content
        )


# Dependency function
async def get_email_service() -> EmailService:
    """Dependency to get email service instance."""
    return EmailService() 