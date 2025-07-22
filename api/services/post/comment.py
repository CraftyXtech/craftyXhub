from .post import PostService
from models import Comment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from schemas.comment import CommentCreate
from fastapi import HTTPException, status
from typing import List

class CommentService:
    @staticmethod
    async def create_comment(
        session: AsyncSession,
        post_uuid: str,
        comment_data: CommentCreate,
        user_id: int
    ) -> Comment:
        db_post = await PostService.get_post_by_uuid(session, post_uuid)
        if not db_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

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


    @staticmethod
    async def get_post_comments(
        session: AsyncSession,
        post_uuid: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Comment]:
        db_post = await PostService.get_post_by_uuid(session, post_uuid)
        if not db_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        query = select(Comment).where(Comment.post_id == db_post.id).options(
            selectinload(Comment.author),
            selectinload(Comment.parent),
            selectinload(Comment.replies).selectinload(Comment.author) 
        ).offset(skip).limit(limit).order_by(Comment.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()
