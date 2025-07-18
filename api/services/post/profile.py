from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session, joinedload
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

    @staticmethod
    async def create_profile(
            db: get_db_session,
            profile_data: ProfileCreate,
            user_id: int,
            avatar: UploadFile = None
    ):
        result = await db.execute(select(Profile).where(Profile.user_id == user_id))
        existing_profile = result.scalar_one_or_none()

        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists")

        avatar_url = None
        if avatar:
            avatar_url = await ProfileService._save_avatar(avatar)

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

    @staticmethod
    async def update_profile(
            db: get_db_session,
            user_uuid: str,
            profile_data: ProfileUpdate,
            avatar: UploadFile = None,
            current_user: User = None
    ):
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
            # Delete old avatar if exists
            if profile.avatar:
                ProfileService._delete_avatar(profile.avatar)
            profile.avatar = await ProfileService._save_avatar(avatar)

        for field, value in profile_data.dict(exclude_unset=True).items():
            if field != "avatar":
                setattr(profile, field, value)

        await db.commit()
        await db.refresh(profile)
        return ProfileResponse.from_orm(profile)

    @staticmethod
    async def delete_profile(db: Session, user_uuid: str, current_user: User):
        result = await db.execute(select(User).where(User.uuid == user_uuid))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this profile")

        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if not profile:
            return False

        # Delete avatar file if exists
        if profile.avatar:
            ProfileService._delete_avatar(profile.avatar)

        db.delete(profile)
        db.commit()
        return True

    @staticmethod
    async def _save_avatar(avatar: UploadFile) -> str:
        os.makedirs(ProfileService.UPLOAD_DIR, exist_ok=True)
        file_extension = Path(avatar.filename).suffix
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(ProfileService.UPLOAD_DIR, file_name)

        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await avatar.read()
            await out_file.write(content)

        return file_path

    @staticmethod
    def _delete_avatar(file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting avatar: {e}")