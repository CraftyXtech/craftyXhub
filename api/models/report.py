from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseTable


class Report(BaseTable):
    __tablename__ = 'reports'

    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    post = relationship("Post")
    user = relationship("User")