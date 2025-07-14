from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


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
