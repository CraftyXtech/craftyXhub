import logging
import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Comment, CommentReport, Notification, Post, Report, User
from models.ai_draft import AIDraft, AIGenerationLog
from models.base import comment_likes, post_bookmarks, post_likes, post_tags, user_follows
from models.collection import Highlight, ReadingHistory, ReadingList, ReadingListItem
from models.user import (
    EmailVerificationToken,
    Media,
    PasswordResetToken,
    Profile,
    UserRole,
    UserRoleChange,
)


logger = logging.getLogger(__name__)
API_ROOT = Path(__file__).resolve().parents[2]


class AdminUserManagementService:
    @staticmethod
    async def ensure_can_manage_target(
        session: AsyncSession,
        *,
        actor: User,
        target: User,
        action: str,
        allow_self: bool = False,
    ) -> None:
        if actor.id == target.id and not allow_self:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You cannot {action} your own account via this endpoint",
            )

        if actor.role == UserRole.SUPER_ADMIN:
            if target.role == UserRole.SUPER_ADMIN:
                await AdminUserManagementService._ensure_not_last_super_admin(
                    session,
                    target=target,
                    action=action,
                )
            return

        if actor.role == UserRole.ADMIN:
            if target.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Only super-admins can {action} admin accounts",
                )
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    @staticmethod
    async def ensure_role_change_allowed(
        session: AsyncSession,
        *,
        actor: User,
        target: User,
        new_role: UserRole,
    ) -> None:
        if actor.id == target.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot modify your own role",
            )

        await AdminUserManagementService.ensure_can_manage_target(
            session,
            actor=actor,
            target=target,
            action="change roles for",
        )

        if actor.role == UserRole.ADMIN and new_role in {
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super-admins can promote users to admin or super-admin",
            )

        if target.role == UserRole.SUPER_ADMIN and new_role != UserRole.SUPER_ADMIN:
            await AdminUserManagementService._ensure_not_last_super_admin(
                session,
                target=target,
                action="change roles for",
            )

    @staticmethod
    async def permanently_delete_user(
        session: AsyncSession,
        *,
        user: User,
    ) -> dict[str, Any]:
        try:
            user_id = user.id
            deleted_user = {
                "id": user.id,
                "uuid": user.uuid,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": getattr(user.role, "value", str(user.role)),
            }

            avatar_paths = list(
                (
                    await session.execute(
                        select(Profile.avatar).where(
                            Profile.user_id == user_id,
                            Profile.avatar.is_not(None),
                        )
                    )
                ).scalars()
            )
            media_paths = list(
                (
                    await session.execute(
                        select(Media.file_path).where(Media.user_id == user_id)
                    )
                ).scalars()
            )
            featured_image_paths = list(
                (
                    await session.execute(
                        select(Post.featured_image).where(
                            Post.author_id == user_id,
                            Post.featured_image.is_not(None),
                        )
                    )
                ).scalars()
            )

            post_ids_subquery = select(Post.id).where(Post.author_id == user_id)
            authored_comment_ids_subquery = select(Comment.id).where(
                Comment.author_id == user_id
            )
            comment_ids_subquery = select(Comment.id).where(
                or_(
                    Comment.author_id == user_id,
                    Comment.post_id.in_(post_ids_subquery),
                )
            )
            reading_list_ids_subquery = select(ReadingList.id).where(
                ReadingList.user_id == user_id
            )

            deleted_counts = {
                "notifications_sender_nullified": await AdminUserManagementService._execute_update(
                    session,
                    update(Notification)
                    .where(Notification.sender_id == user_id)
                    .values(sender_id=None),
                ),
                "comment_children_reparented": await AdminUserManagementService._execute_update(
                    session,
                    update(Comment)
                    .where(Comment.parent_id.in_(authored_comment_ids_subquery))
                    .values(parent_id=None),
                ),
                "comment_reports": await AdminUserManagementService._execute_delete(
                    session,
                    delete(CommentReport).where(
                        or_(
                            CommentReport.user_id == user_id,
                            CommentReport.comment_id.in_(comment_ids_subquery),
                        )
                    ),
                ),
                "comment_likes": await AdminUserManagementService._execute_delete(
                    session,
                    delete(comment_likes).where(
                        or_(
                            comment_likes.c.user_id == user_id,
                            comment_likes.c.comment_id.in_(comment_ids_subquery),
                        )
                    ),
                ),
                "notifications": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Notification).where(
                        or_(
                            Notification.recipient_id == user_id,
                            Notification.post_id.in_(post_ids_subquery),
                            Notification.comment_id.in_(comment_ids_subquery),
                        )
                    ),
                ),
                "reports": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Report).where(
                        or_(
                            Report.user_id == user_id,
                            Report.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "post_likes": await AdminUserManagementService._execute_delete(
                    session,
                    delete(post_likes).where(
                        or_(
                            post_likes.c.user_id == user_id,
                            post_likes.c.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "post_bookmarks": await AdminUserManagementService._execute_delete(
                    session,
                    delete(post_bookmarks).where(
                        or_(
                            post_bookmarks.c.user_id == user_id,
                            post_bookmarks.c.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "post_tags": await AdminUserManagementService._execute_delete(
                    session,
                    delete(post_tags).where(post_tags.c.post_id.in_(post_ids_subquery)),
                ),
                "reading_list_items": await AdminUserManagementService._execute_delete(
                    session,
                    delete(ReadingListItem).where(
                        or_(
                            ReadingListItem.list_id.in_(reading_list_ids_subquery),
                            ReadingListItem.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "reading_history": await AdminUserManagementService._execute_delete(
                    session,
                    delete(ReadingHistory).where(
                        or_(
                            ReadingHistory.user_id == user_id,
                            ReadingHistory.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "highlights": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Highlight).where(
                        or_(
                            Highlight.user_id == user_id,
                            Highlight.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "password_reset_tokens": await AdminUserManagementService._execute_delete(
                    session,
                    delete(PasswordResetToken).where(
                        PasswordResetToken.user_id == user_id
                    ),
                ),
                "email_verification_tokens": await AdminUserManagementService._execute_delete(
                    session,
                    delete(EmailVerificationToken).where(
                        EmailVerificationToken.user_id == user_id
                    ),
                ),
                "ai_generation_logs": await AdminUserManagementService._execute_delete(
                    session,
                    delete(AIGenerationLog).where(AIGenerationLog.user_id == user_id),
                ),
                "ai_drafts": await AdminUserManagementService._execute_delete(
                    session,
                    delete(AIDraft).where(AIDraft.user_id == user_id),
                ),
                "media": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Media).where(Media.user_id == user_id),
                ),
                "user_follows": await AdminUserManagementService._execute_delete(
                    session,
                    delete(user_follows).where(
                        or_(
                            user_follows.c.follower_id == user_id,
                            user_follows.c.followed_id == user_id,
                        )
                    ),
                ),
                "user_role_changes": await AdminUserManagementService._execute_delete(
                    session,
                    delete(UserRoleChange).where(
                        or_(
                            UserRoleChange.user_id == user_id,
                            UserRoleChange.changed_by_id == user_id,
                        )
                    ),
                ),
                "comments": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Comment).where(
                        or_(
                            Comment.author_id == user_id,
                            Comment.post_id.in_(post_ids_subquery),
                        )
                    ),
                ),
                "posts": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Post).where(Post.author_id == user_id),
                ),
                "reading_lists": await AdminUserManagementService._execute_delete(
                    session,
                    delete(ReadingList).where(ReadingList.user_id == user_id),
                ),
                "profiles": await AdminUserManagementService._execute_delete(
                    session,
                    delete(Profile).where(Profile.user_id == user_id),
                ),
                "users": await AdminUserManagementService._execute_delete(
                    session,
                    delete(User).where(User.id == user_id),
                ),
            }

            await session.commit()
        except HTTPException:
            await session.rollback()
            raise
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to permanently delete user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to permanently delete user: {exc}",
            ) from exc

        failed_file_cleanup = AdminUserManagementService._cleanup_files(
            avatar_paths + media_paths + featured_image_paths
        )

        return {
            "deleted_user": deleted_user,
            "deleted_counts": deleted_counts,
            "failed_file_cleanup": failed_file_cleanup,
        }

    @staticmethod
    async def _ensure_not_last_super_admin(
        session: AsyncSession,
        *,
        target: User,
        action: str,
    ) -> None:
        total_super_admins = await session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == UserRole.SUPER_ADMIN)
        )
        if total_super_admins is not None and total_super_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot {action} the last super-admin account",
            )

    @staticmethod
    async def _execute_delete(session: AsyncSession, statement) -> int:
        result = await session.execute(statement)
        return max(result.rowcount or 0, 0)

    @staticmethod
    async def _execute_update(session: AsyncSession, statement) -> int:
        result = await session.execute(statement)
        return max(result.rowcount or 0, 0)

    @staticmethod
    def _cleanup_files(paths: list[str]) -> list[str]:
        failed: list[str] = []
        for raw_path in {path for path in paths if path}:
            candidate = Path(raw_path)
            resolved = candidate if candidate.is_absolute() else API_ROOT / candidate
            try:
                if resolved.exists():
                    os.remove(resolved)
            except OSError:
                failed.append(str(raw_path))
        return failed
