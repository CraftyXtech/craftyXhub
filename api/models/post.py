import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import  BaseTable, post_tags, post_likes

class Category(BaseTable):
    __tablename__ = 'categories'

    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    posts = relationship("Post", back_populates="category")


class Tag(BaseTable):
    __tablename__ = 'tags'

    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")


class Post(BaseTable):
    __tablename__ = 'posts'

    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)  
    featured_image = Column(String(500), nullable=True) 
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    reading_time = Column(Integer, nullable=True)  
    meta_title = Column(String(200), nullable=True)  
    meta_description = Column(String(300), nullable=True)  
    published_at = Column(DateTime, nullable=True)
   

    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    liked_by = relationship("User", secondary=post_likes, back_populates="liked_posts")

