from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseTable, post_likes, post_bookmarks, user_follows



class MediaType(PyEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class UserRole(PyEnum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class User(BaseTable):
    __tablename__ = 'users'
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    provider = Column(String(50), nullable=True, default="email")  # e.g., "google", "github"
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    liked_posts = relationship("Post", secondary=post_likes, back_populates="liked_by")
    bookmarked_posts = relationship("Post", secondary=post_bookmarks, back_populates="bookmarked_by")
    
    following = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=lambda: User.id == user_follows.c.follower_id,
        secondaryjoin=lambda: User.id == user_follows.c.followed_id,
        back_populates="followers",
        cascade="all, delete"
    )
    
    followers = relationship(
        "User",
        secondary=user_follows,
        primaryjoin=lambda: User.id == user_follows.c.followed_id,
        secondaryjoin=lambda: User.id == user_follows.c.follower_id,
        back_populates="following",
        cascade="all, delete"
    )
    
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def is_moderator(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    
    def is_following(self, user):
        return user in self.following
    
    def get_follower_count(self):
        return len(self.followers) if self.followers else 0

    def get_following_count(self):
        return len(self.following) if self.following else 0

class Profile(BaseTable):
    __tablename__ = 'profiles'
    
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    avatar = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    twitter_handle = Column(String(50), nullable=True)
    github_handle = Column(String(50), nullable=True)
    linkedin_handle = Column(String(50), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    follower_notifications = Column(Boolean, default=True)  # Email notifications for new followers
    user = relationship("User", back_populates="profile")
    

class Media(BaseTable):
    __tablename__ = 'media'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(Enum(MediaType), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    user = relationship("User", backref="media")
