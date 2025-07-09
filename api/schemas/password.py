"""
Password Management Schemas for CraftyXhub API

Pydantic schemas for password reset, change, and confirmation
following SubPRD-PasswordManagement.md specifications.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class PasswordResetRequest(BaseModel):
    """Request schema for password reset."""
    email: EmailStr = Field(..., description="User email address")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com"
            }
        }
    }


class PasswordResetResponse(BaseModel):
    """Response schema for password reset request."""
    message: str = Field(..., description="Success message")
    email: EmailStr = Field(..., description="Email where reset link was sent")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Password reset link sent to your email.",
                "email": "user@example.com"
            }
        }
    }


class PasswordResetConfirm(BaseModel):
    """Request schema for confirming password reset."""
    token: str = Field(..., min_length=32, description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "abc123def456ghi789jkl012mno345pqr678stu901",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!"
            }
        }
    }


class PasswordResetConfirmResponse(BaseModel):
    """Response schema for successful password reset."""
    message: str = Field(..., description="Success message")
    login_required: bool = Field(default=True, description="Whether user needs to login again")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Password reset successfully. Please log in with your new password.",
                "login_required": True
            }
        }
    }


class PasswordChange(BaseModel):
    """Request schema for changing password while authenticated."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        
        return v
    
    @validator('new_password')
    def password_different_from_current(cls, v, values):
        """Ensure new password is different from current password."""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!"
            }
        }
    }


class PasswordChangeResponse(BaseModel):
    """Response schema for successful password change."""
    message: str = Field(..., description="Success message")
    token_revoked: bool = Field(default=True, description="Whether existing tokens were revoked")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Password changed successfully. Please log in again.",
                "token_revoked": True
            }
        }
    }


class PasswordConfirm(BaseModel):
    """Request schema for password confirmation."""
    password: str = Field(..., description="Current password for confirmation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "CurrentPassword123!"
            }
        }
    }


class PasswordConfirmResponse(BaseModel):
    """Response schema for password confirmation."""
    confirmed: bool = Field(..., description="Whether password was confirmed")
    valid_until: Optional[str] = Field(None, description="Confirmation validity timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "confirmed": True,
                "valid_until": "2024-01-01T13:00:00Z"
            }
        }
    }


class PasswordStrengthCheck(BaseModel):
    """Request schema for password strength validation."""
    password: str = Field(..., description="Password to validate")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "TestPassword123!"
            }
        }
    }


class PasswordStrengthResponse(BaseModel):
    """Response schema for password strength validation."""
    is_strong: bool = Field(..., description="Whether password meets strength requirements")
    score: int = Field(..., ge=0, le=100, description="Password strength score (0-100)")
    feedback: list[str] = Field(default=[], description="List of improvement suggestions")
    requirements_met: dict = Field(..., description="Breakdown of requirement compliance")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "is_strong": True,
                "score": 85,
                "feedback": ["Consider using a longer password"],
                "requirements_met": {
                    "min_length": True,
                    "has_uppercase": True,
                    "has_lowercase": True,
                    "has_number": True,
                    "has_special_char": True
                }
            }
        }
    }


class PasswordHistoryCheck(BaseModel):
    """Internal schema for password history validation."""
    password: str = Field(..., description="Password to check against history")
    user_id: str = Field(..., description="User ID for history lookup")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "NewPassword123!",
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    } 