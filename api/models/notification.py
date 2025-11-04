from .base import BaseTable
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from schemas.notification import NotificationType


class Notification(BaseTable):
    __tablename__ = 'notifications'
    
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)    
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)    
    notification_type = Column(
        Enum(
            NotificationType,
            name="notificationtype",
            values_callable=lambda obj: [e.value for e in obj], 
        ),
        nullable=False,
        index=True,
    )
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=True)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(500), nullable=True)    
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)    
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_notifications")
    post = relationship("Post", backref="notifications")
    comment = relationship("Comment", backref="notifications")
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_email_sent(self):
        self.email_sent = True
        self.email_sent_at = datetime.utcnow()