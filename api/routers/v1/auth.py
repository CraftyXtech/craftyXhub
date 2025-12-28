from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
from core.config import settings
from database.connection import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from models.user import User, PasswordResetToken, EmailVerificationToken
from schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, ResetPasswordRequest, AuthResult,
    PasswordResetRequestEmail, PasswordResetConfirm, EmailVerificationRequest, PasswordResetResponse
)
from services.user.auth import AuthService, get_current_active_user
from services.user.notification import NotificationService
from schemas.notification import NotificationType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from urllib.parse import urlencode


google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=f"{settings.API_BASE_URL}/v1/auth/google/callback",
    allow_insecure_http=False,
)

facebook_sso = FacebookSSO(
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    redirect_uri=f"{settings.API_BASE_URL}/v1/auth/facebook/callback",
    allow_insecure_http=False,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_db_session)
):
    existing_user = await AuthService.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await AuthService.get_user_by_username(session, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    hashed_password = AuthService.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password=hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    # Notify all admins about new user registration
    try:
        from models.user import UserRole
        
        admins_query = select(User.id).where(
            or_(User.role == UserRole.ADMIN, User.role == UserRole.MODERATOR)
        )
        admins_result = await session.execute(admins_query)
        admin_ids = [row[0] for row in admins_result.all()]

        for admin_id in admin_ids:
            await NotificationService.create_notification(
                session=session,
                recipient_id=admin_id,
                sender_id=db_user.id,
                notification_type=NotificationType.WELCOME,
                title="New User Registration",
                message=f"New user {db_user.username} ({db_user.email}) has registered",
                action_url=f"/admin/users/{db_user.uuid}"
            )
    except Exception as e:
        # Don't fail registration if notification fails
        print(f"Failed to send admin notification: {str(e)}")

    return db_user


@router.post("/login", response_model=Token)
async def login(
        user_credentials: UserLogin,
        session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.authenticate_user(
        session, user_credentials.email, user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    access_token = AuthService._issue_jwt(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
):
    user_data = {
        "uuid": current_user.uuid,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
    return user_data


@router.get("/user/{user_uuid}", response_model=UserResponse)
async def get_user_by_uuid(
        user_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.get_user_by_uuid(session, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    return user


@router.put("/user/{user_uuid}", response_model=UserResponse)
async def update_user_profile(
        user_uuid: str,
        full_name: Optional[str] = None,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.get_user_by_uuid(session, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    if full_name:
        user.full_name = full_name

    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(user)

    return user


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_active_user)
):
    return {"message": "Successfully logged out"}


@router.put("/reset-password")
async def reset_password(
        request: ResetPasswordRequest,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    if request.new_password != request.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )

    if not AuthService.verify_password(request.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    current_user.password = AuthService.get_password_hash(request.new_password)
    current_user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()

    return {"message": "Password updated successfully"}


# ============================================================================
# PUBLIC PASSWORD RESET FLOW (for users who forgot password)
# ============================================================================

@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
        request_data: PasswordResetRequestEmail,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Request password reset via email (public endpoint).
    Generates a token and would send it via email.
    For now, returns success regardless of whether email exists (security best practice).
    """
    user = await AuthService.get_user_by_email(session, request_data.email)
    
    if user:
        # Generate a secure token
        token = secrets.token_urlsafe(32)
        
        # Create password reset token (expires in 1 hour)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        )
        session.add(reset_token)
        await session.commit()
        
        # TODO: Send email with reset link
        # In production, you would send an email like:
        # reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        # await send_password_reset_email(user.email, reset_url)
        
        print(f"[DEV] Password reset token for {user.email}: {token}")
    
    # Always return success to prevent email enumeration attacks
    return PasswordResetResponse(
        message="If an account with that email exists, a password reset link has been sent.",
        success=True
    )


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
        request_data: PasswordResetConfirm,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Confirm password reset with token (public endpoint).
    Validates the token and updates the user's password.
    """
    # Find the token
    result = await session.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.token == request_data.token)
        .where(PasswordResetToken.used == False)
    )
    reset_token = result.scalar_one_or_none()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if reset_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Get the user
    user = await AuthService.get_user_by_id(session, reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Update password
    user.password = AuthService.get_password_hash(request_data.new_password)
    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Mark token as used
    reset_token.used = True
    
    await session.commit()
    
    return PasswordResetResponse(
        message="Password has been reset successfully. You can now log in with your new password.",
        success=True
    )


@router.post("/verify-email", response_model=PasswordResetResponse)
async def verify_email(
        request_data: EmailVerificationRequest,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Verify email address with token (public endpoint).
    """
    # Find the token
    result = await session.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token == request_data.token)
        .where(EmailVerificationToken.used == False)
    )
    verification_token = result.scalar_one_or_none()
    
    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Check if token is expired
    if verification_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Get the user and mark as verified
    user = await AuthService.get_user_by_id(session, verification_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    user.is_verified = True
    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Mark token as used
    verification_token.used = True
    
    await session.commit()
    
    return PasswordResetResponse(
        message="Email verified successfully!",
        success=True
    )

@router.get("/google/login")
async def google_login():
    try:
        async with google_sso:
            return await google_sso.get_login_redirect()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db_session)):
    async with google_sso:
        try:
            user_info = await google_sso.verify_and_process(request)
        except Exception as e:
            params = urlencode({"error": f"Google SSO failed: {str(e)}"})
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/failure?{params}")

        if not user_info or not user_info.email:
            params = urlencode({"error": "Missing email from Google profile"})
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/failure?{params}")

        token = await AuthService.login_with_social_profile(
            session=db,
            email=user_info.email,
            name=user_info.display_name,
            picture=user_info.picture,
            provider="google"
        )

        params = urlencode({
            "access_token": token,
            "token_type": "bearer",
            "expires_in": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
        })
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/success?{params}")


@router.get("/facebook/login")
async def facebook_login():
    try:
        async with facebook_sso:
            return await facebook_sso.get_login_redirect()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/facebook/callback")
async def facebook_callback(request: Request, db: AsyncSession = Depends(get_db_session)):
    async with facebook_sso:
        try:
            user_info = await facebook_sso.verify_and_process(request)
        except Exception as e:
            params = urlencode({"error": f"Facebook SSO failed: {str(e)}"})
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/failure?{params}")

        if not user_info or not user_info.email:
            params = urlencode({"error": "Missing email from Facebook profile"})
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/failure?{params}")

        token = await AuthService.login_with_social_profile(
            session=db,
            email=user_info.email,
            name=user_info.display_name,
            picture=user_info.picture,
            provider="facebook"
        )

        params = urlencode({
            "access_token": token,
            "token_type": "bearer",
            "expires_in": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
        })
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/success?{params}")
