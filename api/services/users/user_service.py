from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import Session, select, and_, func
from sqlalchemy.orm import selectinload

from models.user import User
from models.interactions import Follow, Like, Bookmark, View
from models.tag import Tag
from models.post import Post
from core.exceptions import ResourceNotFoundException, ValidationException


class UserService:
    """Service class for handling user social interactions and relationships."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Following/Followers functionality
    async def follow_user(self, follower_id: UUID, followed_id: UUID) -> Follow:
        """Follow a user."""
        if follower_id == followed_id:
            raise ValidationException("Users cannot follow themselves")
        
        # Check if users exist
        follower = await self.get_user_by_id(follower_id)
        followed = await self.get_user_by_id(followed_id)
        
        if not follower or not followed:
            raise ResourceNotFoundException("User not found")
        
        # Check if already following
        existing_follow = self.session.exec(
            select(Follow).where(
                and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            )
        ).first()
        
        if existing_follow:
            return existing_follow
        
        # Create new follow relationship
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        self.session.add(follow)
        self.session.commit()
        self.session.refresh(follow)
        
        return follow
    
    async def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> bool:
        """Unfollow a user."""
        follow = self.session.exec(
            select(Follow).where(
                and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            )
        ).first()
        
        if not follow:
            return False
        
        self.session.delete(follow)
        self.session.commit()
        return True
    
    async def get_followers(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[User]:
        """Get user's followers."""
        followers = self.session.exec(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.followed_id == user_id)
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(followers)
    
    async def get_following(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[User]:
        """Get users that user is following."""
        following = self.session.exec(
            select(User)
            .join(Follow, Follow.followed_id == User.id)
            .where(Follow.follower_id == user_id)
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(following)
    
    async def get_followers_count(self, user_id: UUID) -> int:
        """Get count of user's followers."""
        count = self.session.exec(
            select(func.count(Follow.id)).where(Follow.followed_id == user_id)
        ).first()
        
        return count or 0
    
    async def get_following_count(self, user_id: UUID) -> int:
        """Get count of users being followed."""
        count = self.session.exec(
            select(func.count(Follow.id)).where(Follow.follower_id == user_id)
        ).first()
        
        return count or 0
    
    async def is_following(self, follower_id: UUID, followed_id: UUID) -> bool:
        """Check if user is following another user."""
        follow = self.session.exec(
            select(Follow).where(
                and_(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            )
        ).first()
        
        return follow is not None
    
    # User activity and statistics
    async def get_user_activity_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive user activity statistics."""
        # Posts count
        posts_count = self.session.exec(
            select(func.count(Post.id)).where(Post.user_id == user_id)
        ).first() or 0
        
        # Likes given count
        likes_given = self.session.exec(
            select(func.count(Like.id)).where(Like.user_id == user_id)
        ).first() or 0
        
        # Bookmarks count
        bookmarks_count = self.session.exec(
            select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        ).first() or 0
        
        # Posts viewed count
        views_count = self.session.exec(
            select(func.count(View.id)).where(View.user_id == user_id)
        ).first() or 0
        
        # Followers and following counts
        followers_count = await self.get_followers_count(user_id)
        following_count = await self.get_following_count(user_id)
        
        return {
            "posts_created": posts_count,
            "likes_given": likes_given,
            "bookmarks_count": bookmarks_count,
            "posts_viewed": views_count,
            "followers_count": followers_count,
            "following_count": following_count
        }
    
    async def get_user_liked_posts(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[Post]:
        """Get posts liked by user."""
        liked_posts = self.session.exec(
            select(Post)
            .join(Like, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
            .where(Like.user_id == user_id)
            .options(selectinload(Post.author))
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(liked_posts)
    
    async def get_user_bookmarked_posts(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[Post]:
        """Get posts bookmarked by user."""
        bookmarked_posts = self.session.exec(
            select(Post)
            .join(Bookmark, Bookmark.post_id == Post.id)
            .where(Bookmark.user_id == user_id)
            .options(selectinload(Post.author))
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(bookmarked_posts)
    
    async def get_user_read_posts(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get posts read by user with reading progress."""
        read_records = self.session.exec(
            select(UserRead, Post)
            .join(Post, UserRead.post_id == Post.id)
            .where(UserRead.user_id == user_id)
            .options(selectinload(Post.author))
            .offset(offset)
            .limit(limit)
        ).all()
        
        return [
            {
                "post": record[1],
                "read_at": record[0].read_at,
                "read_progress": record[0].read_progress
            }
            for record in read_records
        ]
    
    # Tag following functionality
    async def follow_tag(self, user_id: UUID, tag_id: UUID) -> bool:
        """Follow a tag."""
        # Check if user and tag exist
        user = await self.get_user_by_id(user_id)
        tag = self.session.exec(select(Tag).where(Tag.id == tag_id)).first()
        
        if not user or not tag:
            raise ResourceNotFoundException("User or tag not found")
        
        # Check if already following
        from models.user import UserTopic
        existing = self.session.exec(
            select(UserTopic).where(
                and_(UserTopic.user_id == user_id, UserTopic.tag_id == tag_id)
            )
        ).first()
        
        if existing:
            return False
        
        # Create new follow relationship
        user_topic = UserTopic(user_id=user_id, tag_id=tag_id)
        self.session.add(user_topic)
        self.session.commit()
        
        return True
    
    async def unfollow_tag(self, user_id: UUID, tag_id: UUID) -> bool:
        """Unfollow a tag."""
        from models.user import UserTopic
        user_topic = self.session.exec(
            select(UserTopic).where(
                and_(UserTopic.user_id == user_id, UserTopic.tag_id == tag_id)
            )
        ).first()
        
        if not user_topic:
            return False
        
        self.session.delete(user_topic)
        self.session.commit()
        return True
    
    async def get_followed_tags(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[Tag]:
        """Get tags followed by user."""
        from models.user import UserTopic
        followed_tags = self.session.exec(
            select(Tag)
            .join(UserTopic, UserTopic.tag_id == Tag.id)
            .where(UserTopic.user_id == user_id)
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(followed_tags)
    
    # Helper methods
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.session.exec(select(User).where(User.id == user_id)).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.session.exec(select(User).where(User.email == email)).first()
    
    async def get_mutual_followers(self, user1_id: UUID, user2_id: UUID) -> List[User]:
        """Get mutual followers between two users."""
        mutual_followers = self.session.exec(
            select(User)
            .join(Follow.alias("f1"), User.id == Follow.follower_id)
            .join(Follow.alias("f2"), User.id == Follow.follower_id)
            .where(
                and_(
                    Follow.followed_id == user1_id,
                    Follow.followed_id == user2_id
                )
            )
        ).all()
        
        return list(mutual_followers)
    
    async def get_user_recommendations(self, user_id: UUID, limit: int = 10) -> List[User]:
        """Get user recommendations based on mutual connections and interests."""
        # Get users followed by people the current user follows
        # This is a simplified recommendation algorithm
        recommendations = self.session.exec(
            select(User)
            .join(Follow.alias("f1"), User.id == Follow.followed_id)
            .join(Follow.alias("f2"), Follow.follower_id == Follow.follower_id)
            .where(
                and_(
                    Follow.follower_id == user_id,
                    User.id != user_id,
                    # Exclude users already being followed
                    ~User.id.in_(
                        select(Follow.followed_id).where(Follow.follower_id == user_id)
                    )
                )
            )
            .distinct()
            .limit(limit)
        ).all()
        
        return list(recommendations) 