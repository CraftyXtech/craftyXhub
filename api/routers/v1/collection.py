"""
Collection API Router
Endpoints for My Collection feature: Reading Lists, Reading History, Highlights
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from services.collection_service import CollectionService
from services.user.auth import get_current_active_user
from database.connection import get_db_session
from models import User
from schemas.collection import (
    ReadingListCreate,
    ReadingListUpdate,
    ReadingListItemCreate,
    ReadingListResponse,
    ReadingListDetailResponse,
    ReadingListListResponse,
    ReadingHistoryResponse,
    HighlightCreate,
    HighlightListResponse,
)

router = APIRouter(prefix="/collection", tags=["collection"])


# ===== Reading Lists =====

@router.get("/lists", response_model=ReadingListListResponse)
async def get_reading_lists(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get current user's reading lists"""
    lists = await CollectionService.get_user_lists(session, current_user.id)
    
    # Add item count to each list
    result = []
    for reading_list in lists:
        result.append({
            "uuid": reading_list.uuid,
            "name": reading_list.name,
            "description": reading_list.description,
            "is_public": reading_list.is_public,
            "cover_image": reading_list.cover_image,
            "item_count": len(reading_list.items) if reading_list.items else 0,
            "created_at": reading_list.created_at,
            "updated_at": reading_list.updated_at
        })
    
    return {"lists": result, "total": len(result)}


@router.post("/lists", response_model=ReadingListResponse, status_code=status.HTTP_201_CREATED)
async def create_reading_list(
    data: ReadingListCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new reading list"""
    reading_list = await CollectionService.create_list(session, current_user.id, data)
    return {
        "uuid": reading_list.uuid,
        "name": reading_list.name,
        "description": reading_list.description,
        "is_public": reading_list.is_public,
        "cover_image": reading_list.cover_image,
        "item_count": 0,
        "created_at": reading_list.created_at,
        "updated_at": reading_list.updated_at
    }


@router.get("/lists/{list_uuid}", response_model=ReadingListDetailResponse)
async def get_reading_list(
    list_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get a reading list with its items"""
    reading_list = await CollectionService.get_list_by_uuid(session, list_uuid, current_user.id)
    
    # Build items with post info
    items = []
    for item in sorted(reading_list.items, key=lambda x: x.position):
        if item.post:
            items.append({
                "uuid": item.uuid,
                "note": item.note,
                "position": item.position,
                "created_at": item.created_at,
                "post": {
                    "uuid": item.post.uuid,
                    "title": item.post.title,
                    "slug": item.post.slug,
                    "excerpt": item.post.excerpt,
                    "featured_image": item.post.featured_image,
                    "author_name": item.post.author.full_name if item.post.author else None,
                    "created_at": item.post.created_at
                }
            })
    
    return {
        "uuid": reading_list.uuid,
        "name": reading_list.name,
        "description": reading_list.description,
        "is_public": reading_list.is_public,
        "cover_image": reading_list.cover_image,
        "item_count": len(items),
        "created_at": reading_list.created_at,
        "updated_at": reading_list.updated_at,
        "items": items
    }


@router.put("/lists/{list_uuid}", response_model=ReadingListResponse)
async def update_reading_list(
    list_uuid: str,
    data: ReadingListUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a reading list"""
    reading_list = await CollectionService.update_list(session, list_uuid, current_user.id, data)
    return {
        "uuid": reading_list.uuid,
        "name": reading_list.name,
        "description": reading_list.description,
        "is_public": reading_list.is_public,
        "cover_image": reading_list.cover_image,
        "item_count": len(reading_list.items) if reading_list.items else 0,
        "created_at": reading_list.created_at,
        "updated_at": reading_list.updated_at
    }


@router.delete("/lists/{list_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading_list(
    list_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a reading list"""
    await CollectionService.delete_list(session, list_uuid, current_user.id)
    return None


@router.post("/lists/{list_uuid}/posts", status_code=status.HTTP_201_CREATED)
async def add_post_to_list(
    list_uuid: str,
    data: ReadingListItemCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Add a post to a reading list"""
    item = await CollectionService.add_post_to_list(
        session, list_uuid, current_user.id, data.post_uuid, data.note
    )
    return {"message": "Post added to list", "item_uuid": item.uuid}


@router.delete("/lists/{list_uuid}/posts/{post_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post_from_list(
    list_uuid: str,
    post_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Remove a post from a reading list"""
    await CollectionService.remove_post_from_list(session, list_uuid, current_user.id, post_uuid)
    return None


# ===== Reading History =====

@router.get("/history", response_model=ReadingHistoryResponse)
async def get_reading_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get user's reading history"""
    entries, total = await CollectionService.get_reading_history(session, current_user.id, skip, limit)
    
    result = []
    for entry in entries:
        if entry.post:
            result.append({
                "uuid": entry.uuid,
                "read_at": entry.read_at,
                "read_progress": entry.read_progress,
                "post": {
                    "uuid": entry.post.uuid,
                    "title": entry.post.title,
                    "slug": entry.post.slug,
                    "excerpt": entry.post.excerpt,
                    "featured_image": entry.post.featured_image,
                    "author_name": entry.post.author.full_name if entry.post.author else None,
                    "created_at": entry.post.created_at
                }
            })
    
    return {"entries": result, "total": total}


@router.post("/history/{post_uuid}")
async def record_post_view(
    post_uuid: str,
    progress: int = Query(0, ge=0, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Record a post view in reading history"""
    entry = await CollectionService.record_post_view(session, current_user.id, post_uuid, progress)
    return {"message": "View recorded", "entry_uuid": entry.uuid}


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_reading_history(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Clear all reading history"""
    await CollectionService.clear_reading_history(session, current_user.id)
    return None


# ===== Highlights (Phase 2) =====

@router.get("/highlights", response_model=HighlightListResponse)
async def get_highlights(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get user's highlights"""
    highlights, total = await CollectionService.get_user_highlights(session, current_user.id, skip, limit)
    
    result = []
    for highlight in highlights:
        if highlight.post:
            result.append({
                "uuid": highlight.uuid,
                "text": highlight.text,
                "note": highlight.note,
                "position_start": highlight.position_start,
                "position_end": highlight.position_end,
                "created_at": highlight.created_at,
                "post": {
                    "uuid": highlight.post.uuid,
                    "title": highlight.post.title,
                    "slug": highlight.post.slug,
                    "excerpt": highlight.post.excerpt,
                    "featured_image": highlight.post.featured_image,
                    "author_name": highlight.post.author.full_name if highlight.post.author else None,
                    "created_at": highlight.post.created_at
                }
            })
    
    return {"highlights": result, "total": total}


@router.post("/highlights", status_code=status.HTTP_201_CREATED)
async def create_highlight(
    data: HighlightCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new highlight"""
    highlight = await CollectionService.create_highlight(session, current_user.id, data)
    return {"message": "Highlight created", "highlight_uuid": highlight.uuid}


@router.delete("/highlights/{highlight_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_highlight(
    highlight_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a highlight"""
    await CollectionService.delete_highlight(session, highlight_uuid, current_user.id)
    return None
