from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseTable


class CommentReport(BaseTable):
    """Model for reporting inappropriate comments"""
    __tablename__ = 'comment_reports'

    comment_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='pending')  # pending, reviewed, dismissed
    
    comment = relationship("Comment")
    user = relationship("User")
