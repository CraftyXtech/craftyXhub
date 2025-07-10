from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
import re

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .post import Post


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
   
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, max_length=255, index=True)
    slug: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = None
    
   
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
   
    posts: List["Post"] = Relationship(back_populates="category")
    
    def __init__(self, **data):
        """Initialize category with automatic slug generation if not provided."""
        if "slug" not in data and "name" in data:
            data["slug"] = self.generate_slug(data["name"])
        super().__init__(**data)
    
    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from category name."""
        # Convert to lowercase, replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def get_url(self) -> str:
        """Generate URL for category page."""
        return f"/categories/{self.slug}"
    
    def get_post_count(self) -> int:
        """Get count of published posts in this category."""
        return len([post for post in self.posts if post.status == "published"])
    
    def get_latest_posts(self, limit: int = 5) -> List["Post"]:
        """Get latest published posts in this category."""
        published_posts = [post for post in self.posts if post.status == "published"]
        published_posts.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
        return published_posts[:limit] 