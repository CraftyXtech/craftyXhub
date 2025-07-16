from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from datetime import datetime, timezone
from models import Post, Category, Tag, User
from models.base import  post_likes, post_tags
from schemas.post import (
    PostCreate,
    PostUpdate,
    CategoryCreate,
    TagCreate
)
from fastapi import HTTPException, status


class PostService:
    @staticmethod
    async def get_post_by_id(session: AsyncSession, post_id: int) -> Optional[Post]:
        result = await session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.comments)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_post_by_slug(session: AsyncSession, slug: str) -> Optional[Post]:
        result = await session.execute(
            select(Post)
            .where(Post.slug == slug)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.comments)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_post(
            session: AsyncSession,
            post_data: PostCreate,
            author_id: int
    ) -> Post:
        existing_post = await PostService.get_post_by_slug(session, post_data.slug)
        if existing_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post with this slug already exists"
            )

        db_post = Post(
            **post_data.model_dump(exclude={"tag_ids"}),
            author_id=author_id
        )

        if post_data.tag_ids:
            tags = await PostService.get_tags_by_ids(session, post_data.tag_ids)
            db_post.tags.extend(tags)

        session.add(db_post)
        await session.commit()
        await session.refresh(db_post)
        return db_post

    @staticmethod
    async def update_post(
            session: AsyncSession,
            post_id: int,
            post_data: PostUpdate,
            current_user_id: int
    ) -> Post:
        db_post = await PostService.get_post_by_id(session, post_id)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if db_post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post"
            )

        update_data = post_data.model_dump(exclude_unset=True, exclude={"tag_ids"})

        if post_data.tag_ids is not None:
            tags = await PostService.get_tags_by_ids(session, post_data.tag_ids)
            db_post.tags = tags

        if post_data.is_published is not None:
            if post_data.is_published and not db_post.is_published:
                db_post.published_at = datetime.utcnow()
            elif not post_data.is_published and db_post.is_published:
                db_post.published_at = None

        for field, value in update_data.items():
            setattr(db_post, field, value)

        db_post.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(db_post)
        return db_post

    @staticmethod
    async def delete_post(
            session: AsyncSession,
            post_id: int,
            current_user_id: int
    ) -> bool:
        db_post = await PostService.get_post_by_id(session, post_id)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if db_post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post"
            )

        await session.delete(db_post)
        await session.commit()
        return True

    @staticmethod
    async def get_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            published_only: bool = True,
            author_id: Optional[int] = None,
            category_id: Optional[int] = None,
            tag_id: Optional[int] = None
    ) -> List[Post]:
        query = select(Post).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )

        conditions = []
        if published_only:
            conditions.append(Post.is_published == True)
        if author_id:
            conditions.append(Post.author_id == author_id)
        if category_id:
            conditions.append(Post.category_id == category_id)
        if tag_id:
            conditions.append(Post.tags.any(Tag.id == tag_id))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_posts_count(
            session: AsyncSession,
            published_only: bool = True,
            author_id: Optional[int] = None,
            category_id: Optional[int] = None,
            tag_id: Optional[int] = None
    ) -> int:
        query = select(func.count(Post.id))

        conditions = []
        if published_only:
            conditions.append(Post.is_published == True)
        if author_id:
            conditions.append(Post.author_id == author_id)
        if category_id:
            conditions.append(Post.category_id == category_id)
        if tag_id:
            conditions.append(Post.tags.any(Tag.id == tag_id))

        if conditions:
            query = query.where(and_(*conditions))

        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def increment_view_count(session: AsyncSession, post_id: int) -> None:
        db_post = await PostService.get_post_by_id(session, post_id)
        if db_post:
            db_post.view_count += 1
            await session.commit()

    @staticmethod
    async def toggle_post_like(
            session: AsyncSession,
            post_id: int,
            user_id: int
    ) -> bool:
        db_post = await PostService.get_post_by_id(session, post_id)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalar_one()

        if user in db_post.liked_by:
            db_post.liked_by.remove(user)
            liked = False
        else:
            db_post.liked_by.append(user)
            liked = True

        await session.commit()
        return liked

    @staticmethod
    async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
        result = await session.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.posts))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_slug(session: AsyncSession, slug: str) -> Optional[Category]:
        result = await session.execute(
            select(Category)
            .where(Category.slug == slug)
            .options(selectinload(Category.posts))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(session: AsyncSession, category_data: CategoryCreate) -> Category:
        existing_category = await session.execute(
            select(Category)
            .where((Category.name == category_data.name) | (Category.slug == category_data.slug))
        )
        if existing_category.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name or slug already exists"
            )

        db_category = Category(**category_data.model_dump())
        session.add(db_category)
        await session.commit()
        await session.refresh(db_category)
        return db_category

    @staticmethod
    async def get_tag_by_id(session: AsyncSession, tag_id: int) -> Optional[Tag]:
        result = await session.execute(
            select(Tag)
            .where(Tag.id == tag_id)
            .options(selectinload(Tag.posts))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tag_by_slug(session: AsyncSession, slug: str) -> Optional[Tag]:
        result = await session.execute(
            select(Tag)
            .where(Tag.slug == slug)
            .options(selectinload(Tag.posts))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tags_by_ids(session: AsyncSession, tag_ids: List[int]) -> List[Tag]:
        result = await session.execute(
            select(Tag)
            .where(Tag.id.in_(tag_ids))
        )
        return result.scalars().all()

    @staticmethod
    async def create_tag(session: AsyncSession, tag_data: TagCreate) -> Tag:
        # Check if tag with same name or slug exists
        existing_tag = await session.execute(
            select(Tag)
            .where((Tag.name == tag_data.name) | (Tag.slug == tag_data.slug))
        )
        if existing_tag.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name or slug already exists"
            )

        db_tag = Tag(**tag_data.model_dump())
        session.add(db_tag)
        await session.commit()
        await session.refresh(db_tag)
        return db_tag

    @staticmethod
    async def get_post_stats(session: AsyncSession) -> dict:
        total_posts = await session.execute(select(func.count(Post.id)))
        published_posts = await session.execute(
            select(func.count(Post.id))
            .where(Post.is_published == True)
        )
        total_views = await session.execute(select(func.sum(Post.view_count)))
        total_likes = await session.execute(
            select(func.count(post_likes.c.user_id))
        )

        return {
            "total_posts": total_posts.scalar_one(),
            "published_posts": published_posts.scalar_one(),
            "draft_posts": total_posts.scalar_one() - published_posts.scalar_one(),
            "total_views": total_views.scalar_one() or 0,
            "total_likes": total_likes.scalar_one()
        }