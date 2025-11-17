from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from models import User
from schemas.dashboard import AdminDashboardResponse, UserDashboardResponse
from services.dashboard import DashboardService
from services.user.auth import (
    get_current_active_user,
    get_current_admin_or_moderator,
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
    summary="Get system-wide dashboard analytics for admins and moderators",
)
async def get_admin_dashboard(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminDashboardResponse:
    """
    Returns aggregated analytics for admins and moderators, including:
    - Global post statistics
    - User statistics
    - Engagement metrics
    - Top performing posts
    - Recent activity and documents
    """
    return await DashboardService.get_admin_dashboard(session)


@router.get(
    "/user",
    response_model=UserDashboardResponse,
    summary="Get creator-focused dashboard analytics for the current user",
)
async def get_user_dashboard(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserDashboardResponse:
    """
    Returns analytics scoped to the current user as an author/creator, including:
    - Their post statistics
    - Engagement metrics on their content
    - Top performing posts
    - Recent activity on their posts
    - Drafts and recent documents
    """
    return await DashboardService.get_user_dashboard(session, current_user)


