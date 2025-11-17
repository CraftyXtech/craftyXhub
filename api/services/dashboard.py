from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Comment, Notification, Post, Report, User
from models.base import post_bookmarks, post_likes
from schemas.dashboard import (
    AdminDashboardResponse,
    DashboardActivityItem,
    DashboardDocumentSummary,
    DashboardOverview,
    DashboardPostSummary,
    EngagementMetrics,
    PostOverviewStats,
    UserDashboardResponse,
)
from schemas.notification import NotificationType
from services.post.post import PostService
from services.user.notification import NotificationService


class DashboardService:
    """
    Aggregates data for admin and user dashboards from existing services and models.
    """

    @staticmethod
    async def get_admin_dashboard(session: AsyncSession) -> AdminDashboardResponse:
        """
        Build the admin/moderator dashboard response with system-wide metrics.
        """
        try:
            # --- User statistics (mirrors admin_users.get_user_statistics) ---
            total_users = await session.scalar(select(func.count()).select_from(User)) or 0
            active_users = (
                await session.scalar(
                    select(func.count()).select_from(User).where(User.is_active.is_(True))
                )
                or 0
            )
            inactive_users = total_users - active_users

            role_counts_stmt = await session.execute(
                select(User.role, func.count()).group_by(User.role)
            )
            role_counts = {
                getattr(role, "value", role): count for role, count in role_counts_stmt.all()
            }

            admin_count = role_counts.get("admin", 0)
            moderator_count = role_counts.get("moderator", 0)
            user_count = role_counts.get("user", 0)

            recent_threshold = datetime.utcnow() - timedelta(days=30)
            recent_registrations = (
                await session.scalar(
                    select(func.count())
                    .select_from(User)
                    .where(User.created_at >= recent_threshold)
                )
                or 0
            )

            # Posts that likely need moderation / review (reported posts)
            pending_reviews = (
                await session.scalar(
                    select(func.count()).select_from(Report)
                )
                or 0
            )

            # --- Post statistics (global) ---
            post_stats = await PostService.get_post_stats(session, include_deleted=False)

            total_posts = int(post_stats.get("total_posts", 0))
            published_posts = int(post_stats.get("published_posts", 0))
            draft_posts = int(post_stats.get("draft_posts", total_posts - published_posts))
            total_views = int(post_stats.get("total_views", 0) or 0)
            total_likes = int(post_stats.get("total_likes", 0) or 0)

            # Total comments (all posts)
            total_comments = (
                await session.scalar(select(func.count(Comment.id))) or 0
            )

            # Total bookmarks (all posts)
            total_bookmarks = (
                await session.scalar(
                    select(func.count()).select_from(post_bookmarks)
                )
                or 0
            )

            # Trending & popular posts
            trending_posts = await PostService.get_trending_posts(
                session=session, skip=0, limit=5, include_deleted=False
            )
            trending_count = len(trending_posts)

            popular_posts = await PostService.get_popular_posts(
                session=session, skip=0, limit=5, include_deleted=False
            )

            top_posts = [
                DashboardPostSummary(
                    uuid=post.uuid,
                    title=post.title,
                    view_count=post.view_count or 0,
                    like_count=len(post.liked_by or []),
                    comment_count=len(post.comments or []),
                    bookmark_count=len(post.bookmarked_by or []),
                    is_published=bool(post.is_published),
                    published_at=post.published_at,
                )
                for post in popular_posts
            ]

            # Recent published posts as "recent documents"
            recent_posts = await PostService.get_recent_posts(
                session=session, skip=0, limit=5, include_deleted=False
            )

            recent_documents = [
                DashboardDocumentSummary(
                    uuid=post.uuid,
                    title=post.title,
                    status="published" if post.is_published else "draft",
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    category=post.category.name if post.category else None,
                )
                for post in recent_posts
            ]

            # Recent activity derived from notifications + reports
            recent_activity = await DashboardService._build_recent_activity_for_admin(
                session=session, limit=10
            )

            overview = DashboardOverview(
                total_posts=total_posts,
                published_posts=published_posts,
                draft_posts=draft_posts,
                total_users=total_users,
                active_users=active_users,
                inactive_users=inactive_users,
                admin_count=admin_count,
                moderator_count=moderator_count,
                user_count=user_count,
                recent_registrations=recent_registrations,
                pending_reviews=int(pending_reviews),
            )

            posts_overview = PostOverviewStats(
                total_posts=total_posts,
                published_posts=published_posts,
                draft_posts=draft_posts,
                trending_count=trending_count,
            )

            engagement_metrics = EngagementMetrics(
                total_views=total_views,
                total_likes=total_likes,
                total_comments=int(total_comments),
                total_bookmarks=int(total_bookmarks),
            )

            return AdminDashboardResponse(
                overview=overview,
                posts_overview=posts_overview,
                engagement_metrics=engagement_metrics,
                top_posts=top_posts,
                recent_activity=recent_activity,
                recent_documents=recent_documents,
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to build admin dashboard: {exc}",
            )

    @staticmethod
    async def get_user_dashboard(
        session: AsyncSession,
        current_user: User,
    ) -> UserDashboardResponse:
        """
        Build the dashboard for a normal user (creator), scoped to their own posts.
        """
        try:
            user_id = current_user.id

            # Per-user posts counts
            published_posts = await PostService.get_posts_count(
                session=session,
                published_only=True,
                author_id=user_id,
                include_deleted=False,
            )
            draft_posts = await PostService.get_posts_count(
                session=session,
                published_only=False,
                author_id=user_id,
                include_deleted=False,
            )
            total_posts = published_posts + draft_posts

            # Per-user engagement metrics
            total_views = (
                await session.scalar(
                    select(func.coalesce(func.sum(Post.view_count), 0)).where(
                        and_(Post.author_id == user_id, Post.deleted_at.is_(None))
                    )
                )
                or 0
            )

            total_likes = (
                await session.scalar(
                    select(func.count())
                    .select_from(
                        post_likes.join(Post, post_likes.c.post_id == Post.id)
                    )
                    .where(and_(Post.author_id == user_id, Post.deleted_at.is_(None)))
                )
                or 0
            )

            total_comments = (
                await session.scalar(
                    select(func.count(Comment.id)).join(
                        Post, Comment.post_id == Post.id
                    ).where(and_(Post.author_id == user_id, Post.deleted_at.is_(None)))
                )
                or 0
            )

            total_bookmarks = (
                await session.scalar(
                    select(func.count())
                    .select_from(
                        post_bookmarks.join(
                            Post, post_bookmarks.c.post_id == Post.id
                        )
                    )
                    .where(and_(Post.author_id == user_id, Post.deleted_at.is_(None)))
                )
                or 0
            )

            # User's top posts (by views)
            top_posts = await DashboardService._get_top_posts_for_user(
                session=session, user_id=user_id, limit=5
            )
            trending_count = len(top_posts)

            # Drafts and recent documents
            drafts_posts = await PostService.get_draft_posts(
                session=session,
                user_id=user_id,
                skip=0,
                limit=5,
                include_deleted=False,
            )
            drafts = [
                DashboardDocumentSummary(
                    uuid=post.uuid,
                    title=post.title,
                    status="draft",
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    category=post.category.name if post.category else None,
                )
                for post in drafts_posts
            ]

            recent_published_posts = await PostService.get_posts(
                session=session,
                skip=0,
                limit=5,
                published_only=True,
                author_id=user_id,
                include_deleted=False,
            )
            recent_documents = [
                DashboardDocumentSummary(
                    uuid=post.uuid,
                    title=post.title,
                    status="published" if post.is_published else "draft",
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    category=post.category.name if post.category else None,
                )
                for post in recent_published_posts
            ]

            # Recent activity based on notifications for this user
            notifications = await NotificationService.get_user_notifications(
                session=session,
                user_id=user_id,
                skip=0,
                limit=10,
                unread_only=False,
            )

            recent_activity: List[DashboardActivityItem] = []
            for notification in notifications:
                notif_type = (
                    notification.notification_type.value
                    if isinstance(notification.notification_type, NotificationType)
                    else str(notification.notification_type)
                )
                icon, color = DashboardService._map_notification_to_icon(notif_type)

                recent_activity.append(
                    DashboardActivityItem(
                        id=notification.uuid,
                        type=notif_type,
                        title=notification.title,
                        description=notification.message,
                        created_at=notification.created_at,
                        icon=icon,
                        color=color,
                    )
                )

            overview = DashboardOverview(
                total_posts=int(total_posts),
                published_posts=int(published_posts),
                draft_posts=int(draft_posts),
            )

            posts_overview = PostOverviewStats(
                total_posts=int(total_posts),
                published_posts=int(published_posts),
                draft_posts=int(draft_posts),
                trending_count=int(trending_count),
            )

            engagement_metrics = EngagementMetrics(
                total_views=int(total_views),
                total_likes=int(total_likes),
                total_comments=int(total_comments),
                total_bookmarks=int(total_bookmarks),
            )

            return UserDashboardResponse(
                overview=overview,
                posts_overview=posts_overview,
                engagement_metrics=engagement_metrics,
                top_posts=top_posts,
                recent_activity=recent_activity,
                drafts=drafts,
                recent_documents=recent_documents,
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to build user dashboard: {exc}",
            )

    @staticmethod
    async def _get_top_posts_for_user(
        session: AsyncSession,
        user_id: int,
        limit: int = 5,
    ) -> List[DashboardPostSummary]:
        """
        Return top posts for a given user ordered by view count.
        """
        query = (
            select(Post)
            .where(
                and_(
                    Post.author_id == user_id,
                    Post.is_published.is_(True),
                    Post.deleted_at.is_(None),
                )
            )
            .options(
                selectinload(Post.liked_by),
                selectinload(Post.comments),
                selectinload(Post.bookmarked_by),
            )
            .order_by(Post.view_count.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        posts = result.scalars().all()

        return [
            DashboardPostSummary(
                uuid=post.uuid,
                title=post.title,
                view_count=post.view_count or 0,
                like_count=len(post.liked_by or []),
                comment_count=len(post.comments or []),
                bookmark_count=len(post.bookmarked_by or []),
                is_published=bool(post.is_published),
                published_at=post.published_at,
            )
            for post in posts
        ]

    @staticmethod
    async def _build_recent_activity_for_admin(
        session: AsyncSession,
        limit: int = 10,
    ) -> List[DashboardActivityItem]:
        """
        Build a system-wide recent activity list based on notifications and reports.
        """
        # Recent notifications of key types
        important_types = [
            NotificationType.POST_PUBLISHED,
            NotificationType.POST_REPORTED,
            NotificationType.POST_FLAGGED,
            NotificationType.POST_COMMENT,
            NotificationType.POST_LIKE,
        ]

        notif_query = (
            select(Notification)
            .where(Notification.notification_type.in_(important_types))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        notif_result = await session.execute(notif_query)
        notifications = notif_result.scalars().all()

        activity_items: List[DashboardActivityItem] = []
        for notification in notifications:
            notif_type = (
                notification.notification_type.value
                if isinstance(notification.notification_type, NotificationType)
                else str(notification.notification_type)
            )
            icon, color = DashboardService._map_notification_to_icon(notif_type)
            activity_items.append(
                DashboardActivityItem(
                    id=notification.uuid,
                    type=notif_type,
                    title=notification.title,
                    description=notification.message,
                    created_at=notification.created_at,
                    icon=icon,
                    color=color,
                )
            )

        # Optionally, we could also incorporate recent reports as separate activity items.
        # For now, notifications already cover reported posts (POST_REPORTED).

        return activity_items

    @staticmethod
    def _map_notification_to_icon(notification_type: str) -> tuple[str, str]:
        """
        Map notification types to dashboard icon names and colors.
        """
        mapping = {
            "post_published": ("file-text", "success"),
            "post_like": ("heart", "pink"),
            "post_comment": ("message-circle", "info"),
            "post_bookmark": ("bookmark", "warning"),
            "post_reported": ("alert-circle", "danger"),
            "post_flagged": ("flag", "danger"),
            "post_unflagged": ("flag-off", "success"),
            "new_post_from_following": ("users", "primary"),
            "comment_reply": ("message-square", "info"),
            "new_follower": ("user-plus", "primary"),
        }

        icon, color = mapping.get(notification_type, ("activity", "secondary"))
        return icon, color


