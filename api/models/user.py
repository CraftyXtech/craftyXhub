from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
import bcrypt

if TYPE_CHECKING:
    from .post import Post
    from .comment import Comment
    from .interactions import Like, Bookmark, Follow, View
    from .tag import Tag

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(unique=True, max_length=255, index=True)
    email_verified_at: Optional[datetime] = None
    password_hash: str = Field(max_length=255)
    
    # Profile fields
    avatar: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = None
    role: str = Field(default="user", max_length=50, index=True)  # 'user', 'editor', 'admin'
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    
    # Media uploads
    media: List["Media"] = Relationship(back_populates="user")
    
    # User preferences (one-to-one)
    preferences: Optional["UserPreference"] = Relationship(back_populates="user")
    
    # Social relationships
    following: List["User"] = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={
            "secondary": "follows",
            "primaryjoin": "User.id == Follow.follower_id",
            "secondaryjoin": "User.id == Follow.followed_id",
            "overlaps": "follower,followed"
        }
    )
    
    followers: List["User"] = Relationship(
        back_populates="following",
        sa_relationship_kwargs={
            "secondary": "follows",
            "primaryjoin": "User.id == Follow.followed_id", 
            "secondaryjoin": "User.id == Follow.follower_id",
            "overlaps": "follower,followed"
        }
    )
    
    # User interaction relationships
    likes: List["Like"] = Relationship(back_populates="user")
    bookmarks: List["Bookmark"] = Relationship(back_populates="user")
    views: List["View"] = Relationship(back_populates="user")
    
    # Tag following relationship
    followed_tags: List["Tag"] = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={
            "secondary": "user_topics"
        }
    )
    
    # Read tracking relationship
    read_posts: List["UserRead"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "User.id == UserRead.user_id"
        }
    )
    
    # Authentication and role methods
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == "admin"
    
    def is_editor(self) -> bool:
        """Check if user has editor role."""
        return self.role == "editor"
    
    def is_editor_or_admin(self) -> bool:
        """Check if user has editor or admin role."""
        return self.role in ["editor", "admin"]
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Social interaction methods
    def is_following(self, user: "User") -> bool:
        """Check if this user is following another user."""
        return user in self.following
    
    def follow(self, user: "User") -> None:
        """Follow another user."""
        if not self.is_following(user) and user.id != self.id:
            self.following.append(user)
    
    def unfollow(self, user: "User") -> None:
        """Unfollow another user."""
        if self.is_following(user):
            self.following.remove(user)
    
    def get_followers_count(self) -> int:
        """Get count of followers."""
        return len(self.followers)
    
    def get_following_count(self) -> int:
        """Get count of users being followed."""
        return len(self.following)


# Link tables for many-to-many relationships
from sqlmodel import SQLModel

class UserTopic(SQLModel, table=True):
    __tablename__ = "user_topics"
    
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel, table=True):
    __tablename__ = "user_reads"
    
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    post_id: UUID = Field(foreign_key="posts.id", primary_key=True)
    read_at: datetime = Field(default_factory=datetime.utcnow)
    read_progress: int = Field(default=100, ge=0, le=100)  # Percentage (0-100)


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"
    
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    newsletter_enabled: bool = Field(default=True)
    preferred_categories: Optional[str] = None  # JSON string for array of category IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="preferences")


class Media(SQLModel, table=True):
    __tablename__ = "media"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    mime_type: str = Field(max_length=100)
    path: str = Field(max_length=500)
    disk: str = Field(default="local", max_length=50)
    size: int  # File size in bytes
    alt_text: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="media")
    
    def get_url(self) -> str:
        """Generate URL for media file."""
        return f"/media/{self.path}" 