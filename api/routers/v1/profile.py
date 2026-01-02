from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from schemas.user import ProfileCreate, ProfileUpdate, ProfileResponse
from services.post.profile import ProfileService
from database.connection import get_db_session as get_db
from services.user.auth import get_current_active_user
from models import User

router = APIRouter(prefix="/profiles", tags=["profiles"])

def clean_form_data(**kwargs):
    cleaned = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and not value.strip():
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned

@router.post("/", response_model=ProfileResponse)
async def create_profile(
        bio: Optional[str] = Form(None),
        location: Optional[str] = Form(None),
        twitter_handle: Optional[str] = Form(None),
        linkedin_handle: Optional[str] = Form(None),
        instagram_handle: Optional[str] = Form(None),
        facebook_handle: Optional[str] = Form(None),
        birth_date: Optional[str] = Form(None),
        avatar: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    processed_birth_date = birth_date if birth_date and birth_date.strip() else None

    profile_data = ProfileCreate(
        bio=bio,
        location=location,
        twitter_handle=twitter_handle,
        linkedin_handle=linkedin_handle,
        instagram_handle=instagram_handle,
        facebook_handle=facebook_handle,
        birth_date=processed_birth_date
    )
    return await ProfileService.create_profile(
        db=db,
        profile_data=profile_data,
        user_id=current_user.id,
        avatar=avatar
    )


@router.get("/{user_uuid}", response_model=ProfileResponse)
async def get_profile(user_uuid: str, db: Session = Depends(get_db)):
    profile = await ProfileService.get_profile(db, user_uuid)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{user_uuid}", response_model=ProfileResponse)
async def update_profile(
        user_uuid: str,
        bio: Optional[str] = Form(None),
        location: Optional[str] = Form(None),
        twitter_handle: Optional[str] = Form(None),
        linkedin_handle: Optional[str] = Form(None),
        instagram_handle: Optional[str] = Form(None),
        facebook_handle: Optional[str] = Form(None),
        birth_date: Optional[str] = Form(None),
        avatar: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    cleaned_data = clean_form_data(
        bio=bio,
        location=location,
        twitter_handle=twitter_handle,
        linkedin_handle=linkedin_handle,
        instagram_handle=instagram_handle,
        facebook_handle=facebook_handle,
        birth_date=birth_date
    )

    profile_data = ProfileUpdate(**cleaned_data)
    profile = await ProfileService.update_profile(
        db=db,
        user_uuid=user_uuid,
        profile_data=profile_data,
        avatar=avatar,
        current_user=current_user
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/{user_uuid}")
async def delete_profile(
        user_uuid: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    success = ProfileService.delete_profile(db, user_uuid, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}