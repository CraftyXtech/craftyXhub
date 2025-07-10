
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, PaginationParams
from dependencies.web_auth import get_optional_current_user, get_user_context
from models.user import User
from services.web.profile_service import WebProfileService
from schemas.web.profile import (
    UserDetailResponse, UserActivityStatsResponse, PostWithInteractionResponse,
    PaginatedPostsResponse, UserPreferencesRequest, UserPreferencesResponse,
    UserActivityResponse, UserProfileResponse, UserUpdateRequest, UserStatsResponse,
    UserFollowingResponse, UserSocialStatsResponse, ActivityFeedResponse,
    NotificationPreferencesRequest, NotificationPreferencesResponse,
    ProfileVisibilityRequest, ProfileVisibilityResponse
)

router = APIRouter(prefix="/profile", tags=["Web Profile"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view profile"
        )
    
    service = WebProfileService(db)
    
    # Get user profile
    profile_response = await service.get_user_profile(current_user.id, current_user)
    
    return profile_response


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_data: UserUpdateRequest,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to update profile"
        )
    
    service = WebProfileService(db)
    
    # Update user profile
    updated_profile = await service.update_user_profile(
        user_id=current_user.id,
        profile_data=profile_data,
        current_user=current_user
    )
    
    return updated_profile


@router.post("/me/avatar")
async def upload_user_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to upload avatar"
        )
    
    # Validate file type and size
    if avatar.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid file type. Only JPG, PNG, and GIF are allowed."
        )
    
    # Check file size (5MB limit)
    if avatar.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=422,
            detail="File too large. Maximum size is 5MB."
        )
    
    service = WebProfileService(db)
    
    # Upload and update avatar
    avatar_url = await service.upload_user_avatar(
        user_id=current_user.id,
        avatar_file=avatar
    )
    
    return {
        "avatar_url": avatar_url,
        "message": "Avatar uploaded successfully"
    }


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    timeframe: str = "all",  # day, week, month, year, all
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view statistics"
        )
    
    # Validate timeframe
    if timeframe not in ["day", "week", "month", "year", "all"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = WebProfileService(db)
    
    # Get user statistics
    stats_response = await service.get_user_statistics(
        user_id=current_user.id,
        timeframe=timeframe
    )
    
    return stats_response


@router.get("/me/posts", response_model=PaginatedPostsResponse)
async def get_user_posts(
    status: Optional[str] = None,  # published, draft, all
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view posts"
        )
    
    service = WebProfileService(db)
    
    # Get user posts
    posts_response = await service.get_user_posts(
        user_id=current_user.id,
        status=status,
        pagination=pagination,
        current_user=current_user
    )
    
    return posts_response


@router.get("/me/liked", response_model=PaginatedPostsResponse)
async def get_user_liked_posts(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view liked posts"
        )
    
    service = WebProfileService(db)
    
    # Get liked posts
    liked_posts = await service.get_user_liked_posts(
        user_id=current_user.id,
        pagination=pagination,
        current_user=current_user
    )
    
    return liked_posts


@router.get("/me/bookmarks", response_model=PaginatedPostsResponse)
async def get_user_bookmarked_posts(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view bookmarks"
        )
    
    service = WebProfileService(db)
    
    # Get bookmarked posts
    bookmarked_posts = await service.get_user_bookmarked_posts(
        user_id=current_user.id,
        pagination=pagination,
        current_user=current_user
    )
    
    return bookmarked_posts


@router.get("/me/activity", response_model=ActivityFeedResponse)
async def get_user_activity_feed(
    activity_type: Optional[str] = None,  # post, comment, like, bookmark
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view activity feed"
        )
    
    service = WebProfileService(db)
    
    # Get activity feed
    activity_response = await service.get_user_activity_history(
        user_id=current_user.id,
        activity_type=activity_type,
        pagination=pagination
    )
    
    return activity_response


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view preferences"
        )
    
    service = WebProfileService(db)
    
    # Get user preferences
    preferences_response = await service.get_user_preferences(current_user.id)
    
    return preferences_response


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_data: UserPreferencesRequest,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to update preferences"
        )
    
    service = WebProfileService(db)
    
    # Update user preferences
    updated_preferences = await service.update_user_preferences(
        user_id=current_user.id,
        preferences_data=preferences_data
    )
    
    return updated_preferences


@router.get("/me/notifications", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view notification preferences"
        )
    
    service = WebProfileService(db)
    
    # Get notification preferences
    notification_prefs = await service.get_notification_preferences(current_user.id)
    
    return notification_prefs


@router.put("/me/notifications", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    notification_data: NotificationPreferencesRequest,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to update notification preferences"
        )
    
    service = WebProfileService(db)
    
    # Update notification preferences
    updated_prefs = await service.update_notification_preferences(
        user_id=current_user.id,
        notification_data=notification_data
    )
    
    return updated_prefs


@router.get("/me/privacy", response_model=ProfileVisibilityResponse)
async def get_privacy_settings(
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to view privacy settings"
        )
    
    service = WebProfileService(db)
    
    # Get privacy settings
    privacy_settings = await service.get_privacy_settings(current_user.id)
    
    return privacy_settings


@router.put("/me/privacy", response_model=ProfileVisibilityResponse)
async def update_privacy_settings(
    privacy_data: ProfileVisibilityRequest,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to update privacy settings"
        )
    
    service = WebProfileService(db)
    
    # Update privacy settings
    updated_privacy = await service.update_privacy_settings(
        user_id=current_user.id,
        privacy_data=privacy_data
    )
    
    return updated_privacy


# Public profile endpoints (no /me prefix)
@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_public_user_profile(
    user_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebProfileService(db)
    
    # Get public user profile
    profile_response = await service.get_public_user_profile(
        user_id=user_id,
        viewer=current_user
    )
    
    if not profile_response:
        raise HTTPException(status_code=404, detail="User not found")
    
    return profile_response


@router.get("/users/{user_id}/posts", response_model=PaginatedPostsResponse)
async def get_public_user_posts(
    user_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebProfileService(db)
    
    # Get public user posts
    posts_response = await service.get_public_user_posts(
        user_id=user_id,
        pagination=pagination,
        viewer=current_user
    )
    
    return posts_response


@router.get("/users/{user_id}/stats", response_model=UserActivityStatsResponse)
async def get_public_user_stats(
    user_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebProfileService(db)
    
    # Get public user statistics
    stats_response = await service.get_public_user_stats(
        user_id=user_id,
        viewer=current_user
    )
    
    if not stats_response:
        raise HTTPException(status_code=404, detail="User not found")
    
    return stats_response


@router.delete("/me/account")
async def delete_user_account(
    confirm: bool = False,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to delete account"
        )
    
    if not confirm:
        raise HTTPException(
            status_code=422,
            detail="Account deletion must be confirmed"
        )
    
    service = WebProfileService(db)
    
    # Delete user account
    success = await service.delete_user_account(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )
    
    return {"message": "Account deleted successfully"} 