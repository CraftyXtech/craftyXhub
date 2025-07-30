from fastapi import APIRouter, Depends, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from services.user.auth import get_current_active_user as get_current_user
from models.user import User
from services.user.media import MediaService
from typing import List, Optional
from fastapi import UploadFile
from schemas.user import MediaResponse, MediaUpdateRequest
from database.connection import get_db_session as get_db


router = APIRouter(prefix="/media", tags=["media"])


@router.get("/", response_model=List[MediaResponse])
async def get_user_media(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    media = await MediaService.get_user_media(db, current_user.id)
    return media


@router.post("/upload", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    media = await MediaService.upload_media(db, current_user.id, file, description)
    return media

@router.get("/{media_uuid}", response_model=MediaResponse)
async def get_media(
    media_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    media = await MediaService.get_media_by_uuid(db, media_uuid)
    return media

@router.put("/{media_uuid}", response_model=MediaResponse)
async def update_media(
    media_uuid: str,
    media_update: MediaUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    media = await MediaService.update_media(db, media_uuid, current_user.id, media_update.description)
    return media

@router.delete("/{media_uuid}")
async def delete_media(
    media_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await MediaService.delete_media(db, media_uuid, current_user.id)
    return {"message": "Media deleted successfully"}