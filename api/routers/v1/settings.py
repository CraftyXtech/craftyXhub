from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from models import User
from schemas.settings import PublicSiteSettingsResponse, SiteSettingsResponse, SiteSettingsUpdate
from services.site_settings import SiteSettingsService
from services.user.auth import get_current_admin_only


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SiteSettingsResponse)
async def get_site_settings(
    _: User = Depends(get_current_admin_only),
    session: AsyncSession = Depends(get_db_session),
):
    return await SiteSettingsService.get_admin_settings(session)


@router.put("", response_model=SiteSettingsResponse)
async def update_site_settings(
    payload: SiteSettingsUpdate,
    _: User = Depends(get_current_admin_only),
    session: AsyncSession = Depends(get_db_session),
):
    return await SiteSettingsService.update_settings(session, payload)


@router.get("/public", response_model=PublicSiteSettingsResponse)
async def get_public_site_settings(
    session: AsyncSession = Depends(get_db_session),
):
    return await SiteSettingsService.get_public_settings(session)
