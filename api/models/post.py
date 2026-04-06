from  datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, text
from sqlalchemy.orm import relationship
from .base import  Base, BaseTable, post_tags, post_likes, post_bookmarks

class Category(BaseTable):
    __tablename__ = 'categories'

    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    posts = relationship("Post", back_populates="category")
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    parent = relationship("Category", remote_side='Category.id', back_populates="subcategories")
    subcategories = relationship("Category", back_populates="parent")
    slug_history = relationship(
        "CategorySlugHistory",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class Tag(BaseTable):
    __tablename__ = 'tags'

    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    canonical_tag_id = Column(Integer, ForeignKey('tags.id'), nullable=True)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
    category = relationship("Category", foreign_keys=[category_id])
    canonical_tag = relationship(
        "Tag",
        remote_side="Tag.id",
        foreign_keys=[canonical_tag_id],
        backref="deprecated_variants",
    )
    slug_history = relationship(
        "TagSlugHistory",
        back_populates="tag",
        cascade="all, delete-orphan",
    )


class Post(BaseTable):
    __tablename__ = 'posts'

    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    content_blocks = Column(JSON, nullable=True)
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
    seo_keywords = Column(JSON, nullable=True)
    published_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True, default=None)
    is_reviewed = Column(Boolean, default=False, nullable=False)
    review_comments = Column(Text, nullable=True)
    is_flagged = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    liked_by = relationship("User", secondary=post_likes, back_populates="liked_posts")
    bookmarked_by = relationship("User", secondary=post_bookmarks, back_populates="bookmarked_posts")

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class CategorySlugHistory(Base):
    __tablename__ = 'category_slug_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    category = relationship("Category", back_populates="slug_history")


class TagSlugHistory(Base):
    __tablename__ = 'tag_slug_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    tag = relationship("Tag", back_populates="slug_history")
