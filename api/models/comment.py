
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, comment_likes
import uuid


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    # Comments are auto-approved; no manual admin approval needed
    is_approved = Column(Boolean, default=True)
    likes_count = Column(Integer, default=0)
    # created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=text("(datetime('now'))"))
    updated_at = Column(DateTime(timezone=True), 
                      server_default=text("(datetime('now'))"),
                      onupdate=text("(datetime('now'))"))
    

    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    liked_by = relationship("User", secondary=comment_likes, backref="liked_comments")

