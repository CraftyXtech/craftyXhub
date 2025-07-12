
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.dialects.postgresql import insert

from models.interactions import Follow
from models.user import User
from schemas.interaction import FollowToggleResponse


class FollowService:
    """Service for managing user follow relationships."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def toggle_follow(
        self,
        follower_id: UUID,
        followed_id: UUID
    ) -> FollowToggleResponse:
        """
        Toggle follow status between two users.
        
        Args:
            follower_id: UUID of the user doing the following
            followed_id: UUID of the user being followed
            
        Returns:
            FollowToggleResponse with current follow status
        """
        # Prevent self-following
        if follower_id == followed_id:
            raise ValueError("Users cannot follow themselves")

        # Verify both users exist
        follower_query = select(User).where(User.id == follower_id)
        follower_result = await self.db.execute(follower_query)
        follower = follower_result.scalar_one_or_none()

        followed_query = select(User).where(User.id == followed_id)
        followed_result = await self.db.execute(followed_query)
        followed = followed_result.scalar_one_or_none()

        if not follower or not followed:
            raise ValueError("One or both users not found")

        # Check if already following
        existing_follow_query = select(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        )
        existing_follow_result = await self.db.execute(existing_follow_query)
        existing_follow = existing_follow_result.scalar_one_or_none()

        if existing_follow:
            # Unfollow: Remove the follow relationship
            await self.db.delete(existing_follow)
            await self.db.commit()
            following = False
            message = "User unfollowed successfully"
        else:
            # Follow: Add new follow relationship
            new_follow = Follow(
                id=uuid4(),
                follower_id=follower_id,
                followed_id=followed_id,
                created_at=datetime.utcnow()
            )
            self.db.add(new_follow)
            await self.db.commit()
            following = True
            message = "User followed successfully"

        # Get updated follower count for the followed user
        follower_count = await self.get_follower_count(followed_id)
        following_count = await self.get_following_count(follower_id)

        return FollowToggleResponse(
            following=following,
            follower_count=follower_count,
            following_count=following_count,
            message=message,
            followed_user_id=followed_id
        )

    async def get_follower_count(self, user_id: UUID) -> int:
        """
        Get total follower count for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total number of followers
        """
        query = select(func.count(Follow.id)).where(Follow.followed_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_following_count(self, user_id: UUID) -> int:
        """
        Get total following count for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total number of users being followed
        """
        query = select(func.count(Follow.id)).where(Follow.follower_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def is_following(self, follower_id: UUID, followed_id: UUID) -> bool:
        """
        Check if one user is following another.
        
        Args:
            follower_id: UUID of the potential follower
            followed_id: UUID of the potential followed user
            
        Returns:
            True if following relationship exists, False otherwise
        """
        query = select(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        ).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_followers(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """
        Get followers for a specific user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of followers to return
            offset: Number of followers to skip
            
        Returns:
            List of follower users
        """
        query = select(User).join(
            Follow, Follow.follower_id == User.id
        ).where(
            Follow.followed_id == user_id
        ).order_by(
            Follow.created_at.desc()
        ).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_following(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """
        Get users that a specific user is following.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of followed users to return
            offset: Number of followed users to skip
            
        Returns:
            List of followed users
        """
        query = select(User).join(
            Follow, Follow.followed_id == User.id
        ).where(
            Follow.follower_id == user_id
        ).order_by(
            Follow.created_at.desc()
        ).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_mutual_follows(
        self,
        user1_id: UUID,
        user2_id: UUID
    ) -> List[User]:
        """
        Get users that both users are following (mutual connections).
        
        Args:
            user1_id: UUID of the first user
            user2_id: UUID of the second user
            
        Returns:
            List of mutually followed users
        """
        query = select(User).join(
            Follow, Follow.followed_id == User.id
        ).where(
            and_(
                Follow.follower_id == user1_id,
                Follow.followed_id.in_(
                    select(Follow.followed_id).where(
                        Follow.follower_id == user2_id
                    )
                )
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> bool:
        """
        Remove a follow relationship.
        
        Args:
            follower_id: UUID of the follower
            followed_id: UUID of the followed user
            
        Returns:
            True if follow was removed, False if it didn't exist
        """
        query = delete(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0

    async def bulk_unfollow(self, follower_id: UUID, followed_ids: List[UUID]) -> int:
        """
        Remove multiple follow relationships for a user.
        
        Args:
            follower_id: UUID of the follower
            followed_ids: List of user UUIDs to unfollow
            
        Returns:
            Number of follows removed
        """
        query = delete(Follow).where(
            and_(
                Follow.follower_id == follower_id,
                Follow.followed_id.in_(followed_ids)
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount

    async def get_follow_suggestions(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[User]:
        """
        Get follow suggestions for a user based on mutual connections.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested users to follow
        """
        # Get users followed by people the user follows (friends of friends)
        # but exclude users already followed and the user themselves
        query = select(User).join(
            Follow, Follow.followed_id == User.id
        ).where(
            and_(
                Follow.follower_id.in_(
                    select(Follow.followed_id).where(
                        Follow.follower_id == user_id
                    )
                ),
                Follow.followed_id != user_id,
                Follow.followed_id.not_in(
                    select(Follow.followed_id).where(
                        Follow.follower_id == user_id
                    )
                )
            )
        ).group_by(User.id).order_by(
            func.count(Follow.id).desc()
        ).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all() 