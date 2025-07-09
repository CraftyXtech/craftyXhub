"""Post service for editor module."""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, update, delete
from sqlalchemy.orm import selectinload

from models.post import Post
from models.user import User
from models.category import Category
from models.tag import Tag
from models.interactions import PostTag, View, Like, Comment
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
from dependencies.editor_permissions import check_post_permissions
from schemas.auth import AuthorResponse
from schemas.post import CategoryResponse, TagResponse


class PostService:
    """Service for managing posts in editor module."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_post(
        self, 
        post_data: PostCreateRequest, 
        current_user: User
    ) -> PostResponse:
        """Create a new post."""
        # Generate slug from title
        slug = self._generate_slug(post_data.title)
        
        # Ensure slug is unique
        unique_slug = await self._ensure_unique_slug(slug)
        
        # Create post
        post = Post(
            title=post_data.title,
            slug=unique_slug,
            body=post_data.body,
            excerpt=post_data.excerpt,
            featured_image_path=post_data.featured_image_path,
            category_id=post_data.category_id,
            status=post_data.status,
            published_at=post_data.published_at,
            comments_enabled=post_data.comments_enabled,
            user_id=current_user.id,
            difficulty_level=None,
            featured=False,
            feedback=None
        )
        
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        
        # Add tags if provided
        if post_data.tags:
            await self._add_tags_to_post(post.id, post_data.tags)
        
        # Create initial revision
        await self._create_revision(post, current_user, "Initial creation")
        
        return await self._build_post_response(post, current_user)
    
    async def update_post(
        self, 
        post_id: UUID, 
        post_data: PostUpdateRequest, 
        current_user: User
    ) -> PostResponse:
        """Update an existing post."""
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        # Store changes for revision
        changes = []
        
        # Update fields
        if post_data.title and post_data.title != post.title:
            changes.append(f"Title changed from '{post.title}' to '{post_data.title}'")
            post.title = post_data.title
            
            # Regenerate slug if title changed
            new_slug = self._generate_slug(post_data.title)
            unique_slug = await self._ensure_unique_slug(new_slug, exclude_id=post_id)
            if unique_slug != post.slug:
                changes.append(f"Slug changed from '{post.slug}' to '{unique_slug}'")
                post.slug = unique_slug
        
        if post_data.body and post_data.body != post.body:
            changes.append("Content updated")
            post.body = post_data.body
        
        if post_data.excerpt is not None and post_data.excerpt != post.excerpt:
            changes.append("Excerpt updated")
            post.excerpt = post_data.excerpt
        
        if post_data.featured_image_path is not None and post_data.featured_image_path != post.featured_image_path:
            changes.append("Featured image updated")
            post.featured_image_path = post_data.featured_image_path
        
        if post_data.category_id is not None and post_data.category_id != post.category_id:
            changes.append("Category updated")
            post.category_id = post_data.category_id
        
        if post_data.status and post_data.status != post.status:
            changes.append(f"Status changed from '{post.status}' to '{post_data.status}'")
            post.status = post_data.status
        
        if post_data.published_at is not None and post_data.published_at != post.published_at:
            changes.append("Publication date updated")
            post.published_at = post_data.published_at
        
        if post_data.comments_enabled is not None and post_data.comments_enabled != post.comments_enabled:
            changes.append("Comments setting updated")
            post.comments_enabled = post_data.comments_enabled
        
        # Update tags if provided
        if post_data.tags is not None:
            await self._update_post_tags(post.id, post_data.tags)
            changes.append("Tags updated")
        
        post.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(post)
        
        # Create revision if there were changes
        if changes:
            await self._create_revision(post, current_user, "; ".join(changes))
        
        return await self._build_post_response(post, current_user)
    
    async def delete_post(self, post_id: UUID, current_user: User) -> bool:
        """Delete a post."""
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        # Remove all associations
        await self._remove_post_associations(post_id)
        
        # Delete the post
        await self.db.delete(post)
        await self.db.commit()
        
        return True
    
    async def list_posts(
        self, 
        query: PostListRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """List posts with filtering and pagination."""
        # Build query
        stmt = select(Post).options(
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.author)
        ).where(Post.user_id == current_user.id)
        
        # Apply filters
        if query.search:
            stmt = stmt.where(
                or_(
                    Post.title.ilike(f"%{query.search}%"),
                    Post.body.ilike(f"%{query.search}%"),
                    Post.excerpt.ilike(f"%{query.search}%")
                )
            )
        
        if query.status:
            stmt = stmt.where(Post.status == query.status)
        
        if query.category_id:
            stmt = stmt.where(Post.category_id == query.category_id)
        
        if query.tag_id:
            stmt = stmt.join(PostTag).where(PostTag.tag_id == query.tag_id)
        
        # Apply sorting
        if query.sort_by == "title":
            order_col = Post.title
        elif query.sort_by == "created_at":
            order_col = Post.created_at
        elif query.sort_by == "published_at":
            order_col = Post.published_at
        elif query.sort_by == "status":
            order_col = Post.status
        else:
            order_col = Post.updated_at
        
        if query.sort_direction == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(asc(order_col))
        
        # Get total count
        total_stmt = select(func.count(Post.id)).where(Post.user_id == current_user.id)
        
        if query.search:
            total_stmt = total_stmt.where(
                or_(
                    Post.title.ilike(f"%{query.search}%"),
                    Post.body.ilike(f"%{query.search}%"),
                    Post.excerpt.ilike(f"%{query.search}%")
                )
            )
        
        if query.status:
            total_stmt = total_stmt.where(Post.status == query.status)
        
        if query.category_id:
            total_stmt = total_stmt.where(Post.category_id == query.category_id)
        
        if query.tag_id:
            total_stmt = total_stmt.join(PostTag).where(PostTag.tag_id == query.tag_id)
        
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (query.page - 1) * query.per_page
        stmt = stmt.offset(offset).limit(query.per_page)
        
        result = await self.db.execute(stmt)
        posts = result.scalars().all()
        
        # Build response
        post_responses = []
        for post in posts:
            post_responses.append(await self._build_post_response(post, current_user))
        
        return {
            "posts": post_responses,
            "total": total,
            "page": query.page,
            "per_page": query.per_page,
            "total_pages": (total + query.per_page - 1) // query.per_page
        }
    
    async def get_post(self, post_id: UUID, current_user: User) -> PostResponse:
        """Get a single post."""
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        return await self._build_post_response(post, current_user)
    
    async def submit_for_review(
        self, 
        post_id: UUID, 
        request: PostSubmitReviewRequest, 
        current_user: User
    ) -> PostResponse:
        """Submit post for review."""
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        if post.status != "draft":
            raise ValueError("Only draft posts can be submitted for review")
        
        # Update status
        post.status = "under_review"
        post.updated_at = datetime.utcnow()
        
        # Create workflow history entry
        await self._create_workflow_history(
            post_id, "draft", "under_review", current_user.id, request.message
        )
        
        await self.db.commit()
        await self.db.refresh(post)
        
        return await self._build_post_response(post, current_user)
    
    async def resubmit_post(
        self, 
        post_id: UUID, 
        request: PostResubmitRequest, 
        current_user: User
    ) -> PostResponse:
        """Resubmit post after rejection."""
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        if post.status != "rejected":
            raise ValueError("Only rejected posts can be resubmitted")
        
        # Update status
        post.status = "under_review"
        post.updated_at = datetime.utcnow()
        
        # Create workflow history entry
        await self._create_workflow_history(
            post_id, "rejected", "under_review", current_user.id, 
            f"Resubmitted: {request.message}. Changes made: {request.changes_made}"
        )
        
        await self.db.commit()
        await self.db.refresh(post)
        
        return await self._build_post_response(post, current_user)
    
    async def bulk_operation(
        self, 
        request: BulkPostRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Perform bulk operations on posts."""
        if request.action == "submit_review":
            return await self._bulk_submit_review(request.post_ids, current_user)
        elif request.action == "delete":
            return await self._bulk_delete(request.post_ids, current_user)
        elif request.action == "update_category":
            if not request.category_id:
                raise ValueError("Category ID required for category update")
            return await self._bulk_update_category(request.post_ids, request.category_id, current_user)
        elif request.action == "update_tags":
            if not request.tag_ids:
                raise ValueError("Tag IDs required for tag update")
            return await self._bulk_update_tags(request.post_ids, request.tag_ids, current_user)
        else:
            raise ValueError("Invalid bulk operation")
    
    async def auto_save(
        self, 
        post_id: UUID, 
        request: AutoSaveRequest, 
        current_user: User
    ) -> Dict[str, Any]:
        """Auto-save post content."""
        # Store auto-save data (simplified implementation)
        # In a real implementation, this would save to a separate auto_save table
        
        post = await self._get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found")
        
        # Update the post with auto-save data
        if "title" in request.content:
            post.title = request.content["title"]
        
        if "body" in request.content:
            post.body = request.content["body"]
        
        if "excerpt" in request.content:
            post.excerpt = request.content["excerpt"]
        
        post.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "message": "Auto-save successful",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_post_revisions(
        self, 
        post_id: UUID, 
        current_user: User
    ) -> List[PostRevisionResponse]:
        """Get post revision history."""
        # Simplified implementation - in real app, this would query post_revisions table
        return []
    
    async def get_workflow_history(
        self, 
        post_id: UUID, 
        current_user: User
    ) -> List[WorkflowHistoryResponse]:
        """Get post workflow history."""
        # Simplified implementation - in real app, this would query workflow_history table
        return []
    
    async def duplicate_post(
        self, 
        post_id: UUID, 
        current_user: User
    ) -> PostResponse:
        """Duplicate an existing post."""
        original_post = await self._get_post_by_id(post_id)
        if not original_post:
            raise ValueError("Post not found")
        
        # Create duplicate
        duplicate_slug = await self._ensure_unique_slug(f"{original_post.slug}-copy")
        
        duplicate_post = Post(
            title=f"{original_post.title} (Copy)",
            slug=duplicate_slug,
            body=original_post.body,
            excerpt=original_post.excerpt,
            featured_image_path=original_post.featured_image_path,
            category_id=original_post.category_id,
            status="draft",
            published_at=None,
            comments_enabled=original_post.comments_enabled,
            user_id=current_user.id,
            difficulty_level=original_post.difficulty_level,
            featured=False,
            feedback=None
        )
        
        self.db.add(duplicate_post)
        await self.db.commit()
        await self.db.refresh(duplicate_post)
        
        # Copy tags
        original_tags = await self._get_post_tags(post_id)
        if original_tags:
            await self._add_tags_to_post(duplicate_post.id, [tag.id for tag in original_tags])
        
        return await self._build_post_response(duplicate_post, current_user)
    
    # Private helper methods
    
    def _generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    async def _ensure_unique_slug(self, slug: str, exclude_id: Optional[UUID] = None) -> str:
        """Ensure slug is unique by appending numbers if necessary."""
        original_slug = slug
        counter = 1
        
        while True:
            stmt = select(Post).where(Post.slug == slug)
            if exclude_id:
                stmt = stmt.where(Post.id != exclude_id)
            
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none() is None:
                return slug
            
            slug = f"{original_slug}-{counter}"
            counter += 1
    
    async def _get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID with relationships."""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.author)
            )
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def _add_tags_to_post(self, post_id: UUID, tag_ids: List[UUID]) -> None:
        """Add tags to a post."""
        for tag_id in tag_ids:
            post_tag = PostTag(post_id=post_id, tag_id=tag_id)
            self.db.add(post_tag)
        
        await self.db.commit()
    
    async def _update_post_tags(self, post_id: UUID, tag_ids: List[UUID]) -> None:
        """Update post tags by replacing all existing tags."""
        # Remove existing tags
        await self.db.execute(
            delete(PostTag).where(PostTag.post_id == post_id)
        )
        
        # Add new tags
        if tag_ids:
            await self._add_tags_to_post(post_id, tag_ids)
    
    async def _get_post_tags(self, post_id: UUID) -> List[Tag]:
        """Get all tags for a post."""
        result = await self.db.execute(
            select(Tag)
            .join(PostTag)
            .where(PostTag.post_id == post_id)
        )
        return result.scalars().all()
    
    async def _remove_post_associations(self, post_id: UUID) -> None:
        """Remove all associations for a post."""
        # Remove tags
        await self.db.execute(
            delete(PostTag).where(PostTag.post_id == post_id)
        )
        
        # Remove views
        await self.db.execute(
            delete(View).where(View.post_id == post_id)
        )
        
        # Remove likes
        await self.db.execute(
            delete(Like).where(Like.post_id == post_id)
        )
        
        # Remove comments
        await self.db.execute(
            delete(Comment).where(Comment.post_id == post_id)
        )
        
        await self.db.commit()
    
    async def _create_revision(self, post: Post, user: User, changes_summary: str) -> None:
        """Create a post revision record."""
        # Simplified implementation - in real app, this would create a PostRevision record
        pass
    
    async def _create_workflow_history(
        self, 
        post_id: UUID, 
        from_status: str, 
        to_status: str, 
        user_id: UUID, 
        reason: Optional[str] = None
    ) -> None:
        """Create a workflow history record."""
        # Simplified implementation - in real app, this would create a WorkflowHistory record
        pass
    
    async def _get_post_view_count(self, post_id: UUID) -> int:
        """Get view count for a post."""
        result = await self.db.execute(
            select(func.count(View.id)).where(View.post_id == post_id)
        )
        return result.scalar() or 0
    
    async def _get_post_like_count(self, post_id: UUID) -> int:
        """Get like count for a post."""
        result = await self.db.execute(
            select(func.count(Like.id)).where(Like.post_id == post_id)
        )
        return result.scalar() or 0
    
    async def _get_post_comment_count(self, post_id: UUID) -> int:
        """Get comment count for a post."""
        result = await self.db.execute(
            select(func.count(Comment.id)).where(
                Comment.post_id == post_id,
                Comment.approved == True
            )
        )
        return result.scalar() or 0
    
    async def _build_post_response(self, post: Post, current_user: User) -> PostResponse:
        """Build post response with permissions and counts."""
        permissions = check_post_permissions(post, current_user)
        
        # Get counts
        view_count = await self._get_post_view_count(post.id)
        like_count = await self._get_post_like_count(post.id)
        comment_count = await self._get_post_comment_count(post.id)
        
        # Build author response
        author = AuthorResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar
        )
        
        # Build category response
        category = None
        if post.category:
            category = CategoryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            )
        
        # Build tag responses
        tags = []
        for tag in post.tags:
            tags.append(TagResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug
            ))
        
        return PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            body=post.body,
            excerpt=post.excerpt,
            featured_image_path=post.featured_image_path,
            status=post.status,
            category=category,
            tags=tags,
            author=author,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
            comments_enabled=post.comments_enabled,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            can_edit=permissions["can_edit"],
            can_delete=permissions["can_delete"],
            can_publish=permissions["can_publish"]
        )
    
    async def _bulk_submit_review(self, post_ids: List[UUID], current_user: User) -> Dict[str, Any]:
        """Bulk submit posts for review."""
        success_count = 0
        errors = []
        
        for post_id in post_ids:
            try:
                request = PostSubmitReviewRequest()
                await self.submit_for_review(post_id, request, current_user)
                success_count += 1
            except Exception as e:
                errors.append(f"Post {post_id}: {str(e)}")
        
        return {
            "success_count": success_count,
            "errors": errors
        }
    
    async def _bulk_delete(self, post_ids: List[UUID], current_user: User) -> Dict[str, Any]:
        """Bulk delete posts."""
        success_count = 0
        errors = []
        
        for post_id in post_ids:
            try:
                await self.delete_post(post_id, current_user)
                success_count += 1
            except Exception as e:
                errors.append(f"Post {post_id}: {str(e)}")
        
        return {
            "success_count": success_count,
            "errors": errors
        }
    
    async def _bulk_update_category(self, post_ids: List[UUID], category_id: UUID, current_user: User) -> Dict[str, Any]:
        """Bulk update post categories."""
        success_count = 0
        errors = []
        
        for post_id in post_ids:
            try:
                update_request = PostUpdateRequest(category_id=category_id)
                await self.update_post(post_id, update_request, current_user)
                success_count += 1
            except Exception as e:
                errors.append(f"Post {post_id}: {str(e)}")
        
        return {
            "success_count": success_count,
            "errors": errors
        }
    
    async def _bulk_update_tags(self, post_ids: List[UUID], tag_ids: List[UUID], current_user: User) -> Dict[str, Any]:
        """Bulk update post tags."""
        success_count = 0
        errors = []
        
        for post_id in post_ids:
            try:
                update_request = PostUpdateRequest(tags=tag_ids)
                await self.update_post(post_id, update_request, current_user)
                success_count += 1
            except Exception as e:
                errors.append(f"Post {post_id}: {str(e)}")
        
        return {
            "success_count": success_count,
            "errors": errors
        } 