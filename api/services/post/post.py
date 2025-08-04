from typing import List, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from datetime import datetime, timezone, timedelta
from models import Post, Category, Tag, User, Report, Comment
from models.base import post_likes, post_bookmarks
from schemas.post import (
    PostCreate,
    PostUpdate,
    CategoryCreate,
    CategoryUpdate,
    TagCreate,
    ReportCreate
)
from utils.slug_generator import generate_slug, generate_random_slug
from fastapi import HTTPException, status, UploadFile
from pathlib import Path
import uuid
import aiofiles
import os
import logging
import time

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads/posts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

class PostService:

    @staticmethod
    def _apply_post_relationships(query):
        try:
            return query.options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.comments).selectinload(Comment.replies),
                selectinload(Post.liked_by),
                selectinload(Post.bookmarked_by)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply post relationships: {str(e)}"
            )

    @staticmethod
    def _add_soft_delete_filter(query, include_deleted: bool = False):
        try:
            if not include_deleted:
                query = query.where(Post.deleted_at.is_(None))
            return query
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply soft delete filter: {str(e)}"
            )

    @staticmethod
    async def get_post_by_uuid(session: AsyncSession, post_uuid: str, include_deleted: bool = False) -> Optional[Post]:
        try:
            query = select(Post).where(Post.uuid == post_uuid)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get post by UUID: {str(e)}"
            )

    @staticmethod
    async def generate_unique_slug(
            session: AsyncSession,
            title: str,
            model: Post | Category | Tag,
            max_length: int = 50,
            random_slug_length: int = 50,
            max_attempts: int = 5
    ) -> str:
        try:
            for _ in range(max_attempts):
                candidate_slug = generate_slug(title, max_length=max_length, add_random_suffix=False)
                existing = await session.execute(
                    select(model).where(model.slug == candidate_slug)
                )
                if not existing.scalar_one_or_none():
                    return candidate_slug

            for _ in range(5):
                random_slug = generate_random_slug(length=random_slug_length)
                existing = await session.execute(
                    select(model).where(model.slug == random_slug)
                )
                if not existing.scalar_one_or_none():
                    return random_slug

            timestamp = str(int(time.time()))
            base_slug = generate_slug(title, max_length=max_length - len(timestamp) - 1, add_random_suffix=False)
            return f"{base_slug}_{timestamp}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate unique slug: {str(e)}"
            )

    @staticmethod
    async def get_post_by_slug(session: AsyncSession, slug: str, include_deleted: bool = False) -> Optional[Post]:
        try:
            query = select(Post).where(Post.slug == slug)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get post by slug: {str(e)}"
            )

    @staticmethod
    async def get_post_with_relationships(
            session: AsyncSession,
            post_id: int,
            include_deleted: bool = False
    ) -> Optional[Post]:
        try:
            query = select(Post).where(Post.id == post_id)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get post with relationships: {str(e)}"
            )

    @staticmethod
    async def get_trending_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            like_count_subquery = (
                select(post_likes.c.post_id, func.count(post_likes.c.user_id).label("like_count"))
                .group_by(post_likes.c.post_id)
                .subquery()
            )

            query = select(Post).where(Post.is_published == True)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.where(Post.created_at >= datetime.now(timezone.utc) - timedelta(days=7))
            query = query.outerjoin(like_count_subquery, Post.id == like_count_subquery.c.post_id)
            query = query.order_by((Post.view_count + func.coalesce(like_count_subquery.c.like_count, 0)).desc())
            query = query.offset(skip).limit(limit)

            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get trending posts: {str(e)}"
            )

    @staticmethod
    async def get_featured_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            query = select(Post).where(and_(Post.is_published == True, Post.is_featured == True))
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get featured posts: {str(e)}"
            )

    @staticmethod
    async def get_recent_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            query = select(Post).where(Post.is_published == True)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.offset(skip).limit(limit).order_by(Post.published_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get recent posts: {str(e)}"
            )

    @staticmethod
    async def get_popular_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            query = select(Post).where(Post.is_published == True)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.order_by(Post.view_count.desc())
            query = query.offset(skip).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get popular posts: {str(e)}"
            )

    @staticmethod
    async def get_related_posts(
            session: AsyncSession,
            post_uuid: str,
            limit: int = 5,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            query = select(Post).where(and_(
                Post.is_published == True,
                Post.id != db_post.id,
                or_(Post.category_id == db_post.category_id,
                    Post.tags.any(Tag.id.in_([tag.id for tag in db_post.tags])))
            ))
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.order_by(Post.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get related posts: {str(e)}"
            )

    @staticmethod
    async def publish_post(
            session: AsyncSession,
            post_uuid: str,
            current_user: User
    ) -> Post:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            if not current_user.is_moderator:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to publish this post")

            db_post.is_published = True
            db_post.published_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_post)
            return db_post
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to publish post: {str(e)}"
            )

    @staticmethod
    async def unpublish_post(
            session: AsyncSession,
            post_uuid: str,
            current_user: User
    ) -> Post:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            if not current_user.is_moderator:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Not authorized to unpublish this post")

            db_post.is_published = False
            db_post.published_at = None
            await session.commit()
            await session.refresh(db_post)
            return db_post
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to unpublish post: {str(e)}"
            )

    @staticmethod
    async def feature_post(
            session: AsyncSession,
            post_uuid: str,
            current_user: User,
            feature: bool = True
    ) -> Post:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            if db_post.author_id != current_user.id or not current_user.is_moderator:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to feature this post")

            db_post.is_featured = feature
            await session.commit()
            await session.refresh(db_post)
            return db_post
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to feature post: {str(e)}"
            )

    @staticmethod
    async def get_draft_posts(
            session: AsyncSession,
            user_id: int,
            skip: int = 0,
            limit: int = 10,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            query = select(Post).where(and_(
                Post.author_id == user_id,
                Post.is_published == False
            ))
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)
            query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get draft posts: {str(e)}"
            )

    @staticmethod
    async def toggle_bookmark_post(
            session: AsyncSession,
            post_uuid: str,
            user_id: int
    ) -> bool:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            user = await session.execute(select(User).where(User.id == user_id))
            user = user.scalar_one()

            if user in db_post.bookmarked_by:
                db_post.bookmarked_by.remove(user)
                bookmarked = False
            else:
                db_post.bookmarked_by.append(user)
                bookmarked = True

            await session.commit()
            return bookmarked
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to toggle bookmark: {str(e)}"
            )

    @staticmethod
    async def get_user_bookmarks(
            session: AsyncSession,
            user_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Post]:
        try:
            query = select(Post).join(post_bookmarks).where(post_bookmarks.c.user_id == user_id)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted=False)
            query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user bookmarks: {str(e)}"
            )

    @staticmethod
    async def get_reports(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10
    ) -> List[Report]:
        try:
            query = select(Report).options(selectinload(Report.post), selectinload(Report.user))
            query = query.offset(skip).limit(limit).order_by(Report.created_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get reports: {str(e)}"
            )

    @staticmethod
    async def get_reports_count(
            session: AsyncSession,
            post_id: Optional[int] = None,
            user_id: Optional[int] = None
    ) -> int:
        try:
            query = select(func.count(Report.id))
            if post_id:
                query = query.where(Report.post_id == post_id)
            if user_id:
                query = query.where(Report.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get reports count: {str(e)}"
            )

    @staticmethod
    async def report_post(
            session: AsyncSession,
            post_uuid: str,
            report_data: ReportCreate,
            user_id: int
    ) -> Report:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid)
            if not db_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            db_report = Report(
                post_id=db_post.id,
                user_id=user_id,
                reason=report_data.reason,
                description=report_data.description
            )
            session.add(db_report)
            await session.commit()
            await session.refresh(db_report)
            return db_report
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to report post: {str(e)}"
            )

    @staticmethod
    async def get_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            published_only: bool = True,
            author_id: Optional[int] = None,
            category_id: Optional[int] = None,
            tag_id: Optional[int] = None,
            include_deleted: bool = False
    ) -> List[Post]:
        try:
            query = select(Post)
            query = PostService._apply_post_relationships(query)
            query = PostService._add_soft_delete_filter(query, include_deleted)

            conditions = []
            if published_only:
                conditions.append(Post.is_published == True)
            else:
                conditions.append(Post.is_published == False)

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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get posts: {str(e)}"
            )

    @staticmethod
    async def get_posts_count(
            session: AsyncSession,
            published_only: bool = True,
            is_featured: Optional[bool] = None,
            author_id: Optional[int] = None,
            category_id: Optional[int] = None,
            tag_id: Optional[int] = None,
            include_deleted: bool = False
    ) -> int:
        try:
            query = select(func.count(Post.id))
            query = PostService._add_soft_delete_filter(query, include_deleted)

            conditions = []
            if published_only:
                conditions.append(Post.is_published == True)
            else:
                conditions.append(Post.is_published == False)

            if is_featured:
                conditions.append(Post.is_featured == is_featured)
            elif is_featured is not None:
                conditions.append(Post.is_featured == False)

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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get posts count: {str(e)}"
            )

    @staticmethod
    async def create_post(
            session: AsyncSession,
            post_data: PostCreate,
            author_id: int
    ) -> Post:
        try:
            existing_post = await PostService.get_post_by_slug(session, post_data.slug, include_deleted=True)
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
            return await PostService.get_post_with_relationships(session, db_post.id)
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create post: {str(e)}"
            )

    @staticmethod
    async def update_post(
            session: AsyncSession,
            post_uuid: str,
            post_data: PostUpdate,
            current_user_id: int
    ) -> Post:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=False)
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

            for field, value in update_data.items():
                setattr(db_post, field, value)

            db_post.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(db_post)
            return db_post
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update post: {str(e)}"
            )

    @staticmethod
    async def delete_post(
            session: AsyncSession,
            post_uuid: str,
            current_user_id: int
    ) -> bool:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=False)
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
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete post: {str(e)}"
            )

    @staticmethod
    async def soft_delete_post(
            session: AsyncSession,
            post_uuid: str,
            current_user_id: int
    ) -> dict:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=False)
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

            db_post.soft_delete()
            await session.commit()
            return {"message": "Post deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to soft delete post: {str(e)}"
            )

    @staticmethod
    async def restore_post(
            session: AsyncSession,
            post_uuid: str,
            current_user_id: int
    ) -> Post:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=True)
            if not db_post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )

            if db_post.deleted_at is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post is not deleted"
                )

            if db_post.author_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to restore this post"
                )

            db_post.restore()
            await session.commit()
            return db_post
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to restore post: {str(e)}"
            )

    @staticmethod
    async def increment_view_count(
            session: AsyncSession,
            post_uuid: str
    ) -> None:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=False)
            if db_post:
                db_post.view_count += 1
                await session.commit()
        except Exception:
            await session.rollback()
            raise

    @staticmethod
    async def toggle_post_like(
            session: AsyncSession,
            post_uuid: str,
            user_id: int
    ) -> bool:
        try:
            db_post = await PostService.get_post_by_uuid(session, post_uuid, include_deleted=False)
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
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to toggle post like: {str(e)}"
            )

    @staticmethod
    async def create_category(
            session: AsyncSession,
            category_data: CategoryCreate
    ) -> Category:
        try:
            if not category_data.slug or not category_data.slug.strip():
                generated_slug = await PostService.generate_unique_slug(session, category_data.name, Category)
            else:
                generated_slug = category_data.slug.strip()
                existing_category = await session.execute(
                    select(Category).where(Category.slug == generated_slug)
                )
                if existing_category.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Category with this slug already exists"
                    )

            db_category = Category(
                name=category_data.name,
                slug=generated_slug,
                parent_id=category_data.parent_id,
                description=category_data.description
            )

            session.add(db_category)
            await session.commit()
            await session.refresh(db_category)
            return db_category
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create category: {str(e)}"
            )

    @staticmethod
    async def update_category(
            session: AsyncSession,
            category_id: int,
            category_data: CategoryUpdate
    ) -> Category:
        try:
            result = await session.execute(
                select(Category).where(Category.id == category_id)
            )
            db_category = result.scalar_one_or_none()
            
            if not db_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )

            # Update fields if provided
            if category_data.name is not None:
                db_category.name = category_data.name
                
                # Generate new slug if name changed and no slug provided
                if category_data.slug is None:
                    generated_slug = await PostService.generate_unique_slug(session, category_data.name, Category)
                    db_category.slug = generated_slug
            
            if category_data.slug is not None:
                if category_data.slug.strip():
                    existing_category = await session.execute(
                        select(Category).where(
                            Category.slug == category_data.slug.strip(),
                            Category.id != category_id
                        )
                    )
                    if existing_category.scalar_one_or_none():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category with this slug already exists"
                        )
                    db_category.slug = category_data.slug.strip()
            
            if category_data.description is not None:
                db_category.description = category_data.description

            await session.commit()
            await session.refresh(db_category)
            return db_category
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update category: {str(e)}"
            )

    @staticmethod
    async def delete_category(
            session: AsyncSession,
            category_id: int
    ):
        try:
            result = await session.execute(
                select(Category).where(Category.id == category_id)
            )
            db_category = result.scalar_one_or_none()
            
            if not db_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            
            # Check if category has posts
            posts_result = await session.execute(
                select(Post).where(Post.category_id == category_id)
            )
            if posts_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete category that has posts. Please reassign or delete posts first."
                )
            
            # Check if category has subcategories
            subcategories_result = await session.execute(
                select(Category).where(Category.parent_id == category_id)
            )
            if subcategories_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete category that has subcategories. Please delete subcategories first."
                )

            await session.delete(db_category)
            await session.commit()
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete category: {str(e)}"
            )

    @staticmethod
    async def get_tag_by_id(
            session: AsyncSession,
            tag_id: int
    ) -> Optional[Tag]:
        try:
            result = await session.execute(
                select(Tag)
                .where(Tag.id == tag_id)
                .options(selectinload(Tag.posts))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get tag by ID: {str(e)}"
            )

    @staticmethod
    async def get_tag_by_slug(
            session: AsyncSession,
            slug: str
    ) -> Optional[Tag]:
        try:
            result = await session.execute(
                select(Tag)
                .where(Tag.slug == slug)
                .options(selectinload(Tag.posts))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get tag by slug: {str(e)}"
            )

    @staticmethod
    async def get_tags_by_ids(
            session: AsyncSession,
            tag_ids: List[int]
    ) -> List[Tag]:
        try:
            result = await session.execute(
                select(Tag)
                .where(Tag.id.in_(tag_ids))
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get tags by IDs: {str(e)}"
            )

    @staticmethod
    async def create_tag(
            session: AsyncSession,
            tag_data: TagCreate
    ) -> Tag:
        try:
            if not tag_data.slug or not tag_data.slug.strip():
                generated_slug = await PostService.generate_unique_slug(session, tag_data.name, Tag)
            else:
                generated_slug = tag_data.slug.strip()
                existing_tag = await session.execute(
                    select(Tag)
                    .where((Tag.name == tag_data.name) | (Tag.slug == tag_data.slug))
                )
                if existing_tag.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tag with this name or slug already exists"
                    )

            db_tag = Tag(
                name=tag_data.name,
                slug=generated_slug
            )

            session.add(db_tag)
            await session.commit()
            await session.refresh(db_tag)
            return db_tag
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create tag: {str(e)}"
            )

    @staticmethod
    async def get_post_stats(
            session: AsyncSession,
            include_deleted: bool = False
    ) -> dict:
        try:
            total_posts_query = select(func.count(Post.id))
            published_posts_query = select(func.count(Post.id)).where(Post.is_published == True)
            total_views_query = select(func.sum(Post.view_count))
            total_likes_query = select(func.count(post_likes.c.user_id))

            if not include_deleted:
                total_posts_query = total_posts_query.where(Post.deleted_at.is_(None))
                published_posts_query = published_posts_query.where(Post.deleted_at.is_(None))
                total_views_query = total_views_query.where(Post.deleted_at.is_(None))
                total_likes_query = total_likes_query.select_from(
                    post_likes.join(Post, post_likes.c.post_id == Post.id)
                ).where(Post.deleted_at.is_(None))

            total_posts = await session.execute(total_posts_query)
            published_posts = await session.execute(published_posts_query)
            total_views = await session.execute(total_views_query)
            total_likes = await session.execute(total_likes_query)

            total_count = total_posts.scalar_one()
            published_count = published_posts.scalar_one()

            return {
                "total_posts": total_count,
                "published_posts": published_count,
                "draft_posts": total_count - published_count,
                "total_views": total_views.scalar_one() or 0,
                "total_likes": total_likes.scalar_one()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get post stats: {str(e)}"
            )

    @staticmethod
    async def get_deleted_posts(
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            author_id: Optional[int] = None
    ) -> List[Post]:
        try:
            query = select(Post).where(Post.deleted_at.is_not(None))
            query = PostService._apply_post_relationships(query)
            if author_id:
                query = query.where(Post.author_id == author_id)
            query = query.offset(skip).limit(limit).order_by(Post.deleted_at.desc())
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get deleted posts: {str(e)}"
            )

    @staticmethod
    async def save_uploaded_file(
            file: UploadFile,
            upload_dir: Path
    ) -> str:
        try:
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            file_size = 0
            content = await file.read()
            file_size = len(content)

            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"
                )

            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            return f"uploads/images/{unique_filename}"
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

    @staticmethod
    async def cleanup_old_image(
            old_image_path: Optional[str],
            new_image_path: Optional[str],
            upload_dir: Path
    ) -> bool:
        try:
            if not old_image_path:
                return True

            if old_image_path == new_image_path:
                return True

            return await PostService.delete_image_file(old_image_path, upload_dir)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup old image: {str(e)}"
            )

    @staticmethod
    async def delete_image_file(
            image_path: Optional[str],
            upload_dir: Path
    ) -> bool:
        try:
            if not image_path:
                return False

            if os.path.isabs(image_path):
                file_path = Path(image_path)
            else:
                file_path = upload_dir / os.path.basename(image_path)

            if file_path.exists() and file_path.is_file():
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete image file: {str(e)}"
            )