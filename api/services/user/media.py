from fastapi import HTTPException, status
from fastapi import UploadFile
from typing import List, Optional
import os
import uuid
import aiofiles
from models.user import Media, MediaType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  
from uuid import UUID


class MediaService:
    upload_dir = "uploads/media"  

    @staticmethod
    async def upload_media(db_session: AsyncSession, user_id: int, file: UploadFile, description: Optional[str] = None) -> Media:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

        mime_type = file.content_type
        file_ext = file.filename.split('.')[-1].lower()
        media_type = MediaService._determine_media_type(mime_type, file_ext)

        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(MediaService.upload_dir, unique_filename)

        os.makedirs(MediaService.upload_dir, exist_ok=True)

        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {str(e)}")

        media = Media(
            user_id=user_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=media_type,
            file_size=len(content),
            mime_type=mime_type,
            description=description
        )

        db_session.add(media)
        await db_session.commit()
        await db_session.refresh(media)
        return media

    @staticmethod
    async def get_user_media(db_session: AsyncSession, user_id: int) -> List[Media]:
        return (await db_session.execute(select(Media).filter(Media.user_id == user_id))).scalars().all()

    @staticmethod
    async def get_media_by_uuid(db_session: AsyncSession, media_uuid: UUID) -> Optional[Media]:
        media = (await db_session.execute(select(Media).filter(Media.uuid == media_uuid))).scalars().first()
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
        return media
    
    @staticmethod
    async def update_media(db_session: AsyncSession, media_uuid: UUID, user_id: int, description: Optional[str]) -> Media:
        media = await MediaService.get_media_by_uuid(db_session, media_uuid)
        if media.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this media")

        media.description = description
        db_session.add(media)
        await db_session.commit()
        await db_session.refresh(media)
        return media

    @staticmethod
    async def delete_media(db_session: AsyncSession, media_uuid: uuid, user_id: int) -> None:
        media = await MediaService.get_media_by_uuid(db_session, media_uuid)
        if media.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this media")

        # Delete file from storage
        try:
            if os.path.exists(media.file_path):
                os.remove(media.file_path)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file: {str(e)}")

        await db_session.delete(media)
        await db_session.commit()

    @staticmethod
    def _determine_media_type(mime_type: str, file_ext: str) -> MediaType:
        mime_type = mime_type.lower()
        if mime_type.startswith('image/'):
            return MediaType.IMAGE
        elif mime_type.startswith('video/'):
            return MediaType.VIDEO
        elif mime_type in ['application/pdf', 'text/plain'] or file_ext in ['pdf', 'txt', 'doc', 'docx']:
            return MediaType.DOCUMENT
        return MediaType.OTHER