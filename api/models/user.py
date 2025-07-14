from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(unique=True, max_length=255, index=True)
    email_verified_at: Optional[datetime] = None
    password: str = Field(max_length=255)

    avatar: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = None
    role: str = Field(default="user", max_length=50, index=True)
