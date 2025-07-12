from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint

if TYPE_CHECKING:
    from .user import User
    from .post import Post
    from .comment import Comment

from .tag import PostTag
from .comment import Comment

class Like(SQLModel, table=True):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "likeable_type", "likeable_id", name="uix_user_likeable"),
    )
    
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    
    likeable_type: str = Field(max_length=50, index=True) 
    likeable_id: UUID = Field(index=True)
    
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="likes")
    
    def __init__(self, **data):
        """Initialize like with validation."""
        super().__init__(**data)
        self._validate_likeable_type()
    
    def _validate_likeable_type(self) -> None:
        """Validate that likeable_type is valid."""
        if self.likeable_type not in ['post', 'comment']:
            raise ValueError("likeable_type must be 'post' or 'comment'")
    
    def get_likeable_object(self):
        """Get the actual likeable object (Post or Comment)."""
        # This would require database session to fetch
        # Implementation depends on the specific use case
        pass
    
    model_config = {
        "table": True,
        "str_strip_whitespace": True,
    }


class Bookmark(SQLModel, table=True):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uix_user_post_bookmark"),
    )
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    post_id: UUID = Field(foreign_key="posts.id", index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="bookmarks")
    post: Optional["Post"] = Relationship(back_populates="bookmarks")
    
    model_config = {
        "table": True,
        "str_strip_whitespace": True,
    }


class Follow(SQLModel, table=True):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uix_follower_followed"),
    )
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    follower_id: UUID = Field(foreign_key="users.id", index=True)
    followed_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    follower: Optional["User"] = Relationship(
        back_populates="following",
        sa_relationship_kwargs={
            "foreign_keys": "[Follow.follower_id]",
            "overlaps": "following,followers"
        }
    )
    followed: Optional["User"] = Relationship(
        back_populates="followers", 
        sa_relationship_kwargs={
            "foreign_keys": "[Follow.followed_id]",
            "overlaps": "following,followers"
        }
    )
    
    def __init__(self, **data):
        """Initialize follow with validation."""
        super().__init__(**data)
        self._validate_self_follow()
    
    def _validate_self_follow(self) -> None:
        """Validate that user is not following themselves."""
        if self.follower_id == self.followed_id:
            raise ValueError("User cannot follow themselves")
    
    model_config = {
        "table": True,
        "str_strip_whitespace": True,
    }


class View(SQLModel, table=True):
    __tablename__ = "views"
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    post_id: UUID = Field(foreign_key="posts.id", index=True)
    user_id: Optional[UUID] = Field(foreign_key="users.id", index=True, default=None)  # Nullable for anonymous views
    
    # Analytics fields
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 support
    user_agent: Optional[str] = None
    
    # Timestamp
    viewed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    post: Optional["Post"] = Relationship(back_populates="views")
    user: Optional["User"] = Relationship(back_populates="views")
    
    def is_anonymous(self) -> bool:
        """Check if this is an anonymous view."""
        return self.user_id is None
    
    def get_browser_info(self) -> dict:
        """Parse user agent to extract browser information."""
        # Simple user agent parsing - in production, use a proper library
        if not self.user_agent:
            return {"browser": "Unknown", "os": "Unknown"}
        
        user_agent = self.user_agent.lower()
        
        # Basic browser detection
        if "chrome" in user_agent:
            browser = "Chrome"
        elif "firefox" in user_agent:
            browser = "Firefox"
        elif "safari" in user_agent:
            browser = "Safari"
        elif "edge" in user_agent:
            browser = "Edge"
        else:
            browser = "Unknown"
        
        # Basic OS detection
        if "windows" in user_agent:
            os = "Windows"
        elif "mac" in user_agent:
            os = "macOS"
        elif "linux" in user_agent:
            os = "Linux"
        elif "android" in user_agent:
            os = "Android"
        elif "ios" in user_agent:
            os = "iOS"
        else:
            os = "Unknown"
        
        return {"browser": browser, "os": os}


# Analytics helper functions
class AnalyticsHelper:
    """Helper class for analytics queries."""
    
    @staticmethod
    def get_post_engagement_stats(post_id: UUID) -> dict:
        """Get engagement statistics for a post."""
        # This would require database session and actual queries
        # Implementation depends on the specific use case
        return {
            "likes": 0,
            "bookmarks": 0,
            "views": 0,
            "comments": 0
        }
    
    @staticmethod
    def get_user_activity_stats(user_id: UUID) -> dict:
        """Get activity statistics for a user."""
        # This would require database session and actual queries
        # Implementation depends on the specific use case
        return {
            "posts_liked": 0,
            "posts_bookmarked": 0,
            "posts_viewed": 0,
            "comments_made": 0,
            "followers": 0,
            "following": 0
        }
    
    @staticmethod
    def get_popular_posts(limit: int = 10, timeframe_days: int = 7) -> List[UUID]:
        """Get most popular posts based on engagement."""
        # This would require database session and actual queries
        # Implementation depends on the specific use case
        return []
    
    @staticmethod
    def get_trending_tags(limit: int = 10) -> List[UUID]:
        """Get trending tags based on recent activity."""
        # This would require database session and actual queries
        # Implementation depends on the specific use case
        return [] 