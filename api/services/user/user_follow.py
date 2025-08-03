from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func
from models import User
from models.base import user_follows
from schemas.user import FollowActionResponse, UserFollowersResponse, UserFollowingResponse, UserResponse
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Tuple, Union
import math


class UserFollowService:

    @staticmethod
    async def follow_user(
            session: AsyncSession,
            follower_id: int,
            followed_uuid: str
    ) -> FollowActionResponse:
        try:
            followed_user = await UserFollowService._get_user_by_uuid(session, followed_uuid)

            if follower_id == followed_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot follow yourself"
                )

            if await UserFollowService.is_following(session, follower_id, followed_user.id):
                return FollowActionResponse(
                    success=False,
                    message="Already following this user",
                    is_following=True,
                    follower_count=await UserFollowService.count_followers(session, followed_user.id)
                )

            await UserFollowService._create_follow_relationship(session, follower_id, followed_user.id)
            await session.refresh(followed_user)

            return FollowActionResponse(
                success=True,
                message="Successfully followed user",
                is_following=True,
                follower_count=await UserFollowService.count_followers(session, followed_user.id)
            )
        except HTTPException:
            raise
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Follow relationship violates database constraints"
            )
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def unfollow_user(
            session: AsyncSession,
            follower_id: int,
            followed_uuid: str
    ) -> FollowActionResponse:
        try:
            followed_user = await UserFollowService._get_user_by_uuid(session, followed_uuid)

            if not await UserFollowService.is_following(session, follower_id, followed_user.id):
                return FollowActionResponse(
                    success=False,
                    message="Not following this user",
                    is_following=False,
                    follower_count=await UserFollowService.count_followers(session, followed_user.id)
                )

            await UserFollowService._delete_follow_relationship(session, follower_id, followed_user.id)
            await session.refresh(followed_user)

            return FollowActionResponse(
                success=True,
                message="Successfully unfollowed user",
                is_following=False,
                follower_count=await UserFollowService.count_followers(session, followed_user.id)
            )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def get_followers(
            session: AsyncSession,
            user_uuid: str,
            current_user_id: int,
            page: int = 1,
            size: int = 10
    ) -> UserFollowersResponse:
        try:
            user = await UserFollowService._get_user_by_uuid(session, user_uuid)
            followers, total = await UserFollowService._get_followers_data(session, user.id, page, size)

            follower_responses = await UserFollowService._build_user_responses(
                session, followers, current_user_id)

            return UserFollowService._build_paginated_response(
                follower_responses, total, page, size, UserFollowersResponse, "followers"
            )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def get_following(
            session: AsyncSession,
            user_uuid: str,
            current_user_id: int,
            page: int = 1,
            size: int = 10
    ) -> UserFollowingResponse:
        try:
            user = await UserFollowService._get_user_by_uuid(session, user_uuid)
            following, total = await UserFollowService._get_following_data(session, user.id, page, size)

            following_responses = await UserFollowService._build_user_responses(
                session, following, current_user_id)

            return UserFollowService._build_paginated_response(
                following_responses, total, page, size, UserFollowingResponse, "following"
            )
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def _get_user_by_uuid(session: AsyncSession, uuid: str) -> User:
        try:
            result = await session.execute(select(User).where(User.uuid == uuid))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def is_following(
            session: AsyncSession,
            follower_id: int,
            followed_id: int
    ) -> bool:
        try:
            result = await session.execute(
                select(user_follows).where(
                    and_(
                        user_follows.c.follower_id == follower_id,
                        user_follows.c.followed_id == followed_id
                    )
                )
            )
            return result.first() is not None
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def count_followers(session: AsyncSession, user_id: int) -> int:
        try:
            result = await session.execute(
                select(func.count()).where(user_follows.c.followed_id == user_id)
            )
            return result.scalar()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def _create_follow_relationship(
            session: AsyncSession,
            follower_id: int,
            followed_id: int
    ) -> None:
        try:
            await session.execute(
                user_follows.insert().values(
                    follower_id=follower_id,
                    followed_id=followed_id
                )
            )
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise

    @staticmethod
    async def _delete_follow_relationship(
            session: AsyncSession,
            follower_id: int,
            followed_id: int
    ) -> None:
        try:
            await session.execute(
                user_follows.delete().where(
                    and_(
                        user_follows.c.follower_id == follower_id,
                        user_follows.c.followed_id == followed_id
                    )
                )
            )
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise

    @staticmethod
    async def _get_followers_data(
            session: AsyncSession,
            user_id: int,
            page: int,
            size: int
    ) -> Tuple[List[User], int]:
        try:
            skip = (page - 1) * size
            query = (
                select(User)
                .join(user_follows, User.id == user_follows.c.follower_id)
                .where(user_follows.c.followed_id == user_id)
                .offset(skip)
                .limit(size)
                .options(selectinload(User.profile))
            )
            result = await session.execute(query)
            users = result.scalars().all()

            count = await session.scalar(
                select(func.count()).where(user_follows.c.followed_id == user_id)
            )

            return users, count
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise

    @staticmethod
    async def _get_following_data(
            session: AsyncSession,
            user_id: int,
            page: int,
            size: int
    ) -> Tuple[List[User], int]:
        try:
            skip = (page - 1) * size
            query = (
                select(User)
                .join(user_follows, User.id == user_follows.c.followed_id)
                .where(user_follows.c.follower_id == user_id)
                .offset(skip)
                .limit(size)
                .options(selectinload(User.profile))
            )
            result = await session.execute(query)
            users = result.scalars().all()

            count = await session.scalar(
                select(func.count()).where(user_follows.c.follower_id == user_id)
            )

            return users, count
        except SQLAlchemyError as e:
            raise
        except Exception as e:
            raise

    @staticmethod
    async def _build_user_responses(
            session: AsyncSession,
            users: List[User],
            current_user_id: int
    ) -> List[UserResponse]:
        try:
            responses = []
            for user in users:
                is_following = await UserFollowService.is_following(
                    session, current_user_id, user.id
                )

                user_data = {
                    "uuid": user.uuid,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "role": user.role,
                    "last_login": user.last_login,
                    "is_following": is_following,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                user_response = UserResponse(**user_data)
                responses.append(user_response)
            return responses
        except Exception as e:
            raise

    @staticmethod
    def _build_paginated_response(
            data: List[UserResponse],
            total: int,
            page: int,
            size: int,
            response_class: Union[UserFollowersResponse, UserFollowingResponse],
            data_key: str
    ) -> Union[UserFollowersResponse, UserFollowingResponse]:
        try:
            total_pages = math.ceil(total / size) if total > 0 else 1
            has_next = page < total_pages
            has_prev = page > 1

            response_data = {
                data_key: data,
                "total": total,
                "page": page,
                "size": size,
                "pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }

            return response_class(**response_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error building response"
            )