from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.user import ProfileCreate, ProfileUpdate, ProfileResponse
from models import Profile, User
from database.connection import get_db_session
from sqlmodel import select

import os
import uuid
import aiofiles
from pathlib import Path

class ProfileService:
    UPLOAD_DIR = "uploads/avatars"

    @staticmethod
    async def get_profile(db: get_db_session, user_uuid: str):
        try:
            result = await db.execute(select(User).where(User.uuid == user_uuid))
            user = result.scalar_one_or_none()

            if not user:
                return None

            result = await db.execute(
                select(Profile).options(joinedload(Profile.user)).where(Profile.user_id == user.id)
            )
            profile = result.scalar_one_or_none()

            if profile:
                return ProfileResponse.from_orm(profile)

            return None

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving profile"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving profile"
            )

    @staticmethod
    async def create_profile(
            db: get_db_session,
            profile_data: ProfileCreate,
            user_id: int,
            avatar: UploadFile = None
    ):
        avatar_url = None
        try:
            result = await db.execute(select(Profile).where(Profile.user_id == user_id))
            existing_profile = result.scalar_one_or_none()

            if existing_profile:
                raise HTTPException(status_code=400, detail="Profile already exists")

            if avatar:
                try:
                    avatar_url = await ProfileService._save_avatar(avatar)
                except Exception as avatar_error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to save avatar file"
                    )

            db_profile = Profile(
                user_id=user_id,
                avatar=avatar_url,
                bio=profile_data.bio,
                location=profile_data.location,
                website=profile_data.website,
                twitter_handle=profile_data.twitter_handle,
                github_handle=profile_data.github_handle,
                linkedin_handle=profile_data.linkedin_handle,
                birth_date=profile_data.birth_date
            )

            db.add(db_profile)
            await db.commit()
            await db.refresh(db_profile)

            return ProfileResponse.from_orm(db_profile)

        except HTTPException:
            if avatar_url:
                ProfileService._delete_avatar(avatar_url)
            raise
        except IntegrityError as e:
            await db.rollback()
            if avatar_url:
                ProfileService._delete_avatar(avatar_url)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile data violates database constraints"
            )
        except SQLAlchemyError as e:
            await db.rollback()
            if avatar_url:
                ProfileService._delete_avatar(avatar_url)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating profile"
            )
        except Exception as e:
            await db.rollback()
            if avatar_url:
                ProfileService._delete_avatar(avatar_url)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating profile"
            )

    @staticmethod
    async def update_profile(
            db: get_db_session,
            user_uuid: str,
            profile_data: ProfileUpdate,
            avatar: UploadFile = None,
            current_user: User = None
    ):
        old_avatar_path = None
        new_avatar_path = None

        try:
            result = await db.execute(select(User).where(User.uuid == user_uuid))
            user = result.scalar_one_or_none()

            if not user:
                return None

            if user.id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to update this profile")

            profile_result = await db.execute(
                select(Profile).options(joinedload(Profile.user)).where(Profile.user_id == user.id)
            )
            profile = profile_result.scalar_one_or_none()

            if not profile:
                return None

            if avatar:
                try:
                    old_avatar_path = profile.avatar  # Store old path before updating
                    new_avatar_path = await ProfileService._save_avatar(avatar)
                    profile.avatar = new_avatar_path
                except Exception as avatar_error:
                    logger.error(f"Error saving avatar for user {user_uuid}: {str(avatar_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to save avatar file"
                    )

            for field, value in profile_data.dict(exclude_unset=True).items():
                if field != "avatar":
                    setattr(profile, field, value)

            await db.commit()
            await db.refresh(profile)

            if avatar and old_avatar_path:
                ProfileService._delete_avatar(old_avatar_path)

            return ProfileResponse.from_orm(profile)

        except HTTPException:
            if new_avatar_path:
                ProfileService._delete_avatar(new_avatar_path)
            raise
        except IntegrityError as e:
            await db.rollback()
            if new_avatar_path:
                ProfileService._delete_avatar(new_avatar_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile data violates database constraints"
            )
        except SQLAlchemyError as e:
            await db.rollback()
            if new_avatar_path:
                ProfileService._delete_avatar(new_avatar_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating profile"
            )
        except Exception as e:
            await db.rollback()
            if new_avatar_path:
                ProfileService._delete_avatar(new_avatar_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating profile"
            )

    @staticmethod
    async def delete_profile(db: Session, user_uuid: str, current_user: User):
        try:
            result = await db.execute(select(User).where(User.uuid == user_uuid))
            user = result.scalar_one_or_none()

            if not user:
                return None

            if user.id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this profile")

            profile_result = await db.execute(select(Profile).where(Profile.user_id == user.id))
            profile = profile_result.scalar_one_or_none()

            if not profile:
                return False

            avatar_path = profile.avatar

            await db.delete(profile)
            await db.commit()

            if avatar_path:
                ProfileService._delete_avatar(avatar_path)

            return True

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting profile"
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting profile"
            )

    @staticmethod
    async def _save_avatar(avatar: UploadFile) -> str:
        try:
            if not avatar.filename:
                raise ValueError("No filename provided")

            os.makedirs(ProfileService.UPLOAD_DIR, exist_ok=True)

            file_extension = Path(avatar.filename).suffix
            if not file_extension:
                raise ValueError("File has no extension")

            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(ProfileService.UPLOAD_DIR, file_name)

            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await avatar.read()
                if not content:
                    raise ValueError("File is empty")
                await out_file.write(content)

            return file_path

        except ValueError as e:
            raise
        except OSError as e:
            raise Exception(f"Failed to save avatar: File system error")
        except Exception as e:
            raise Exception(f"Failed to save avatar: {str(e)}")

    @staticmethod
    def _delete_avatar(file_path: str):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)