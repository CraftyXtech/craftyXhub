"""
Collection Models
Models for the My Collection feature: Reading Lists, Reading History, Highlights
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import text
from .base import BaseTable


class ReadingList(BaseTable):
    """Custom reading list for organizing posts"""
    __tablename__ = 'reading_lists'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    cover_image = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reading_lists")
    items = relationship("ReadingListItem", back_populates="reading_list", cascade="all, delete-orphan", order_by="ReadingListItem.position")


class ReadingListItem(BaseTable):
    """A post saved to a reading list"""
    __tablename__ = 'reading_list_items'
    
    list_id = Column(Integer, ForeignKey('reading_lists.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    note = Column(Text, nullable=True)  # User's note on this post
    position = Column(Integer, default=0)  # Order in list
    
    # Relationships
    reading_list = relationship("ReadingList", back_populates="items")
    post = relationship("Post")


class ReadingHistory(BaseTable):
    """Auto-tracked post views for reading history"""
    __tablename__ = 'reading_history'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    read_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    read_progress = Column(Integer, default=0)  # Percentage 0-100
    
    # Relationships
    user = relationship("User", back_populates="reading_history")
    post = relationship("Post")


class Highlight(BaseTable):
    """Saved text highlights from posts"""
    __tablename__ = 'highlights'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    text = Column(Text, nullable=False)  # The highlighted text
    note = Column(Text, nullable=True)  # User's annotation
    position_start = Column(Integer, nullable=True)  # Character position in content
    position_end = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="highlights")
    post = relationship("Post")
