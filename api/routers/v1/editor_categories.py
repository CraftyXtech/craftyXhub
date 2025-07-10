

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.editor_permissions import (
    require_editor_or_admin,
    verify_category_permissions
)
from models.user import User
from services.editor.category_service import CategoryService
from schemas.editor.categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListRequest,
    CategoryUsageResponse,
    CategoryStatsResponse,
    BulkCategoryRequest,
    CategoryMergeRequest
)

router = APIRouter(prefix="/editor/categories", tags=["Editor - Categories"])


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreateRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category."""
    service = CategoryService(db)
    try:
        return await service.create_category(category_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    search: Optional[str] = Query(None, description="Search categories"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category"),
    level: Optional[int] = Query(None, description="Filter by hierarchy level"),
    include_usage: bool = Query(False, description="Include usage statistics"),
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all categories with optional filtering."""
    service = CategoryService(db)
    query = CategoryListRequest(
        search=search,
        parent_id=parent_id,
        level=level,
        include_usage=include_usage
    )
    return await service.list_categories(query, current_user)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category by ID."""
    service = CategoryService(db)
    category = await service.get_category(category_id, current_user)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdateRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing category."""
    service = CategoryService(db)
    try:
        return await service.update_category(category_id, category_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a category."""
    service = CategoryService(db)
    try:
        await service.delete_category(category_id, current_user)
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}/usage", response_model=CategoryUsageResponse)
async def get_category_usage(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get category usage statistics."""
    service = CategoryService(db)
    usage = await service.get_category_usage(category_id, current_user)
    if not usage:
        raise HTTPException(status_code=404, detail="Category not found")
    return usage


@router.get("/{category_id}/stats", response_model=CategoryStatsResponse)
async def get_category_stats(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed category statistics."""
    service = CategoryService(db)
    stats = await service.get_category_stats(category_id, current_user)
    if not stats:
        raise HTTPException(status_code=404, detail="Category not found")
    return stats


@router.get("/{category_id}/children", response_model=List[CategoryResponse])
async def get_category_children(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all child categories of a parent category."""
    service = CategoryService(db)
    return await service.get_category_children(category_id, current_user)


@router.post("/bulk", response_model=dict)
async def bulk_category_operation(
    request: BulkCategoryRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk operations on categories."""
    service = CategoryService(db)
    try:
        return await service.bulk_operation(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/merge", response_model=CategoryResponse)
async def merge_categories(
    request: CategoryMergeRequest,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Merge multiple categories into one."""
    service = CategoryService(db)
    try:
        return await service.merge_categories(request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hierarchy/tree", response_model=List[CategoryResponse])
async def get_category_tree(
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get the complete category hierarchy tree."""
    service = CategoryService(db)
    return await service.get_category_tree(current_user)


@router.post("/{category_id}/reorder")
async def reorder_categories(
    category_id: UUID,
    new_order: int,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """Reorder categories within their hierarchy level."""
    service = CategoryService(db)
    try:
        await service.reorder_category(category_id, new_order, current_user)
        return {"message": "Category reordered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 