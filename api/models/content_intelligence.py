from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .base import BaseTable


class ContentSource(BaseTable):
    __tablename__ = "content_sources"

    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, index=True)
    url = Column(String(1000), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    source_metadata = Column(JSON, nullable=True)

    category = relationship("Category")


class SiteSearchQuery(BaseTable):
    __tablename__ = "site_search_queries"

    query = Column(String(255), nullable=False, index=True)
    result_count = Column(Integer, default=0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_key = Column(String(255), nullable=True, index=True)
    source = Column(String(50), default="public_search", nullable=False)

    user = relationship("User")


class TopicBrief(BaseTable):
    __tablename__ = "topic_briefs"

    title = Column(String(255), nullable=False)
    angle = Column(Text, nullable=True)
    audience = Column(String(255), nullable=True)
    keywords = Column(JSON, nullable=True)
    source_signals = Column(JSON, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    category = relationship("Category")
    created_by = relationship("User")


class PostQualityReview(BaseTable):
    __tablename__ = "post_quality_reviews"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    checks = Column(JSON, nullable=False)
    needs_human_review = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, default=100, nullable=False)
    status = Column(String(20), default="needs_review", nullable=False, index=True)
    override_reason = Column(Text, nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)

    post = relationship("Post", backref="quality_reviews")
    approved_by = relationship("User")


class DistributionAsset(BaseTable):
    __tablename__ = "distribution_assets"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    asset_metadata = Column(JSON, nullable=True)
    tracked_url = Column(String(1000), nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)

    post = relationship("Post", backref="distribution_assets")
    approved_by = relationship("User")
    tracking_links = relationship(
        "TrackingLink",
        back_populates="distribution_asset",
        cascade="all, delete-orphan",
    )


class TrackingLink(BaseTable):
    __tablename__ = "tracking_links"

    token = Column(String(80), unique=True, nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    distribution_asset_id = Column(
        Integer,
        ForeignKey("distribution_assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    platform = Column(String(50), nullable=False, index=True)
    destination_url = Column(String(1000), nullable=False)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(150), nullable=True)
    click_count = Column(Integer, default=0, nullable=False)

    post = relationship("Post")
    distribution_asset = relationship("DistributionAsset", back_populates="tracking_links")
    clicks = relationship("TrackingClick", back_populates="tracking_link", cascade="all, delete-orphan")


class TrackingClick(BaseTable):
    __tablename__ = "tracking_clicks"

    tracking_link_id = Column(
        Integer,
        ForeignKey("tracking_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_hash = Column(String(80), nullable=True)
    user_agent = Column(String(255), nullable=True)
    referrer = Column(String(1000), nullable=True)

    tracking_link = relationship("TrackingLink", back_populates="clicks")
    user = relationship("User")
