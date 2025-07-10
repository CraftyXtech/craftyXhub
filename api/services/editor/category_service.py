

import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from models.category import Category
from models.post import Post
from models.user import User
from schemas.editor.categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
    CategoryListRequest,
    CategoryStatsResponse,
    CategoryUsageResponse,
    BulkCategoryRequest,
    CategoryMergeRequest
)
from dependencies.editor_permissions import check_category_permissions
from schemas.post import AuthorResponse


class CategoryService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_category(
        self, 
        category_data: CategoryCreateRequest, 
        current_user: User
    ) -> CategoryResponse:
        """Create a new category."""
        # Generate slug if not provided
        slug = category_data.slug or self._generate_slug(category_data.name)
        
        # Check if slug is unique
        if await self._is_slug_taken(slug):
            raise ValueError("Slug already exists")
        
        # Validate parent category if provided
        parent_category = None
        if category_data.parent_id:
            parent_category = await self._get_category_by_id(category_data.parent_id)
            if not parent_category:
                raise ValueError("Parent category not found")
        
        # Create category
        category = Category(
            name=category_data.name,
            slug=slug,
            description=category_data.description,
            parent_id=category_data.parent_id,
            created_by=current_user.id,
            post_count=0,
            hierarchy_path=self._build_hierarchy_path(category_data.name, parent_category)
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return await self._build_category_response(category, current_user)
    
    async def update_category(
        self, 
        category_id: UUID, 
        category_data: CategoryUpdateRequest, 
        current_user: User
    ) -> CategoryResponse:
        """Update an existing category."""
        category = await self._get_category_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Update fields
        if category_data.name:
            category.name = category_data.name
        
        if category_data.slug:
            if await self._is_slug_taken(category_data.slug, exclude_id=category_id):
                raise ValueError("Slug already exists")
            category.slug = category_data.slug
        elif category_data.name:
            # Regenerate slug if name changed but slug not provided
            new_slug = self._generate_slug(category_data.name)
            if await self._is_slug_taken(new_slug, exclude_id=category_id):
                raise ValueError("Generated slug already exists")
            category.slug = new_slug
        
        if category_data.description is not None:
            category.description = category_data.description
        
        if category_data.parent_id is not None:
            if category_data.parent_id == category.id:
                raise ValueError("Category cannot be its own parent")
            
            # Validate parent category
            if category_data.parent_id:
                parent_category = await self._get_category_by_id(category_data.parent_id)
                if not parent_category:
                    raise ValueError("Parent category not found")
                
                # Check for circular reference
                if await self._would_create_circular_reference(category.id, category_data.parent_id):
                    raise ValueError("Circular reference detected")
            
            category.parent_id = category_data.parent_id
        
        category.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(category)
        
        return await self._build_category_response(category, current_user)
    
    async def delete_category(self, category_id: UUID, current_user: User) -> bool:
        """Delete a category if it has no posts."""
        category = await self._get_category_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Check if category has posts
        post_count = await self._get_category_post_count(category_id)
        if post_count > 0:
            raise ValueError("Cannot delete category with associated posts")
        
        # Check if category has child categories
        child_count = await self._get_child_category_count(category_id)
        if child_count > 0:
            raise ValueError("Cannot delete category with child categories")
        
        await self.db.delete(category)
        await self.db.commit()
        return True
    
    async def list_categories(
        self, 
        query: CategoryListRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """List categories with filtering and pagination."""
        # Build query
        stmt = select(Category).options(
            selectinload(Category.parent),
            selectinload(Category.children),
            selectinload(Category.created_by_user)
        )
        
        # Apply filters
        if query.search:
            stmt = stmt.where(
                or_(
                    Category.name.ilike(f"%{query.search}%"),
                    Category.description.ilike(f"%{query.search}%")
                )
            )
        
        if query.parent_id:
            stmt = stmt.where(Category.parent_id == query.parent_id)
        
        # Apply sorting
        if query.sort_by == "name":
            order_col = Category.name
        elif query.sort_by == "post_count":
            order_col = Category.post_count
        elif query.sort_by == "created_at":
            order_col = Category.created_at
        else:
            order_col = Category.name
        
        if query.sort_direction == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(asc(order_col))
        
        # Apply pagination
        total_stmt = select(func.count(Category.id))
        if query.search:
            total_stmt = total_stmt.where(
                or_(
                    Category.name.ilike(f"%{query.search}%"),
                    Category.description.ilike(f"%{query.search}%")
                )
            )
        if query.parent_id:
            total_stmt = total_stmt.where(Category.parent_id == query.parent_id)
        
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()
        
        offset = (query.page - 1) * query.per_page
        stmt = stmt.offset(offset).limit(query.per_page)
        
        result = await self.db.execute(stmt)
        categories = result.scalars().all()
        
        # Build response
        category_responses = []
        for category in categories:
            category_responses.append(await self._build_category_response(category, current_user))
        
        return {
            "categories": category_responses,
            "total": total,
            "page": query.page,
            "per_page": query.per_page,
            "total_pages": (total + query.per_page - 1) // query.per_page
        }
    
    async def get_category_stats(self, current_user: User) -> CategoryStatsResponse:
        """Get category usage statistics."""
        # Total categories
        total_result = await self.db.execute(select(func.count(Category.id)))
        total_categories = total_result.scalar()
        
        # Categories with posts
        with_posts_result = await self.db.execute(
            select(func.count(Category.id)).where(Category.post_count > 0)
        )
        categories_with_posts = with_posts_result.scalar()
        
        # Unused categories
        unused_categories = total_categories - categories_with_posts
        
        # Most used categories
        most_used_result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.created_by_user))
            .where(Category.post_count > 0)
            .order_by(desc(Category.post_count))
            .limit(10)
        )
        most_used = most_used_result.scalars().all()
        
        # Recent categories
        recent_result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.created_by_user))
            .order_by(desc(Category.created_at))
            .limit(10)
        )
        recent = recent_result.scalars().all()
        
        # Calculate hierarchy depth
        max_depth_result = await self.db.execute(
            select(func.max(func.array_length(func.string_to_array(Category.hierarchy_path, '/'), 1)))
        )
        hierarchy_depth = max_depth_result.scalar() or 0
        
        # Build usage responses
        most_used_categories = []
        for category in most_used:
            usage_percentage = (category.post_count / total_categories * 100) if total_categories > 0 else 0
            most_used_categories.append(CategoryUsageResponse(
                category=await self._build_category_response(category, current_user),
                post_count=category.post_count,
                usage_percentage=usage_percentage,
                recent_growth=0  # TODO: Calculate recent growth
            ))
        
        recent_categories = []
        for category in recent:
            recent_categories.append(await self._build_category_response(category, current_user))
        
        return CategoryStatsResponse(
            total_categories=total_categories,
            categories_with_posts=categories_with_posts,
            unused_categories=unused_categories,
            most_used_categories=most_used_categories,
            recent_categories=recent_categories,
            hierarchy_depth=hierarchy_depth
        )
    
    async def bulk_operation(
        self, 
        request: BulkCategoryRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Perform bulk operations on categories."""
        if request.action == "delete":
            return await self._bulk_delete(request.category_ids, current_user)
        elif request.action == "merge":
            if not request.target_id:
                raise ValueError("Target ID required for merge operation")
            return await self._bulk_merge(request.category_ids, request.target_id, current_user)
        elif request.action == "update":
            if not request.updates:
                raise ValueError("Updates required for update operation")
            return await self._bulk_update(request.category_ids, request.updates, current_user)
        else:
            raise ValueError("Invalid bulk operation")
    
    async def merge_categories(
        self, 
        request: CategoryMergeRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Merge multiple categories into a target category."""
        target_category = await self._get_category_by_id(request.target_category_id)
        if not target_category:
            raise ValueError("Target category not found")
        
        # Get source categories
        source_categories = []
        for source_id in request.source_category_ids:
            category = await self._get_category_by_id(source_id)
            if not category:
                raise ValueError(f"Source category {source_id} not found")
            source_categories.append(category)
        
        # Move posts from source categories to target category
        total_moved = 0
        for source_category in source_categories:
            # Update posts to use target category
            await self.db.execute(
                Post.__table__.update()
                .where(Post.category_id == source_category.id)
                .values(category_id=target_category.id)
            )
            
            total_moved += source_category.post_count
            
            # Delete source category if requested
            if request.delete_source_tags:
                await self.db.delete(source_category)
        
        # Update target category post count
        target_category.post_count += total_moved
        
        await self.db.commit()
        
        return {
            "message": f"Merged {len(source_categories)} categories into {target_category.name}",
            "posts_moved": total_moved,
            "target_category": await self._build_category_response(target_category, current_user)
        }
    
    # Private helper methods
    
    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from category name."""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    async def _is_slug_taken(self, slug: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a slug is already taken."""
        stmt = select(Category).where(Category.slug == slug)
        if exclude_id:
            stmt = stmt.where(Category.id != exclude_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID."""
        result = await self.db.execute(
            select(Category)
            .options(
                selectinload(Category.parent),
                selectinload(Category.children),
                selectinload(Category.created_by_user)
            )
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_category_post_count(self, category_id: UUID) -> int:
        """Get the number of posts in a category."""
        result = await self.db.execute(
            select(func.count(Post.id)).where(Post.category_id == category_id)
        )
        return result.scalar()
    
    async def _get_child_category_count(self, category_id: UUID) -> int:
        """Get the number of child categories."""
        result = await self.db.execute(
            select(func.count(Category.id)).where(Category.parent_id == category_id)
        )
        return result.scalar()
    
    def _build_hierarchy_path(self, name: str, parent: Optional[Category]) -> str:
        """Build hierarchy path for category."""
        if parent:
            return f"{parent.hierarchy_path}/{name.lower()}"
        return f"/{name.lower()}"
    
    async def _would_create_circular_reference(self, category_id: UUID, parent_id: UUID) -> bool:
        """Check if setting parent would create circular reference."""
        current_parent_id = parent_id
        while current_parent_id:
            if current_parent_id == category_id:
                return True
            
            result = await self.db.execute(
                select(Category.parent_id).where(Category.id == current_parent_id)
            )
            current_parent_id = result.scalar_one_or_none()
        
        return False
    
    async def _build_category_response(self, category: Category, current_user: User) -> CategoryResponse:
        """Build category response with permissions."""
        permissions = check_category_permissions(category, current_user)
        
        # Build author response
        author = AuthorResponse(
            id=category.created_by_user.id,
            name=category.created_by_user.name,
            avatar=category.created_by_user.avatar
        )
        
        return CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            parent_id=category.parent_id,
            parent=None,  # TODO: Build parent response if needed
            children=[],  # TODO: Build children responses if needed
            hierarchy_path=category.hierarchy_path,
            post_count=category.post_count,
            created_by=author,
            created_at=category.created_at,
            updated_at=category.updated_at,
            can_edit=permissions["can_edit"],
            can_delete=permissions["can_delete"]
        )
    
    async def _bulk_delete(self, category_ids: List[UUID], current_user: User) -> Dict[str, Any]:
        """Bulk delete categories."""
        deleted_count = 0
        errors = []
        
        for category_id in category_ids:
            try:
                await self.delete_category(category_id, current_user)
                deleted_count += 1
            except ValueError as e:
                errors.append(f"Category {category_id}: {str(e)}")
        
        return {
            "deleted_count": deleted_count,
            "errors": errors
        }
    
    async def _bulk_merge(self, category_ids: List[UUID], target_id: UUID, current_user: User) -> Dict[str, Any]:
        """Bulk merge categories."""
        request = CategoryMergeRequest(
            source_category_ids=category_ids,
            target_category_id=target_id,
            delete_source_categories=True
        )
        return await self.merge_categories(request, current_user)
    
    async def _bulk_update(self, category_ids: List[UUID], updates: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Bulk update categories."""
        updated_count = 0
        errors = []
        
        for category_id in category_ids:
            try:
                update_request = CategoryUpdateRequest(**updates)
                await self.update_category(category_id, update_request, current_user)
                updated_count += 1
            except Exception as e:
                errors.append(f"Category {category_id}: {str(e)}")
        
        return {
            "updated_count": updated_count,
            "errors": errors
        } 