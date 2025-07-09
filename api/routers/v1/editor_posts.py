"""
Editor Posts API Router

Provides endpoints for post management in the editor module.
Follows SubPRD-PostManagement.md specifications.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.editor_permissions import (
    require_editor_or_admin,
    verify_post_ownership,
    verify_post_edit_permissions,
    verify_post_publish_permissions
)
from models.user import User
from services.editor.post_service import PostService
from schemas.editor.posts import (
    PostCreateRequest,
    PostUpdateRequest,
    PostListRequest,
    PostResponse,
    PostSummaryResponse,
    BulkPostRequest,
    PostRevisionResponse,
    WorkflowHistoryResponse,
    AutoSaveRequest,
    PostSubmitReviewRequest,
    PostResubmitRequest
)

router = APIRouter(prefix="/editor/posts", tags=["Editor - Posts"])


@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreateRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post."""
    service = PostService(db)
    try:
        return await service.create_post(post_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PostSummaryResponse])
async def list_posts(
    search: Optional[str] = Query(None, description="Search posts"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    tag_id: Optional[UUID] = Query(None, description="Filter by tag"),
    sort_by: str = Query("updated_at", description="Sort by field"),
    sort_direction: str = Query("desc", description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """List posts with filtering and pagination."""
    service = PostService(db)
    query = PostListRequest(
        search=search,
        status=status,
        category_id=category_id,
        tag_id=tag_id,
        sort_by=sort_by,
        sort_direction=sort_direction,
        page=page,
        per_page=per_page
    )
    result = await service.list_posts(query, current_user)
    return result.get("posts", [])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific post by ID."""
    service = PostService(db)
    post = await service.get_post(post_id, current_user)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    post_data: PostUpdateRequest,
    current_user: User = Depends(verify_post_edit_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing post."""
    service = PostService(db)
    try:
        return await service.update_post(post_id, post_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(verify_post_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Delete a post."""
    service = PostService(db)
    try:
        await service.delete_post(post_id, current_user)
        return {"message": "Post deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/submit-review", response_model=PostResponse)
async def submit_for_review(
    post_id: UUID,
    request: PostSubmitReviewRequest,
    current_user: User = Depends(verify_post_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Submit a post for review."""
    service = PostService(db)
    try:
        return await service.submit_for_review(post_id, request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/resubmit", response_model=PostResponse)
async def resubmit_post(
    post_id: UUID,
    request: PostResubmitRequest,
    current_user: User = Depends(verify_post_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Resubmit a post after rejection."""
    service = PostService(db)
    try:
        return await service.resubmit_post(post_id, request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: UUID,
    current_user: User = Depends(verify_post_publish_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Publish a post."""
    service = PostService(db)
    try:
        # Update post status to published
        from schemas.editor.posts import PostUpdateRequest
        from datetime import datetime
        
        update_data = PostUpdateRequest(
            status="published",
            published_at=datetime.utcnow()
        )
        return await service.update_post(post_id, update_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/archive", response_model=PostResponse)
async def archive_post(
    post_id: UUID,
    current_user: User = Depends(verify_post_edit_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Archive a post."""
    service = PostService(db)
    try:
        # Update post status to archived
        from schemas.editor.posts import PostUpdateRequest
        
        update_data = PostUpdateRequest(status="archived")
        return await service.update_post(post_id, update_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/duplicate", response_model=PostResponse)
async def duplicate_post(
    post_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate a post."""
    service = PostService(db)
    try:
        return await service.duplicate_post(post_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/auto-save", response_model=dict)
async def auto_save_post(
    post_id: UUID,
    request: AutoSaveRequest,
    current_user: User = Depends(verify_post_edit_permissions),
    db: AsyncSession = Depends(get_db)
):
    """Auto-save post content."""
    service = PostService(db)
    try:
        return await service.auto_save(post_id, request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{post_id}/revisions", response_model=List[PostRevisionResponse])
async def get_post_revisions(
    post_id: UUID,
    current_user: User = Depends(verify_post_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Get post revision history."""
    service = PostService(db)
    return await service.get_post_revisions(post_id, current_user)


@router.get("/{post_id}/workflow-history", response_model=List[WorkflowHistoryResponse])
async def get_workflow_history(
    post_id: UUID,
    current_user: User = Depends(verify_post_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Get post workflow history."""
    service = PostService(db)
    return await service.get_workflow_history(post_id, current_user)


@router.post("/bulk", response_model=dict)
async def bulk_post_operation(
    request: BulkPostRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk operations on posts."""
    service = PostService(db)
    try:
        return await service.bulk_operation(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/drafts/my", response_model=List[PostSummaryResponse])
async def get_my_drafts(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's draft posts."""
    service = PostService(db)
    query = PostListRequest(
        status="draft",
        sort_by="updated_at",
        sort_direction="desc"
    )
    result = await service.list_posts(query, current_user)
    return result.get("posts", [])


@router.get("/pending-review/list", response_model=List[PostSummaryResponse])
async def get_pending_review_posts(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get posts pending review."""
    service = PostService(db)
    query = PostListRequest(
        status="under_review",
        sort_by="updated_at",
        sort_direction="asc"
    )
    result = await service.list_posts(query, current_user)
    return result.get("posts", [])


@router.get("/published/recent", response_model=List[PostSummaryResponse])
async def get_recent_published_posts(
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get recently published posts."""
    service = PostService(db)
    query = PostListRequest(
        status="published",
        sort_by="published_at",
        sort_direction="desc",
        per_page=limit
    )
    result = await service.list_posts(query, current_user)
    return result.get("posts", []) 