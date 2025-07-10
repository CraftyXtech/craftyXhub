from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.editor_permissions import (
    require_editor_or_admin,
    verify_tag_permissions
)
from models.user import User
from services.editor.tag_service import TagService
from schemas.editor.tags import (
    TagCreateRequest,
    TagUpdateRequest,
    TagResponse,
    TagListRequest,
    TagUsageResponse,
    TagStatsResponse,
    BulkTagRequest,
    TagMergeRequest,
    TaxonomySuggestionsResponse
)

router = APIRouter(prefix="/editor/tags", tags=["Editor - Tags"])


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreateRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag."""
    service = TagService(db)
    try:
        return await service.create_tag(tag_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TagResponse])
async def list_tags(
    search: Optional[str] = Query(None, description="Search tags"),
    sort_by: str = Query("name", description="Sort by: name, usage_count, created_at"),
    sort_direction: str = Query("asc", description="Sort direction: asc, desc"),
    min_usage: Optional[int] = Query(None, description="Minimum usage count"),
    max_usage: Optional[int] = Query(None, description="Maximum usage count"),
    include_usage: bool = Query(False, description="Include usage statistics"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all tags with optional filtering."""
    service = TagService(db)
    query = TagListRequest(
        search=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        min_usage=min_usage,
        max_usage=max_usage,
        include_usage=include_usage
    )
    return await service.list_tags(query, current_user)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tag by ID."""
    service = TagService(db)
    tag = await service.get_tag(tag_id, current_user)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_data: TagUpdateRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing tag."""
    service = TagService(db)
    try:
        return await service.update_tag(tag_id, tag_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a tag."""
    service = TagService(db)
    try:
        await service.delete_tag(tag_id, current_user)
        return {"message": "Tag deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tag_id}/usage", response_model=TagUsageResponse)
async def get_tag_usage(
    tag_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get tag usage statistics."""
    service = TagService(db)
    usage = await service.get_tag_usage(tag_id, current_user)
    if not usage:
        raise HTTPException(status_code=404, detail="Tag not found")
    return usage


@router.get("/{tag_id}/stats", response_model=TagStatsResponse)
async def get_tag_stats(
    tag_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed tag statistics."""
    service = TagService(db)
    stats = await service.get_tag_stats(tag_id, current_user)
    if not stats:
        raise HTTPException(status_code=404, detail="Tag not found")
    return stats


@router.get("/trending/list", response_model=List[TagResponse])
async def get_trending_tags(
    limit: int = Query(10, description="Number of trending tags to return"),
    days: int = Query(7, description="Number of days to look back for trending"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get trending tags based on recent usage."""
    service = TagService(db)
    return await service.get_trending_tags(limit, days, current_user)


@router.get("/suggestions/taxonomy", response_model=TaxonomySuggestionsResponse)
async def get_taxonomy_suggestions(
    content: str = Query(..., description="Content to analyze for tag suggestions"),
    limit: int = Query(5, description="Number of suggestions to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get tag suggestions based on content analysis."""
    service = TagService(db)
    return await service.get_taxonomy_suggestions(content, limit, current_user)


@router.post("/bulk", response_model=dict)
async def bulk_tag_operation(
    request: BulkTagRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk operations on tags."""
    service = TagService(db)
    try:
        return await service.bulk_operation(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/merge", response_model=TagResponse)
async def merge_tags(
    request: TagMergeRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Merge multiple tags into one."""
    service = TagService(db)
    try:
        return await service.merge_tags(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/similar/{tag_id}", response_model=List[TagResponse])
async def get_similar_tags(
    tag_id: UUID,
    limit: int = Query(5, description="Number of similar tags to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get tags similar to the specified tag."""
    service = TagService(db)
    return await service.get_similar_tags(tag_id, limit, current_user)


@router.get("/unused/list", response_model=List[TagResponse])
async def get_unused_tags(
    days: int = Query(30, description="Number of days to consider as unused"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get tags that haven't been used recently."""
    service = TagService(db)
    return await service.get_unused_tags(days, current_user)


@router.post("/cleanup/unused")
async def cleanup_unused_tags(
    days: int = Query(30, description="Number of days to consider as unused"),
    dry_run: bool = Query(True, description="Perform a dry run without actual deletion"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Clean up unused tags."""
    service = TagService(db)
    try:
        result = await service.cleanup_unused_tags(days, dry_run, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 