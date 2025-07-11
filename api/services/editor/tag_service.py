
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload

from models.tag import Tag
from models.post import Post
from models.interactions import PostTag
from models.user import User
from schemas.editor.tags import (
    TagCreateRequest,
    TagUpdateRequest,
    TagResponse,
    TagListRequest,
    TagStatsResponse,
    TagUsageResponse,
    BulkTagRequest,
    TagMergeRequest,
    TaxonomySuggestionsResponse
)
from dependencies.editor_permissions import check_tag_permissions
from schemas.post import AuthorResponse


class TagService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tag(
        self, 
        tag_data: TagCreateRequest, 
        current_user: User
    ) -> TagResponse:
        """Create a new tag."""
        # Generate slug if not provided
        slug = tag_data.slug or self._generate_slug(tag_data.name)
        
        # Check if slug is unique
        if await self._is_slug_taken(slug):
            raise ValueError("Slug already exists")
        
        # Create tag
        tag = Tag(
            name=tag_data.name,
            slug=slug,
            created_by=current_user.id,
            post_count=0,
            usage_trend=0.0,
            last_used_at=None
        )
        
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        
        return await self._build_tag_response(tag, current_user)
    
    async def update_tag(
        self, 
        tag_id: UUID, 
        tag_data: TagUpdateRequest, 
        current_user: User
    ) -> TagResponse:
        """Update an existing tag."""
        tag = await self._get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("Tag not found")
        
        # Update fields
        if tag_data.name:
            tag.name = tag_data.name
        
        if tag_data.slug:
            if await self._is_slug_taken(tag_data.slug, exclude_id=tag_id):
                raise ValueError("Slug already exists")
            tag.slug = tag_data.slug
        elif tag_data.name:
            # Regenerate slug if name changed but slug not provided
            new_slug = self._generate_slug(tag_data.name)
            if await self._is_slug_taken(new_slug, exclude_id=tag_id):
                raise ValueError("Generated slug already exists")
            tag.slug = new_slug
        
        tag.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(tag)
        
        return await self._build_tag_response(tag, current_user)
    
    async def delete_tag(self, tag_id: UUID, current_user: User) -> bool:
        """Delete a tag if it has no posts."""
        tag = await self._get_tag_by_id(tag_id)
        if not tag:
            raise ValueError("Tag not found")
        
        # Check if tag has posts
        post_count = await self._get_tag_post_count(tag_id)
        if post_count > 0:
            raise ValueError("Cannot delete tag with associated posts")
        
        await self.db.delete(tag)
        await self.db.commit()
        return True
    
    async def list_tags(
        self, 
        query: TagListRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """List tags with filtering and pagination."""
        # Build query
        stmt = select(Tag).options(
            selectinload(Tag.created_by_user)
        )
        
        # Apply filters
        if query.search:
            stmt = stmt.where(Tag.name.ilike(f"%{query.search}%"))
        
        if query.min_usage is not None:
            stmt = stmt.where(Tag.post_count >= query.min_usage)
        
        if query.max_usage is not None:
            stmt = stmt.where(Tag.post_count <= query.max_usage)
        
        # Apply sorting
        if query.sort_by == "name":
            order_col = Tag.name
        elif query.sort_by == "post_count":
            order_col = Tag.post_count
        elif query.sort_by == "usage_trend":
            order_col = Tag.usage_trend
        elif query.sort_by == "created_at":
            order_col = Tag.created_at
        elif query.sort_by == "last_used_at":
            order_col = Tag.last_used_at
        else:
            order_col = Tag.name
        
        if query.sort_direction == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(asc(order_col))
        
        # Apply pagination
        total_stmt = select(func.count(Tag.id))
        if query.search:
            total_stmt = total_stmt.where(Tag.name.ilike(f"%{query.search}%"))
        if query.min_usage is not None:
            total_stmt = total_stmt.where(Tag.post_count >= query.min_usage)
        if query.max_usage is not None:
            total_stmt = total_stmt.where(Tag.post_count <= query.max_usage)
        
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()
        
        offset = (query.page - 1) * query.per_page
        stmt = stmt.offset(offset).limit(query.per_page)
        
        result = await self.db.execute(stmt)
        tags = result.scalars().all()
        
        # Build response
        tag_responses = []
        for tag in tags:
            tag_responses.append(await self._build_tag_response(tag, current_user))
        
        return {
            "tags": tag_responses,
            "total": total,
            "page": query.page,
            "per_page": query.per_page,
            "total_pages": (total + query.per_page - 1) // query.per_page
        }
    
    async def get_tag_stats(self, current_user: User) -> TagStatsResponse:
        """Get tag usage statistics."""
        # Total tags
        total_result = await self.db.execute(select(func.count(Tag.id)))
        total_tags = total_result.scalar()
        
        # Tags with posts
        with_posts_result = await self.db.execute(
            select(func.count(Tag.id)).where(Tag.post_count > 0)
        )
        tags_with_posts = with_posts_result.scalar()
        
        # Unused tags
        unused_tags = total_tags - tags_with_posts
        
        # Trending tags (high usage trend)
        trending_result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.created_by_user))
            .where(Tag.usage_trend > 0)
            .order_by(desc(Tag.usage_trend))
            .limit(10)
        )
        trending = trending_result.scalars().all()
        
        # Popular tags (high post count)
        popular_result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.created_by_user))
            .where(Tag.post_count > 0)
            .order_by(desc(Tag.post_count))
            .limit(10)
        )
        popular = popular_result.scalars().all()
        
        # Recent tags
        recent_result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.created_by_user))
            .order_by(desc(Tag.created_at))
            .limit(10)
        )
        recent = recent_result.scalars().all()
        
        # Build usage responses
        trending_tags = []
        for tag in trending:
            usage_percentage = (tag.post_count / total_tags * 100) if total_tags > 0 else 0
            trending_tags.append(TagUsageResponse(
                tag=await self._build_tag_response(tag, current_user),
                post_count=tag.post_count,
                usage_percentage=usage_percentage,
                trend_score=tag.usage_trend
            ))
        
        popular_tags = []
        for tag in popular:
            usage_percentage = (tag.post_count / total_tags * 100) if total_tags > 0 else 0
            popular_tags.append(TagUsageResponse(
                tag=await self._build_tag_response(tag, current_user),
                post_count=tag.post_count,
                usage_percentage=usage_percentage,
                trend_score=tag.usage_trend
            ))
        
        recent_tags = []
        for tag in recent:
            recent_tags.append(await self._build_tag_response(tag, current_user))
        
        return TagStatsResponse(
            total_tags=total_tags,
            tags_with_posts=tags_with_posts,
            unused_tags=unused_tags,
            trending_tags=trending_tags,
            popular_tags=popular_tags,
            recent_tags=recent_tags
        )
    
    async def bulk_operation(
        self, 
        request: BulkTagRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Perform bulk operations on tags."""
        if request.action == "delete":
            return await self._bulk_delete(request.tag_ids, current_user)
        elif request.action == "merge":
            if not request.target_id:
                raise ValueError("Target ID required for merge operation")
            return await self._bulk_merge(request.tag_ids, request.target_id, current_user)
        elif request.action == "update":
            if not request.updates:
                raise ValueError("Updates required for update operation")
            return await self._bulk_update(request.tag_ids, request.updates, current_user)
        else:
            raise ValueError("Invalid bulk operation")
    
    async def merge_tags(
        self, 
        request: TagMergeRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Merge multiple tags into a target tag."""
        target_tag = await self._get_tag_by_id(request.target_tag_id)
        if not target_tag:
            raise ValueError("Target tag not found")
        
        # Get source tags
        source_tags = []
        for source_id in request.source_tag_ids:
            tag = await self._get_tag_by_id(source_id)
            if not tag:
                raise ValueError(f"Source tag {source_id} not found")
            source_tags.append(tag)
        
        # Move post associations from source tags to target tag
        total_moved = 0
        for source_tag in source_tags:
            # Update post_tag associations
            await self.db.execute(
                PostTag.__table__.update()
                .where(PostTag.tag_id == source_tag.id)
                .values(tag_id=target_tag.id)
            )
            
            total_moved += source_tag.post_count
            
            # Delete source tag if requested
            if request.delete_source_tags:
                await self.db.delete(source_tag)
        
        # Update target tag post count and usage trend
        target_tag.post_count += total_moved
        target_tag.usage_trend = await self._calculate_usage_trend(target_tag.id)
        target_tag.last_used_at = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "message": f"Merged {len(source_tags)} tags into {target_tag.name}",
            "posts_moved": total_moved,
            "target_tag": await self._build_tag_response(target_tag, current_user)
        }
    
    async def get_suggestions(
        self, 
        query: str, 
        current_user: User
    ) -> TaxonomySuggestionsResponse:
        """Get taxonomy suggestions based on query."""
        # Tag suggestions based on similarity
        tag_suggestions = await self._get_tag_suggestions(query)
        
        # Similar tags
        similar_tags_result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.created_by_user))
            .where(Tag.name.ilike(f"%{query}%"))
            .limit(10)
        )
        similar_tags = similar_tags_result.scalars().all()
        
        # Build similar tag responses
        similar_tag_responses = []
        for tag in similar_tags:
            similar_tag_responses.append(await self._build_tag_response(tag, current_user))
        
        return TaxonomySuggestionsResponse(
            category_suggestions=[],  # TODO: Implement category suggestions
            tag_suggestions=tag_suggestions,
            similar_categories=[],  # TODO: Implement similar categories
            similar_tags=similar_tag_responses
        )
    
    # Private helper methods
    
    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from tag name."""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    async def _is_slug_taken(self, slug: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a slug is already taken."""
        stmt = select(Tag).where(Tag.slug == slug)
        if exclude_id:
            stmt = stmt.where(Tag.id != exclude_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def _get_tag_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Get tag by ID."""
        result = await self.db.execute(
            select(Tag)
            .options(selectinload(Tag.created_by_user))
            .where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_tag_post_count(self, tag_id: UUID) -> int:
        """Get the number of posts with this tag."""
        result = await self.db.execute(
            select(func.count(PostTag.post_id)).where(PostTag.tag_id == tag_id)
        )
        return result.scalar()
    
    async def _calculate_usage_trend(self, tag_id: UUID) -> float:
        """Calculate usage trend for a tag."""
        # Simple implementation - could be enhanced with time-based analysis
        post_count = await self._get_tag_post_count(tag_id)
        if post_count == 0:
            return 0.0
        
        # Calculate trend based on recent usage
        recent_usage_result = await self.db.execute(
            select(func.count(PostTag.post_id))
            .join(Post)
            .where(
                PostTag.tag_id == tag_id,
                Post.created_at >= func.now() - text("INTERVAL '30 days'")
            )
        )
        recent_usage = recent_usage_result.scalar()
        
        return (recent_usage / post_count) * 100 if post_count > 0 else 0.0
    
    async def _get_tag_suggestions(self, query: str) -> List[str]:
        """Get tag suggestions based on query."""
        # Simple implementation - could be enhanced with ML
        result = await self.db.execute(
            select(Tag.name)
            .where(Tag.name.ilike(f"%{query}%"))
            .order_by(desc(Tag.post_count))
            .limit(10)
        )
        return [tag_name for tag_name in result.scalars().all()]
    
    async def _build_tag_response(self, tag: Tag, current_user: User) -> TagResponse:
        """Build tag response with permissions."""
        permissions = check_tag_permissions(tag, current_user)
        
        # Build author response
        author = AuthorResponse(
            id=tag.created_by_user.id,
            name=tag.created_by_user.name,
            avatar=tag.created_by_user.avatar
        )
        
        return TagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            post_count=tag.post_count,
            usage_trend=tag.usage_trend,
            created_by=author,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
            last_used_at=tag.last_used_at,
            can_edit=permissions["can_edit"],
            can_delete=permissions["can_delete"]
        )
    
    async def _bulk_delete(self, tag_ids: List[UUID], current_user: User) -> Dict[str, Any]:
        """Bulk delete tags."""
        deleted_count = 0
        errors = []
        
        for tag_id in tag_ids:
            try:
                await self.delete_tag(tag_id, current_user)
                deleted_count += 1
            except ValueError as e:
                errors.append(f"Tag {tag_id}: {str(e)}")
        
        return {
            "deleted_count": deleted_count,
            "errors": errors
        }
    
    async def _bulk_merge(self, tag_ids: List[UUID], target_id: UUID, current_user: User) -> Dict[str, Any]:
        """Bulk merge tags."""
        request = TagMergeRequest(
            source_tag_ids=tag_ids,
            target_tag_id=target_id,
            delete_source_tags=True
        )
        return await self.merge_tags(request, current_user)
    
    async def _bulk_update(self, tag_ids: List[UUID], updates: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Bulk update tags."""
        updated_count = 0
        errors = []
        
        for tag_id in tag_ids:
            try:
                update_request = TagUpdateRequest(**updates)
                await self.update_tag(tag_id, update_request, current_user)
                updated_count += 1
            except Exception as e:
                errors.append(f"Tag {tag_id}: {str(e)}")
        
        return {
            "updated_count": updated_count,
            "errors": errors
        } 