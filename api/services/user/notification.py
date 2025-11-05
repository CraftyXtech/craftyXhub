from typing import List, Optional
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from fastapi import HTTPException, status
import logging

from models import Notification, User, Post, Comment
from models.base import user_follows
from models.notification import NotificationType

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def _apply_notification_relationships(query):
        """Apply eager loading for notification relationships"""
        try:
            return query.options(
                selectinload(Notification.recipient),
                selectinload(Notification.sender).selectinload(User.profile),
                selectinload(Notification.post),
                selectinload(Notification.comment)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply notification relationships: {str(e)}"
            )

    @staticmethod
    async def create_notification(
        session: AsyncSession,
        recipient_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        sender_id: Optional[int] = None,
        post_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        action_url: Optional[str] = None
    ) -> Notification:
        try:
            recipient_result = await session.execute(
                select(User).where(User.id == recipient_id)
            )
            recipient = recipient_result.scalar_one_or_none()
            if not recipient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipient user not found"
                )

            if sender_id:
                sender_result = await session.execute(
                    select(User).where(User.id == sender_id)
                )
                sender = sender_result.scalar_one_or_none()
                if not sender:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sender user not found"
                    )

            db_notification = Notification(
                recipient_id=recipient_id,
                sender_id=sender_id,
                notification_type=notification_type,
                title=title,
                message=message,
                post_id=post_id,
                comment_id=comment_id,
                action_url=action_url,
                is_read=False
            )

            session.add(db_notification)
            await session.commit()

            result = await session.execute(
                select(Notification)
                .where(Notification.id == db_notification.id)
                .options(
                    selectinload(Notification.recipient),
                    selectinload(Notification.sender).selectinload(User.profile),
                    selectinload(Notification.post),
                    selectinload(Notification.comment)
                )
            )
            return result.scalar_one()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create notification: {str(e)}"
            )

    @staticmethod
    async def get_user_notifications(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Notification]:
        try:
            query = select(Notification).where(Notification.recipient_id == user_id)
            
            if unread_only:
                query = query.where(Notification.is_read == False)
            
            query = NotificationService._apply_notification_relationships(query)
            query = query.order_by(Notification.created_at.desc())
            query = query.offset(skip).limit(limit)

            result = await session.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user notifications: {str(e)}"
            )

    @staticmethod
    async def get_notification_by_uuid(
        session: AsyncSession,
        notification_uuid: str,
        user_id: int
    ) -> Optional[Notification]:
        try:
            query = select(Notification).where(
                and_(
                    Notification.uuid == notification_uuid,
                    Notification.recipient_id == user_id
                )
            )
            query = NotificationService._apply_notification_relationships(query)

            result = await session.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting notification by UUID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get notification: {str(e)}"
            )

    @staticmethod
    async def get_notification_stats(
        session: AsyncSession,
        user_id: int
    ) -> dict:
        try:
            total_query = select(func.count(Notification.id)).where(
                Notification.recipient_id == user_id
            )
            total_result = await session.execute(total_query)
            total = total_result.scalar_one()

            unread_query = select(func.count(Notification.id)).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.is_read == False
                )
            )
            unread_result = await session.execute(unread_query)
            unread = unread_result.scalar_one()

            return {
                "total": total,
                "unread": unread,
                "read": total - unread
            }

        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get notification stats: {str(e)}"
            )

    @staticmethod
    async def mark_as_read(
        session: AsyncSession,
        notification_uuid: str,
        user_id: int
    ) -> Notification:
        try:
            notification = await NotificationService.get_notification_by_uuid(
                session, notification_uuid, user_id
            )

            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )

            if not notification.is_read:
                notification.mark_as_read()
                await session.commit()
                await session.refresh(notification)

            return notification

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notification as read: {str(e)}"
            )

    @staticmethod
    async def mark_all_as_read(
        session: AsyncSession,
        user_id: int
    ) -> int:
        try:
            # Get all unread notifications
            query = select(Notification).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.is_read == False
                )
            )
            result = await session.execute(query)
            notifications = result.scalars().all()

            # Mark each as read
            count = 0
            for notification in notifications:
                notification.mark_as_read()
                count += 1

            if count > 0:
                await session.commit()

            return count

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark all notifications as read: {str(e)}"
            )

    @staticmethod
    async def delete_notification(
        session: AsyncSession,
        notification_uuid: str,
        user_id: int
    ) -> bool:
        try:
            notification = await NotificationService.get_notification_by_uuid(
                session, notification_uuid, user_id
            )

            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )

            await session.delete(notification)
            await session.commit()
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete notification: {str(e)}"
            )

    @staticmethod
    async def delete_all_notifications(
        session: AsyncSession,
        user_id: int
    ) -> int:
        try:
            count_query = select(func.count(Notification.id)).where(
                Notification.recipient_id == user_id
            )
            count_result = await session.execute(count_query)
            count = count_result.scalar_one()

            delete_query = delete(Notification).where(
                Notification.recipient_id == user_id
            )
            await session.execute(delete_query)
            await session.commit()

            return count

        except Exception as e:
            logger.error(f"Error deleting all notifications: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete all notifications: {str(e)}"
            )

    @staticmethod
    async def mark_email_sent(
        session: AsyncSession,
        notification_id: int
    ) -> None:
        try:
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()

            if notification:
                notification.mark_email_sent()
                await session.commit()

        except Exception as e:
            logger.error(f"Error marking email as sent: {str(e)}")
            await session.rollback()

    @staticmethod
    async def get_unread_count(
        session: AsyncSession,
        user_id: int
    ) -> int:
        try:
            query = select(func.count(Notification.id)).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.is_read == False
                )
            )
            result = await session.execute(query)
            return result.scalar_one()

        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get unread count: {str(e)}"
            )

    @staticmethod
    async def delete_old_notifications(
        session: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> int:
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count before deletion
            count_query = select(func.count(Notification.id)).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.created_at < cutoff_date
                )
            )
            count_result = await session.execute(count_query)
            count = count_result.scalar_one()

            # Delete old notifications
            delete_query = delete(Notification).where(
                and_(
                    Notification.recipient_id == user_id,
                    Notification.created_at < cutoff_date
                )
            )
            await session.execute(delete_query)
            await session.commit()

            return count

        except Exception as e:
            logger.error(f"Error deleting old notifications: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete old notifications: {str(e)}"
            )
            
    
    @staticmethod
    async def notify_comment_reply(
        session: AsyncSession,
        parent_comment: Comment,
        replier_id: int,
        reply_id: int
    ) -> None:
        """Notify the parent comment author about a reply"""
        try:
            if parent_comment.author_id == replier_id:
                return

            replier_result = await session.execute(
                select(User).where(User.id == replier_id)
            )
            replier = replier_result.scalar_one_or_none()
            if not replier:
                return

            # Get post for UUID
            post_result = await session.execute(
                select(Post).where(Post.id == parent_comment.post_id)
            )
            post = post_result.scalar_one_or_none()
            if not post:
                return

            await NotificationService.create_notification(
                session=session,
                recipient_id=parent_comment.author_id,
                sender_id=replier_id,
                notification_type=NotificationType.COMMENT_REPLY,
                title="New Reply to Your Comment",
                message=f"{replier.username} replied to your comment",
                post_id=parent_comment.post_id,
                comment_id=reply_id,
                action_url=f"/posts/{post.uuid}#comment-{reply_id}"
            )
        except Exception as e:
            logger.error(f"Error creating comment reply notification: {str(e)}")

    @staticmethod
    async def notify_post_comment(
        session: AsyncSession,
        post: Post,
        commenter_id: int,
        comment_id: int
    ) -> None:
        """Notify the post author about a new comment"""
        try:
            if post.author_id == commenter_id:
                return

            commenter_result = await session.execute(
                select(User).where(User.id == commenter_id)
            )
            commenter = commenter_result.scalar_one_or_none()
            if not commenter:
                return
            
            # Create notification (this commits internally)
            await NotificationService.create_notification(
                session=session,
                recipient_id=post.author_id,
                sender_id=commenter_id,
                notification_type=NotificationType.POST_COMMENT,
                title="New Comment on Your Post",
                message=f"{commenter.username} commented on your post: {post.title}",
                post_id=post.id,
                comment_id=comment_id,
                action_url=f"/posts/{post.uuid}#comment-{comment_id}"
            )
        except Exception as e:
            logger.error(f"Error creating post comment notification: {str(e)}")

    @staticmethod
    async def notify_post_like(
        session: AsyncSession,
        post: Post,
        liker_id: int
    ) -> None:
        """Notify the post author about a like"""
        try:
            if post.author_id == liker_id:
                return

            liker_result = await session.execute(
                select(User).where(User.id == liker_id)
            )
            liker = liker_result.scalar_one_or_none()
            if not liker:
                return

            # Create notification for the post author
            await NotificationService.create_notification(
                session=session,
                recipient_id=post.author_id,
                sender_id=liker_id,
                notification_type=NotificationType.POST_LIKE,
                title="New Like on Your Post",
                message=f"{liker.username} liked your post: {post.title}",
                post_id=post.id,
                action_url=f"/posts/{post.uuid}"
            )
        except Exception as e:
            logger.error(f"Error creating post like notification: {str(e)}")

    @staticmethod
    async def notify_followers_new_post(
        session: AsyncSession,
        post: Post,
        author_id: int
    ) -> None:
        try:
            author_result = await session.execute(
                select(User).where(User.id == author_id)
            )
            author = author_result.scalar_one_or_none()
            if not author:
                return

            
            followers_query = select(user_follows.c.follower_id).where(
                user_follows.c.followed_id == author_id
            )

            followers_result = await session.execute(followers_query)
            follower_ids = [row[0] for row in followers_result.all()]

            for follower_id in follower_ids:
                await NotificationService.create_notification(
                    session=session,
                    recipient_id=follower_id,
                    sender_id=author_id,
                    notification_type=NotificationType.POST_PUBLISHED, 
                    title="New Post from Someone You Follow",
                    message=f"{author.username} published a new post: {post.title}",
                    post_id=post.id,
                    action_url=f"/posts/{post.uuid}"
                )

            await session.commit()

        except Exception as e:
            logger.error(f"Error creating follower notifications: {str(e)}")
            await session.rollback()


    @staticmethod
    async def notify_post_reported(
        session: AsyncSession,
        post: Post,
        reporter_id: int
    ) -> None:
        """Notify admins/moderators about a reported post"""
        try:
            reporter_result = await session.execute(
                select(User).where(User.id == reporter_id)
            )
            reporter = reporter_result.scalar_one_or_none()
            if not reporter:
                return

            admins_query = select(User.id).where(
                or_(User.is_admin == True, User.is_moderator == True)
            )
            admins_result = await session.execute(admins_query)
            admin_ids = [row[0] for row in admins_result.all()]

            for admin_id in admin_ids:
                await NotificationService.create_notification(
                    session=session,
                    recipient_id=admin_id,
                    sender_id=reporter_id,
                    notification_type=NotificationType.POST_REPORTED,
                    title="Post Reported",
                    message=f"Post '{post.title}' was reported by {reporter.username}",
                    post_id=post.id,
                    action_url=f"/admin/posts/{post.uuid}"
                )
        except Exception as e:
            logger.error(f"Error creating post reported notification: {str(e)}")

    @staticmethod
    async def notify_post_flagged(
        session: AsyncSession,
        post: Post,
        admin_id: int
    ) -> None:
        """Notify post author that their post was flagged"""
        try:
            admin_result = await session.execute(
                select(User).where(User.id == admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            if not admin:
                return

            await NotificationService.create_notification(
                session=session,
                recipient_id=post.author_id,
                sender_id=admin_id,
                notification_type=NotificationType.POST_FLAGGED,
                title="Post Flagged",
                message=f"Your post '{post.title}' has been flagged by moderators",
                post_id=post.id,
                action_url=f"/posts/{post.uuid}"
            )
        except Exception as e:
            logger.error(f"Error creating post flagged notification: {str(e)}")
