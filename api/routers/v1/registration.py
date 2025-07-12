
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from services.auth.email_service import get_email_service, EmailService
from services.auth.token_service import get_token_service, TokenService
from services.auth.registration_service import RegistrationService
from schemas.registration import (
    UserRegistration, 
    EmailVerificationRequest, 
    ResendVerificationRequest,
    ResendVerificationResponse
)
from schemas.user import UserResponse
from core.exceptions import UserAlreadyExistsError, UserNotFoundError, TokenValidationError, TokenExpiredError, TokenNotFoundError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account and send email verification",
    responses={
        201: {
            "description": "User registered successfully",
            "model": UserResponse
        },
        409: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Registration failed"}
                }
            }
        }
    }
)
async def register_user(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Register a new user account.
    
    This endpoint:
    - Validates user input (email format, password strength, etc.)
    - Checks if email is already registered
    - Creates a new user account
    - Sends email verification link
    - Returns user information (without sensitive data)
    
    **Password Requirements:**
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one number
    - At least one special character
    """
    try:
        return await RegistrationService.register_user(
            db=db, 
            user_data=user_data,
            email_service=email_service,
            token_service=token_service
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/verify-email", 
    response_model=UserResponse,
    summary="Verify email address",
    description="Verify user email address using verification token",
    responses={
        200: {
            "description": "Email verified successfully",
            "model": UserResponse
        },
        400: {
            "description": "Invalid token format",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token format"}
                }
            }
        },
        404: {
            "description": "Invalid verification token or user not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid verification token"}
                }
            }
        },
        410: {
            "description": "Verification token has expired",
            "content": {
                "application/json": {
                    "example": {"detail": "Verification token has expired"}
                }
            }
        }
    }
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Verify user email address.
    
    This endpoint:
    - Validates the verification token
    - Marks the user's email as verified
    - Activates the user account
    - Sends a welcome email
    - Returns updated user information
    
    **Note:** Verification tokens expire after 24 hours.
    """
    try:
        return await RegistrationService.verify_email(
            db=db, 
            token=verification_data.token,
            token_service=token_service,
            email_service=email_service
        )
    except TokenNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token"
        )
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Verification token has expired"
        )
    except TokenValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format"
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post(
    "/resend-verification", 
    response_model=ResendVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend email verification link to user",
    responses={
        200: {
            "description": "Response about verification email status",
            "model": ResendVerificationResponse
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
async def resend_verification(
    resend_data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Resend email verification link.
    
    This endpoint:
    - Checks if user exists
    - Revokes any existing verification tokens
    - Generates a new verification token
    - Sends new verification email
    - Returns status message
    
    **Note:** If email is already verified, returns appropriate message.
    """
    try:
        was_sent = await RegistrationService.resend_verification(
            db=db, 
            email=resend_data.email,
            token_service=token_service,
            email_service=email_service
        )
        if was_sent:
            return ResendVerificationResponse(
                message="Verification email sent successfully"
            )
        else:
            return ResendVerificationResponse(
                message="Email already verified"
            )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) 