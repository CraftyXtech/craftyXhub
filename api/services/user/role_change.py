from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, UserRoleChange


class RoleChangeService:
    """Service responsible for logging and retrieving user role changes."""

    @staticmethod
    async def log_role_change(
        session: AsyncSession,
        *,
        target_user: User,
        changed_by: User,
        old_role: str,
        new_role: str,
        reason: Optional[str] = None,
    ) -> UserRoleChange:
        """
        Log a role change event. The caller is responsible for committing the transaction.
        """
        try:
            record = UserRoleChange(
                user_id=target_user.id,
                changed_by_id=changed_by.id,
                old_role=old_role,
                new_role=new_role,
                reason=reason,
            )
            session.add(record)
            # Let the caller commit so that the role update and audit entry are atomic
            return record
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to log role change: {str(e)}",
            )

    @staticmethod
    async def get_user_role_history(
        session: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserRoleChange]:
        """
        Retrieve role change history for a specific user, ordered by most recent first.
        """
        try:
            query = (
                select(UserRoleChange)
                .where(UserRoleChange.user_id == user_id)
                .order_by(UserRoleChange.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user role history: {str(e)}",
            )


