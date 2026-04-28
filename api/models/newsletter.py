from sqlalchemy import Boolean, Column, String

from .base import BaseTable


class NewsletterSubscriber(BaseTable):
    __tablename__ = "newsletter_subscribers"

    email = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), default="homepage", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
