from .post import PostService
from models import Comment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.comment import CommentCreate
from fastapi import HTTPException, status
from services.user.notification import NotificationService
from typing import List
import logging

logger = logging.getLogger(__name__)


class CommentService:
    @staticmethod
    async def create_comment(
        session: AsyncSession,
        post_uuid: str,
        comment_data: CommentCreate,
        user_id: int
    ) -> Comment:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            parent_id_val = comment_data.parent_id
            parent_comment = None
            if getattr(comment_data, "parent_uuid", None):
                parent_comment = await CommentService.get_comment_by_uuid(session, comment_data.parent_uuid)
                if parent_comment.post_id != db_post.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Parent comment does not belong to this post"
                    )
                parent_id_val = parent_comment.id

            db_comment = Comment(
                content=comment_data.content,
                post_id=db_post.id,
                author_id=user_id,
                parent_id=parent_id_val,
                is_approved=True
            )
            session.add(db_comment)
            await session.commit()

            result = await session.execute(
                select(Comment)
                .options(
                    selectinload(Comment.author),
                    selectinload(Comment.post), 
                    selectinload(Comment.replies).selectinload(Comment.author),
                )
                .where(Comment.id == db_comment.id)
            )
            db_comment = result.scalar_one()
            
            try:
                if parent_comment:
                    await NotificationService.notify_comment_reply(
                        session=session,
                        parent_comment=parent_comment,
                        replier_id=user_id,
                        reply_id=db_comment.id
                    )
                else:
                    await NotificationService.notify_post_comment(
                        session=session,
                        post=db_post,
                        commenter_id=user_id,
                        comment_id=db_comment.id
                    )
            except Exception as notification_error:
                logger.error(f"Notification failed but comment was created: {notification_error}")
            
            return db_comment

        except HTTPException:
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error creating comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid comment data or reference"
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error creating comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )
    @staticmethod
    async def get_post_comments(
            session: AsyncSession,
            post_uuid: str,
            skip: int = 0,
            limit: int = 10
    ) -> List[Comment]:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            query = select(Comment).where(Comment.post_id == db_post.id).options(
                selectinload(Comment.author),
                selectinload(Comment.parent),
                selectinload(Comment.replies).selectinload(Comment.author)
            ).offset(skip).limit(limit).order_by(Comment.created_at.desc())

            result = await session.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting post comments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve comments"
            )
        except Exception as e:
            logger.error(f"Unexpected error getting post comments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def get_user_comments(
            session: AsyncSession,
            user_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Comment]:
        """Get all comments made by a specific user"""
        try:
            from sqlalchemy import func
            
            query = select(Comment).where(Comment.author_id == user_id).options(
                selectinload(Comment.author),
                selectinload(Comment.post),
                selectinload(Comment.parent)
            ).offset(skip).limit(limit).order_by(Comment.created_at.desc())

            result = await session.execute(query)
            return result.scalars().all()

        except SQLAlchemyError as e:
            logger.error(f"Database error getting user comments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve comments"
            )
        except Exception as e:
            logger.error(f"Unexpected error getting user comments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def get_comment_by_uuid(
            session: AsyncSession,
            comment_uuid: str
    ) -> Comment:
        try:
            query = select(Comment).where(Comment.uuid == comment_uuid).options(
                selectinload(Comment.author),
                selectinload(Comment.replies).selectinload(Comment.author)
            )
            result = await session.execute(query)
            db_comment = result.scalar_one_or_none()

            if not db_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )

            return db_comment

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve comment"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def update_comment(
            session: AsyncSession,
            db_comment: Comment,
            comment_data: CommentCreate
    ) -> Comment:
        try:
            if comment_data.content is not None:
                db_comment.content = comment_data.content

            if comment_data.parent_id is not None:
                db_comment.parent_id = comment_data.parent_id

            session.add(db_comment)
            await session.commit()

            result = await session.execute(
                select(Comment).where(Comment.id == db_comment.id).options(
                    selectinload(Comment.author),
                    selectinload(Comment.replies).selectinload(Comment.author)
                )
            )
            return result.scalar_one()

        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid comment data or reference"
            )
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def approve_comment(
            session: AsyncSession,
            db_comment: Comment
    ) -> Comment:
        try:
            db_comment.is_approved = True
            session.add(db_comment)
            await session.commit()

            result = await session.execute(
                select(Comment).where(Comment.id == db_comment.id).options(
                    selectinload(Comment.author),
                    selectinload(Comment.replies).selectinload(Comment.author)
                )
            )
            return result.scalar_one()

        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve comment"
            )
        except Exception as e:
            logger.error(f"Unexpected error approving comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def delete_comment(
            session: AsyncSession,
            db_comment: Comment
    ) -> bool:
        try:
            await session.delete(db_comment)
            await session.commit()
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def toggle_like(
            session: AsyncSession,
            comment_uuid: str,
            user_id: int
    ) -> dict:
        """Toggle like on a comment"""
        try:
            from models import User
            from models.base import comment_likes
            
            db_comment = await CommentService.get_comment_by_uuid(session, comment_uuid)
            if not db_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            # Check if user already liked the comment
            result = await session.execute(
                select(comment_likes).where(
                    comment_likes.c.user_id == user_id,
                    comment_likes.c.comment_id == db_comment.id
                )
            )
            existing_like = result.first()
            
            if existing_like:
                # Unlike - remove the like
                await session.execute(
                    comment_likes.delete().where(
                        comment_likes.c.user_id == user_id,
                        comment_likes.c.comment_id == db_comment.id
                    )
                )
                db_comment.likes_count = max(0, (db_comment.likes_count or 0) - 1)
                liked = False
            else:
                # Like - add the like
                await session.execute(
                    comment_likes.insert().values(
                        user_id=user_id,
                        comment_id=db_comment.id
                    )
                )
                db_comment.likes_count = (db_comment.likes_count or 0) + 1
                liked = True
            
            session.add(db_comment)
            await session.commit()
            
            return {"liked": liked, "likes_count": db_comment.likes_count}

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error toggling comment like: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle like"
            )
        except Exception as e:
            logger.error(f"Unexpected error toggling comment like: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )

    @staticmethod
    async def report_comment(
            session: AsyncSession,
            comment_uuid: str,
            user_id: int,
            reason: str,
            description: str = None
    ):
        """Report a comment"""
        try:
            from models import CommentReport
            
            db_comment = await CommentService.get_comment_by_uuid(session, comment_uuid)
            if not db_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            # Check if user already reported this comment
            result = await session.execute(
                select(CommentReport).where(
                    CommentReport.comment_id == db_comment.id,
                    CommentReport.user_id == user_id
                )
            )
            existing_report = result.scalar_one_or_none()
            
            if existing_report:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already reported this comment"
                )
            
            # Create new report
            report = CommentReport(
                comment_id=db_comment.id,
                user_id=user_id,
                reason=reason,
                description=description,
                status='pending'
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            
            return report

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error reporting comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to report comment"
            )
        except Exception as e:
            logger.error(f"Unexpected error reporting comment: {str(e)}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )