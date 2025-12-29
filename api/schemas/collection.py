"""
Collection Schemas
Pydantic schemas for My Collection feature
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===== Reading List Schemas =====

class ReadingListCreate(BaseModel):
    """Schema for creating a reading list"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: bool = False
    cover_image: Optional[str] = None


class ReadingListUpdate(BaseModel):
    """Schema for updating a reading list"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image: Optional[str] = None


class ReadingListItemCreate(BaseModel):
    """Schema for adding a post to a reading list"""
    post_uuid: str
    note: Optional[str] = None


class ReadingListItemUpdate(BaseModel):
    """Schema for updating an item in a reading list"""
    note: Optional[str] = None
    position: Optional[int] = None


class ReadingListItemReorder(BaseModel):
    """Schema for reordering items in a list"""
    item_uuids: List[str]  # Ordered list of item UUIDs


# ===== Response Schemas =====

class PostSummary(BaseModel):
    """Minimal post info for display in lists"""
    uuid: str
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReadingListItemResponse(BaseModel):
    """Response schema for a reading list item"""
    uuid: str
    note: Optional[str] = None
    position: int
    created_at: datetime
    post: PostSummary

    class Config:
        from_attributes = True


class ReadingListResponse(BaseModel):
    """Response schema for a reading list"""
    uuid: str
    name: str
    description: Optional[str] = None
    is_public: bool
    cover_image: Optional[str] = None
    item_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReadingListDetailResponse(ReadingListResponse):
    """Response schema for a reading list with items"""
    items: List[ReadingListItemResponse] = []


class ReadingListListResponse(BaseModel):
    """Response schema for list of reading lists"""
    lists: List[ReadingListResponse]
    total: int


# ===== Reading History Schemas =====

class ReadingHistoryEntry(BaseModel):
    """Response schema for a reading history entry"""
    uuid: str
    read_at: datetime
    read_progress: int
    post: PostSummary

    class Config:
        from_attributes = True


class ReadingHistoryResponse(BaseModel):
    """Response schema for reading history"""
    entries: List[ReadingHistoryEntry]
    total: int


# ===== Highlight Schemas (Phase 2) =====

class HighlightCreate(BaseModel):
    """Schema for creating a highlight"""
    post_uuid: str
    text: str = Field(..., min_length=1)
    note: Optional[str] = None
    position_start: Optional[int] = None
    position_end: Optional[int] = None


class HighlightResponse(BaseModel):
    """Response schema for a highlight"""
    uuid: str
    text: str
    note: Optional[str] = None
    position_start: Optional[int] = None
    position_end: Optional[int] = None
    created_at: datetime
    post: PostSummary

    class Config:
        from_attributes = True


class HighlightListResponse(BaseModel):
    """Response schema for list of highlights"""
    highlights: List[HighlightResponse]
    total: int
