"""
Like Service

Business logic for post like operations following SubPRD-InteractionAPI.md specifications.
"""

from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.dialects.postgresql import insert

from models.interactions import Like
from models.post import Post
from models.user import User
from schemas.interaction import LikeToggleResponse


class LikeService:
    """Service class for post like operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle_like(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> LikeToggleResponse:
        """
        Toggle like status for a post by a user.
        
        Args:
            post_id: UUID of the post to like/unlike
            user_id: UUID of the user performing the action
            
        Returns:
            LikeToggleResponse with current like status and count
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

        # Check if user has already liked the post
        existing_like_query = select(Like).where(
            and_(
                Like.post_id == post_id,
                Like.user_id == user_id
            )
        )
        existing_like_result = await self.db.execute(existing_like_query)
        existing_like = existing_like_result.scalar_one_or_none()

        if existing_like:
            # Unlike: Remove the like
            await self.db.delete(existing_like)
            await self.db.commit()
            liked = False
            message = "Post unliked successfully"
        else:
            # Like: Add new like
            new_like = Like(
                id=uuid4(),
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            self.db.add(new_like)
            await self.db.commit()
            liked = True
            message = "Post liked successfully"

        # Get updated like count
        like_count = await self.get_like_count(post_id)

        return LikeToggleResponse(
            liked=liked,
            like_count=like_count,
            message=message,
            post_id=post_id
        )

    async def get_like_count(self, post_id: UUID) -> int:
        """
        Get total like count for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Total number of likes
        """
        query = select(func.count(Like.id)).where(Like.post_id == post_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def is_liked_by_user(self, post_id: UUID, user_id: UUID) -> bool:
        """
        Check if a post is liked by a specific user.
        
        Args:
            post_id: UUID of the post
            user_id: UUID of the user
            
        Returns:
            True if post is liked by user, False otherwise
        """
        query = select(Like).where(
            and_(
                Like.post_id == post_id,
                Like.user_id == user_id
            )
        ).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_user_likes(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[Like]:
        """
        Get posts liked by a user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of likes to return
            offset: Number of likes to skip
            
        Returns:
            List of Like objects
        """
        query = select(Like).where(
            Like.user_id == user_id
        ).order_by(Like.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_post_likes(
        self,
        post_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[Like]:
        """
        Get users who liked a post.
        
        Args:
            post_id: UUID of the post
            limit: Maximum number of likes to return
            offset: Number of likes to skip
            
        Returns:
            List of Like objects
        """
        query = select(Like).where(
            Like.post_id == post_id
        ).order_by(Like.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_user_like_count(self, user_id: UUID) -> int:
        """
        Get total number of likes given by a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total number of likes given
        """
        query = select(func.count(Like.id)).where(Like.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_user_received_likes(self, user_id: UUID) -> int:
        """
        Get total number of likes received by a user's posts.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total number of likes received
        """
        query = select(func.count(Like.id)).select_from(
            Like.__table__.join(Post.__table__, Like.post_id == Post.id)
        ).where(Post.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_most_liked_posts(
        self,
        limit: int = 10,
        days: Optional[int] = None
    ) -> list[dict]:
        """
        Get most liked posts with like counts.
        
        Args:
            limit: Maximum number of posts to return
            days: Optional number of days to look back
            
        Returns:
            List of dictionaries with post_id and like_count
        """
        query = select(
            Like.post_id,
            func.count(Like.id).label('like_count')
        ).group_by(Like.post_id)

        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.where(Like.created_at >= cutoff_date)

        query = query.order_by(func.count(Like.id).desc()).limit(limit)

        result = await self.db.execute(query)
        return [
            {
                'post_id': row.post_id,
                'like_count': row.like_count
            }
            for row in result
        ]

    async def bulk_check_likes(
        self,
        post_ids: list[UUID],
        user_id: UUID
    ) -> dict[UUID, bool]:
        """
        Check like status for multiple posts by a user.
        
        Args:
            post_ids: List of post UUIDs to check
            user_id: UUID of the user
            
        Returns:
            Dictionary mapping post_id to like status
        """
        if not post_ids:
            return {}

        query = select(Like.post_id).where(
            and_(
                Like.post_id.in_(post_ids),
                Like.user_id == user_id
            )
        )

        result = await self.db.execute(query)
        liked_post_ids = {row.post_id for row in result}

        return {
            post_id: post_id in liked_post_ids
            for post_id in post_ids
        }

    async def unlike_all_by_user(self, user_id: UUID) -> int:
        """
        Remove all likes by a user (for user deletion).
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of likes removed
        """
        # Get count before deletion
        count_query = select(func.count(Like.id)).where(Like.user_id == user_id)
        count_result = await self.db.execute(count_query)
        delete_count = count_result.scalar() or 0

        # Delete all likes by user
        delete_query = delete(Like).where(Like.user_id == user_id)
        await self.db.execute(delete_query)
        await self.db.commit()

        return delete_count 