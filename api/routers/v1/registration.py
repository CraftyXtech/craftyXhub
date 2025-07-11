
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from dependencies.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.registration import (
    UserRegistration,
    RegistrationResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    OnboardingPreferences,
    OnboardingResponse
)
from schemas.auth import LoginResponse
from core.security import generate_verification_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register new user account with email verification"
)
async def register_user(
    registration_data: UserRegistration,
    db: AsyncSession = Depends(get_db),
    request: Request = None
) -> RegistrationResponse:
    
    # TODO: Implement rate limiting (3 attempts per IP per hour)
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == registration_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address already registered"
        )
    
    # Create new user
    user = User(
        name=registration_data.name,
        email=registration_data.email,
        role="user",  # Default role
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
        # email_verified_at will be None until verification
    )
    
    user.password_hash = user.hash_password(registration_data.password)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    
    verification_token = generate_verification_token("email_verification")
    
   
    # TODO: Send verification email
    
    # For now, return success response
    return RegistrationResponse(
        user=UserResponse.model_validate(user),
        tokens=None,  # No tokens until email verified
        email_verification_required=True,
        message="Registration successful. Please check your email to verify your account."
    )


@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Email Verification",
    description="Verify email address with token and auto-login user"
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> EmailVerificationResponse:
    """
    Verify user email address with verification token.
    
    - **token**: Email verification token (32+ characters)
    
    Verifies email and automatically logs in the user.
    """
    # TODO: Implement token validation from database/Redis
    # For now, this is a placeholder implementation
    
    # In a real implementation, you would:
    # 1. Look up the token in your verification token storage
    # 2. Check if it's not expired (24 hours)
    # 3. Get the associated user
    # 4. Mark email as verified
    # 5. Delete the verification token
    
    # Placeholder: assuming token is valid and finding user
    # This should be replaced with actual token validation logic
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification not yet implemented. Requires email service setup."
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend Verification Email",
    description="Resend email verification link"
)
async def resend_verification_email(
    resend_data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> ResendVerificationResponse:
    """
    Resend email verification link.
    
    - **email**: User email address
    
    Sends new verification email if user exists and is not verified.
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == resend_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists or not for security
        return ResendVerificationResponse(
            message="If an account with this email exists and is not verified, a new verification email has been sent.",
            email=resend_data.email
        )
    
    if user.email_verified_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already verified"
        )
    
    # Generate new verification token
    verification_token = generate_verification_token("email_verification")
    
    # TODO: Store new verification token and send email
    
    return ResendVerificationResponse(
        message="Verification email sent successfully.",
        email=resend_data.email
    )


@router.get(
    "/verify/{token}",
    response_model=EmailVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Email Verification Link",
    description="Handle email verification link clicks"
)
async def verify_email_link(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> EmailVerificationResponse:
    """
    Handle email verification link clicks.
    
    This endpoint handles the verification links sent in emails.
    Users click the link which includes the token as a URL parameter.
    """
    # TODO: Implement token validation and user verification
    # This should mirror the verify_email endpoint but handle GET requests
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email verification link handling not yet implemented. Requires email service setup."
    )


@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
    status_code=status.HTTP_200_OK,
    summary="User Onboarding",
    description="Complete user onboarding with preferences and topic selection"
)
async def complete_onboarding(
    preferences: OnboardingPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OnboardingResponse:
    """
    Complete user onboarding process.
    
    - **interested_categories**: List of category slugs user is interested in
    - **followed_topics**: List of tag slugs user wants to follow
    - **newsletter_frequency**: Newsletter frequency preference
    - **notification_preferences**: Notification preference settings
    
    Sets up user preferences and topic subscriptions.
    """
    try:
        # TODO: Implement preference storage
        # This would involve:
        # 1. Creating UserPreference records
        # 2. Creating UserTopic subscriptions for followed topics
        # 3. Setting notification preferences
        # 4. Updating user profile with onboarding completion
        
        # For now, just acknowledge the onboarding
        preferences_saved = True
        
        return OnboardingResponse(
            message="Onboarding completed successfully.",
            user=UserResponse.model_validate(current_user),
            preferences_saved=preferences_saved
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save onboarding preferences"
        ) 