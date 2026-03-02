from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
