from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseTable, post_likes, post_bookmarks

class User(BaseTable):

    __tablename__ = 'users'

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    liked_posts = relationship("Post", secondary=post_likes, back_populates="liked_by")
    bookmarked_posts = relationship("Post", secondary=post_bookmarks, back_populates="bookmarked_by")



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
    user = relationship("User", back_populates="profile")
