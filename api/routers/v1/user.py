from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from database.connection import get_db_session
from services.user.auth import get_current_active_user
from models import User
from schemas.user import (
    UserFollowersResponse, 
    UserFollowingResponse, 
    FollowActionResponse
)
from services.user.user_follow import UserFollowService

router = APIRouter(prefix="/users", tags=["User Following"])

@router.post(
    "/{user_uuid}/follow", 
    response_model=FollowActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Follow a user",
    responses={
        200: {"description": "Successfully followed user"},
        400: {"description": "Cannot follow yourself"},
        404: {"description": "User not found"}
    }
)

async def follow_user(
    user_uuid: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
) -> FollowActionResponse:
 
    return await UserFollowService.follow_user(
        session=session,
        follower_id=current_user.id,
        followed_uuid=str(user_uuid)
    )

@router.post(
    "/{user_uuid}/follow", 
    response_model=FollowActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Unfollow a user",
    responses={
        200: {"description": "Successfully unfollowed user"},
        404: {"description": "User not found"}
    }
)

async def unfollow_user(
    user_uuid: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
) -> FollowActionResponse:

    return await UserFollowService.unfollow_user(
        session=session,
        follower_id=current_user.id,
        followed_uuid=str(user_uuid)
    )

@router.get(
    "/{user_uuid}/followers",
    response_model=UserFollowersResponse,
    summary="Get user's followers",
    responses={
        200: {"description": "List of followers"},
        404: {"description": "User not found"}
    }
)
async def get_user_followers(
    user_uuid: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user, use_cache=False)
) -> UserFollowersResponse:
    
    return await UserFollowService.get_followers(
        session=session,
        user_uuid=str(user_uuid),
        current_user_id=current_user.id,
        page=page,
        size=size
    )

@router.get(
    "/{user_uuid}/following",
    response_model=UserFollowingResponse,
    summary="Get users followed by this user",
    responses={
        200: {"description": "List of followed users"},
        404: {"description": "User not found"}
    }
)
async def get_user_following(
    user_uuid: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user, use_cache=False)
) -> UserFollowingResponse:

    return await UserFollowService.get_following(
        session=session,
        user_uuid=str(user_uuid),
        current_user_id=current_user.id,
        page=page,
        size=size
    )

