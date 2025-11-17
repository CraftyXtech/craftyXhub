import math
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import get_db_session
from models import User
from models.user import UserRole as DBUserRole, UserRoleChange
from schemas.user import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserStatsResponse,
    AdminUserUpdate,
    UserRole as SchemaUserRole,
    UserRoleUpdate,
    UserStatusUpdate,
    UserRoleChangeListResponse,
)
from services.user.auth import (
    AuthService,
    get_current_admin_or_moderator,
    get_current_admin_only,
)
from services.user.role_change import RoleChangeService


router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get(
    "",
    response_model=AdminUserListResponse,
    summary="List users with filters and pagination",
)
async def list_admin_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, username, or email"),
    role: Optional[SchemaUserRole] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query(None, description="Filter by status: active/inactive"),
    sort: Optional[str] = Query(
        None,
        description="Sort field, prefix with '-' for descending (created_at, last_login, full_name)",
    ),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminUserListResponse:
    filters = _build_user_filters(search, role, status)

    total_stmt = select(func.count()).select_from(User)
    if filters:
        total_stmt = total_stmt.where(and_(*filters))

    total = await session.scalar(total_stmt) or 0

    query = (
        select(User)
        .options(selectinload(User.profile))
        .offset((page - 1) * size)
        .limit(size)
    )

    if filters:
        query = query.where(and_(*filters))

    order_clause = _resolve_sort_clause(sort)
    query = query.order_by(order_clause)

    result = await session.execute(query)
    users: List[User] = result.scalars().all()

    pages = math.ceil(total / size) if total else 0
    has_next = page < pages
    has_prev = page > 1

    return AdminUserListResponse(
        users=users,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get(
    "/stats",
    response_model=AdminUserStatsResponse,
    summary="Retrieve aggregate user statistics",
)
async def get_user_statistics(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminUserStatsResponse:
    total_users = await session.scalar(select(func.count()).select_from(User)) or 0
    active_users = await session.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    ) or 0
    inactive_users = total_users - active_users

    role_counts_stmt = await session.execute(
        select(User.role, func.count()).group_by(User.role)
    )
    role_counts = {
        getattr(role, "value", role): count for role, count in role_counts_stmt.all()
    }

    admin_count = role_counts.get(SchemaUserRole.ADMIN.value, 0)
    moderator_count = role_counts.get(SchemaUserRole.MODERATOR.value, 0)
    user_count = role_counts.get(SchemaUserRole.USER.value, 0)

    recent_threshold = datetime.utcnow() - timedelta(days=30)
    recent_registrations = await session.scalar(
        select(func.count())
        .select_from(User)
        .where(User.created_at >= recent_threshold)
    ) or 0

    return AdminUserStatsResponse(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        admin_count=admin_count,
        moderator_count=moderator_count,
        user_count=user_count,
        recent_registrations=recent_registrations,
    )


@router.get(
    "/{user_uuid}",
    response_model=AdminUserResponse,
    summary="Get detailed information for a specific user",
)
async def get_admin_user(
    user_uuid: str,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminUserResponse:
    user = await _get_user_or_404(session, user_uuid)
    return user


@router.put(
    "/{user_uuid}",
    response_model=AdminUserResponse,
    summary="Update core user attributes",
)
async def update_admin_user(
    user_uuid: str,
    payload: AdminUserUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminUserResponse:
    user = await _get_user_or_404(session, user_uuid)

    if payload.email and payload.email != user.email:
        existing_email = await AuthService.get_user_by_email(session, payload.email)
        if existing_email and existing_email.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = payload.email

    if payload.username and payload.username != user.username:
        existing_username = await AuthService.get_user_by_username(session, payload.username)
        if existing_username and existing_username.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )
        user.username = payload.username

    if payload.full_name:
        user.full_name = payload.full_name

    if payload.is_verified is not None:
        user.is_verified = payload.is_verified

    await session.commit()
    return await _get_user_or_404(session, user_uuid)


@router.patch(
    "/{user_uuid}/role",
    response_model=AdminUserResponse,
    summary="Change a user's role",
)
async def change_user_role(
    user_uuid: str,
    payload: UserRoleUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_admin: User = Depends(get_current_admin_only),
) -> AdminUserResponse:
    user = await _get_user_or_404(session, user_uuid)

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot modify your own role",
        )

    # Only super-admins are allowed to change roles at all
    if current_admin.role != DBUserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super-admins can change user roles",
        )

    target_old_role = user.role
    target_new_role = DBUserRole(payload.role.value)

    # Prevent demoting the last super-admin
    if target_old_role == DBUserRole.SUPER_ADMIN and target_new_role != DBUserRole.SUPER_ADMIN:
        # Count how many super-admins exist
        total_super_admins = await session.scalar(
            select(func.count()).select_from(User).where(User.role == DBUserRole.SUPER_ADMIN)
        )
        if total_super_admins is not None and total_super_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last super-admin",
            )

    old_role_value = getattr(target_old_role, "value", str(target_old_role))
    new_role_value = getattr(target_new_role, "value", str(target_new_role))

    user.role = target_new_role

    # Log audit entry (same transaction as the role change)
    await RoleChangeService.log_role_change(
        session=session,
        target_user=user,
        changed_by=current_admin,
        old_role=old_role_value,
        new_role=new_role_value,
        reason=payload.reason,
    )

    await session.commit()
    return await _get_user_or_404(session, user_uuid)


@router.patch(
    "/{user_uuid}/status",
    response_model=AdminUserResponse,
    summary="Activate or deactivate a user",
)
async def toggle_user_status(
    user_uuid: str,
    payload: UserStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> AdminUserResponse:
    user = await _get_user_or_404(session, user_uuid)
    user.is_active = payload.is_active

    await session.commit()
    return await _get_user_or_404(session, user_uuid)


@router.delete(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate a user account",
)
async def deactivate_user(
    user_uuid: str,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_or_moderator),
) -> dict:
    user = await _get_user_or_404(session, user_uuid)

    if not user.is_active:
        return {"message": "User is already inactive"}

    user.is_active = False
    await session.commit()

    return {"message": "User deactivated successfully"}


@router.get(
    "/{user_uuid}/role-history",
    response_model=UserRoleChangeListResponse,
    summary="Get role change history for a specific user",
)
async def get_user_role_history(
    user_uuid: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_admin_only),
) -> UserRoleChangeListResponse:
    user = await _get_user_or_404(session, user_uuid)

    total_stmt = (
        select(func.count())
        .select_from(UserRoleChange)
        .where(UserRoleChange.user_id == user.id)
    )
    total = await session.scalar(total_stmt) or 0

    changes = await RoleChangeService.get_user_role_history(
        session=session,
        user_id=user.id,
        skip=(page - 1) * size,
        limit=size,
    )

    pages = math.ceil(total / size) if total else 0
    has_next = page < pages
    has_prev = page > 1

    return UserRoleChangeListResponse(
        changes=changes,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
    )


async def _get_user_or_404(session: AsyncSession, user_uuid: str) -> User:
    result = await session.execute(
        select(User)
            .options(selectinload(User.profile))
            .where(User.uuid == user_uuid)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _build_user_filters(
    search: Optional[str],
    role: Optional[SchemaUserRole],
    status: Optional[str],
) -> List:
    filters = []
    if search:
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                User.full_name.ilike(term),
                User.username.ilike(term),
                User.email.ilike(term),
            )
        )

    if role:
        filters.append(User.role == DBUserRole(role.value))

    if status:
        normalized = status.lower()
        if normalized not in {"active", "inactive"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status filter must be 'active' or 'inactive'",
            )
        filters.append(User.is_active.is_(normalized == "active"))

    return filters


def _resolve_sort_clause(sort: Optional[str]):
    mapping = {
        "created_at": User.created_at.asc(),
        "-created_at": User.created_at.desc(),
        "last_login": User.last_login.asc(),
        "-last_login": User.last_login.desc(),
        "full_name": User.full_name.asc(),
        "-full_name": User.full_name.desc(),
    }
    return mapping.get(sort or "-created_at", User.created_at.desc())

