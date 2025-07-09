from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
import re

if TYPE_CHECKING:
    from .post import Post
    from .user import User

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, max_length=255, index=True)
    slug: str = Field(unique=True, max_length=255, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    posts: List["Post"] = Relationship(
        back_populates="tags",
        sa_relationship_kwargs={"secondary": "post_tags"}
    )
    followers: List["User"] = Relationship(
        back_populates="followed_topics",
        sa_relationship_kwargs={"secondary": "user_topics"}
    )
    
    def __init__(self, **data):
        """Initialize tag with automatic slug generation if not provided."""
        if "slug" not in data and "name" in data:
            data["slug"] = self.generate_slug(data["name"])
        super().__init__(**data)
    
    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from tag name."""
        # Convert to lowercase, replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def get_url(self) -> str:
        """Generate URL for tag page."""
        return f"/tags/{self.slug}"
    
    def get_post_count(self) -> int:
        """Get count of published posts with this tag."""
        return len([post for post in self.posts if post.status == "published"])
    
    def get_follower_count(self) -> int:
        """Get count of users following this tag."""
        return len(self.followers)
    
    def get_latest_posts(self, limit: int = 5) -> List["Post"]:
        """Get latest published posts with this tag."""
        published_posts = [post for post in self.posts if post.status == "published"]
        published_posts.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
        return published_posts[:limit]
    
    def is_followed_by(self, user: "User") -> bool:
        """Check if user is following this tag."""
        return user in self.followers


# Link table for post-tag many-to-many relationship
class PostTag(SQLModel, table=True):
    __tablename__ = "post_tags"
    
    post_id: UUID = Field(foreign_key="posts.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True) 