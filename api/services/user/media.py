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
from sqlalchemy.exc import SQLAlchemyError, IntegrityError



class MediaService:
    upload_dir = "uploads/media"

    @staticmethod
    async def upload_media(db_session: AsyncSession, user_id: int, file: UploadFile,
                           description: Optional[str] = None) -> Media:
        file_path = None
        try:
            if not file.filename:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

            mime_type = file.content_type
            file_ext = file.filename.split('.')[-1].lower()
            media_type = MediaService._determine_media_type(mime_type, file_ext)

            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(MediaService.upload_dir, unique_filename)

            os.makedirs(MediaService.upload_dir, exist_ok=True)

            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                if not content:
                    raise ValueError("File is empty")
                await out_file.write(content)

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

        except HTTPException:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise
        except ValueError as e:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except OSError as e:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save file")
        except IntegrityError as e:
            await db_session.rollback()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Media data violates database constraints")
        except SQLAlchemyError as e:
            await db_session.rollback()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
        except Exception as e:
            await db_session.rollback()
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred")

    @staticmethod
    async def get_user_media(db_session: AsyncSession, user_id: int) -> List[Media]:
        try:
            result = await db_session.execute(select(Media).filter(Media.user_id == user_id))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred")

    @staticmethod
    async def get_media_by_uuid(db_session: AsyncSession, media_uuid: UUID) -> Optional[Media]:
        try:
            result = await db_session.execute(select(Media).filter(Media.uuid == media_uuid))
            media = result.scalars().first()
            if not media:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
            return media
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred")

    @staticmethod
    async def update_media(db_session: AsyncSession, media_uuid: UUID, user_id: int,
                           description: Optional[str]) -> Media:
        try:
            media = await MediaService.get_media_by_uuid(db_session, media_uuid)
            if media.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this media")

            media.description = description
            db_session.add(media)
            await db_session.commit()
            await db_session.refresh(media)
            return media

        except HTTPException:
            raise
        except IntegrityError as e:
            await db_session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Media data violates database constraints")
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred")

    @staticmethod
    async def delete_media(db_session: AsyncSession, media_uuid: UUID, user_id: int) -> None:
        try:
            media = await MediaService.get_media_by_uuid(db_session, media_uuid)
            if media.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this media")

            file_path = media.file_path

            await db_session.delete(media)
            await db_session.commit()

            if os.path.exists(file_path):
                os.remove(file_path)

        except HTTPException:
            raise
        except OSError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file")
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred")
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An unexpected error occurred")

    @staticmethod
    def _determine_media_type(mime_type: str, file_ext: str) -> MediaType:
        try:
            mime_type = mime_type.lower()
            if mime_type.startswith('image/'):
                return MediaType.IMAGE
            elif mime_type.startswith('video/'):
                return MediaType.VIDEO
            elif mime_type in ['application/pdf', 'text/plain'] or file_ext in ['pdf', 'txt', 'doc', 'docx']:
                return MediaType.DOCUMENT
            return MediaType.OTHER
        except Exception as e:
            return MediaType.OTHER