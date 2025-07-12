
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.dialects.postgresql import insert

from models.interactions import Bookmark
from models.post import Post
from models.user import User
from schemas.interaction import BookmarkToggleResponse


class BookmarkService:
    """Service for managing post bookmarks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle_bookmark(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> BookmarkToggleResponse:
        """
        Toggle bookmark status for a post by a user.
        
        Args:
            post_id: UUID of the post to bookmark/unbookmark
            user_id: UUID of the user performing the action
            
        Returns:
            BookmarkToggleResponse with current bookmark status
        """
        # Verify post exists and is published
        post_query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.is_not(None)
            )
        )
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise ValueError("Post not found or not published")

        # Check if user has already bookmarked the post
        existing_bookmark_query = select(Bookmark).where(
            and_(
                Bookmark.post_id == post_id,
                Bookmark.user_id == user_id
            )
        )
        existing_bookmark_result = await self.db.execute(existing_bookmark_query)
        existing_bookmark = existing_bookmark_result.scalar_one_or_none()

        if existing_bookmark:
            # Unbookmark: Remove the bookmark
            await self.db.delete(existing_bookmark)
            await self.db.commit()
            bookmarked = False
            message = "Post unbookmarked successfully"
        else:
            # Bookmark: Add new bookmark
            new_bookmark = Bookmark(
                id=uuid4(),
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            self.db.add(new_bookmark)
            await self.db.commit()
            bookmarked = True
            message = "Post bookmarked successfully"

        # Get updated bookmark count
        bookmark_count = await self.get_bookmark_count(post_id)

        return BookmarkToggleResponse(
            bookmarked=bookmarked,
            bookmark_count=bookmark_count,
            message=message,
            post_id=post_id
        )

    async def get_bookmark_count(self, post_id: UUID) -> int:
        """
        Get total bookmark count for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Total number of bookmarks
        """
        query = select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def is_bookmarked_by_user(self, post_id: UUID, user_id: UUID) -> bool:
        """
        Check if a post is bookmarked by a specific user.
        
        Args:
            post_id: UUID of the post
            user_id: UUID of the user
            
        Returns:
            True if post is bookmarked by user, False otherwise
        """
        query = select(Bookmark).where(
            and_(
                Bookmark.post_id == post_id,
                Bookmark.user_id == user_id
            )
        ).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_user_bookmarks(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Bookmark]:
        """
        Get bookmarks for a specific user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of bookmarks to return
            offset: Number of bookmarks to skip
            
        Returns:
            List of user's bookmarks
        """
        query = select(Bookmark).where(
            Bookmark.user_id == user_id
        ).order_by(
            Bookmark.created_at.desc()
        ).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_bookmark_count(self, user_id: UUID) -> int:
        """
        Get total number of bookmarks for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total number of bookmarks
        """
        query = select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def remove_bookmark(self, post_id: UUID, user_id: UUID) -> bool:
        """
        Remove a bookmark.
        
        Args:
            post_id: UUID of the post
            user_id: UUID of the user
            
        Returns:
            True if bookmark was removed, False if it didn't exist
        """
        query = delete(Bookmark).where(
            and_(
                Bookmark.post_id == post_id,
                Bookmark.user_id == user_id
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0

    async def get_post_bookmarkers(
        self,
        post_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """
        Get users who bookmarked a specific post.
        
        Args:
            post_id: UUID of the post
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of users who bookmarked the post
        """
        query = select(User).join(
            Bookmark, Bookmark.user_id == User.id
        ).where(
            Bookmark.post_id == post_id
        ).order_by(
            Bookmark.created_at.desc()
        ).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def bulk_remove_bookmarks(self, user_id: UUID, post_ids: List[UUID]) -> int:
        """
        Remove multiple bookmarks for a user.
        
        Args:
            user_id: UUID of the user
            post_ids: List of post UUIDs to unbookmark
            
        Returns:
            Number of bookmarks removed
        """
        query = delete(Bookmark).where(
            and_(
                Bookmark.user_id == user_id,
                Bookmark.post_id.in_(post_ids)
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount 