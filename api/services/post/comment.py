from .post import PostService
from models import Comment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.comment import CommentCreate
from fastapi import HTTPException, status
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

            db_comment = Comment(
                content=comment_data.content,
                post_id=db_post.id,
                author_id=user_id,
                parent_id=comment_data.parent_id
            )
            session.add(db_comment)
            await session.commit()

            result = await session.execute(
                select(Comment)
                .options(
                    selectinload(Comment.author),
                    selectinload(Comment.replies).selectinload(Comment.author),
                )
                .where(Comment.id == db_comment.id)
            )
            return result.scalar_one()

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