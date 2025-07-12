from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
import re

if TYPE_CHECKING:
    from .user import User, UserRead
    from .category import Category
    from .tag import Tag
    from .comment import Comment
    from .interactions import Like, Bookmark, View

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    category_id: Optional[UUID] = Field(foreign_key="categories.id", index=True, default=None)
    title: str = Field(max_length=255)
    slug: str = Field(unique=True, max_length=255, index=True)
    excerpt: Optional[str] = None
    body: str  
    status: str = Field(default="draft", max_length=50, index=True)  
    published_at: Optional[datetime] = Field(default=None, index=True)
    difficulty_level: Optional[str] = Field(default=None, max_length=50)
    featured: bool = Field(default=False, index=True)
    comments_enabled: bool = Field(default=True)
    generated_image_path: Optional[str] = Field(default=None, max_length=255)
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author: Optional["User"] = Relationship(back_populates="posts")
    category: Optional["Category"] = Relationship(back_populates="posts")
    tags: List["Tag"] = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={"secondary": "post_tags"}
    )
    comments: List["Comment"] = Relationship(back_populates="post")
    
    # Social interaction relationships
    likes: List["Like"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(Post.id == foreign(Like.likeable_id), Like.likeable_type == 'post')",
            "overlaps": "user"
        }
    )
    
    bookmarks: List["Bookmark"] = Relationship(back_populates="post")
    views: List["View"] = Relationship(back_populates="post")
    
    # Read tracking relationship
    readers: List["UserRead"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Post.id == UserRead.post_id"
        }
    )
    
    def __init__(self, **data):
        """Initialize post with automatic slug generation if not provided."""
        if "slug" not in data and "title" in data:
            data["slug"] = self.generate_slug(data["title"])
        super().__init__(**data)
    
    @staticmethod
    def generate_slug(title: str) -> str:
        """Generate URL-friendly slug from post title."""
        # Convert to lowercase, replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    # Publishing workflow methods
    def is_published(self) -> bool:
        """Check if post is published."""
        return self.status == "published" and self.published_at is not None
    
    def publish(self) -> None:
        """Publish the post."""
        self.status = "published"
        if self.published_at is None:
            self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive the post."""
        self.status = "archived"
        self.updated_at = datetime.utcnow()
    
    def unpublish(self) -> None:
        """Unpublish the post (set to draft)."""
        self.status = "draft"
        self.updated_at = datetime.utcnow()
    
    # Social interaction methods
    def is_liked_by(self, user: "User") -> bool:
        """Check if post is liked by user."""
        return any(like.user_id == user.id for like in self.likes)
    
    def is_bookmarked_by(self, user: "User") -> bool:
        """Check if post is bookmarked by user."""
        return any(bookmark.user_id == user.id for bookmark in self.bookmarks)
    
    def record_read(self, user: "User", progress: int = 100) -> None:
        """Record that user has read this post."""
        # This would need to be implemented with proper session handling
        # For now, create placeholder that can be implemented in service layer
        pass
    
    # Statistics methods
    def get_like_count(self) -> int:
        """Get count of likes for this post."""
        return len(self.likes)
    
    def get_bookmark_count(self) -> int:
        """Get count of bookmarks for this post."""
        return len(self.bookmarks)
    
    def get_comment_count(self) -> int:
        """Get count of approved comments for this post."""
        return len([comment for comment in self.comments if comment.status == "approved"])
    
    def get_view_count(self) -> int:
        """Get count of views for this post."""
        return len(self.views)
    
    # URL and SEO methods
    def get_url(self) -> str:
        """Generate URL for post."""
        return f"/posts/{self.slug}"
    
    def get_reading_time(self) -> int:
        """Estimate reading time in minutes based on word count."""
        if not self.body:
            return 0
        word_count = len(self.body.split())
        # Average reading speed: 200 words per minute
        return max(1, round(word_count / 200))
    
    def get_excerpt(self, length: int = 160) -> str:
        """Get post excerpt, either from excerpt field or body."""
        if self.excerpt:
            return self.excerpt[:length]
        if self.body:
            # Strip HTML tags and get first part of body
            clean_body = re.sub(r'<[^>]+>', '', self.body)
            return clean_body[:length] + "..." if len(clean_body) > length else clean_body
        return "" 