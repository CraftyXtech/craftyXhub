"""
Web interaction service for public-facing API endpoints.

Handles user interactions with posts (likes, bookmarks, views)
for the public web interface.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.post import Post
from models.user import User
from models.interactions import Like, Bookmark, View
from schemas.web.interactions import (
    InteractionResponse, InteractionCountsResponse, InteractionStatusResponse,
    BulkInteractionRequest, BulkInteractionResponse, UserInteractionHistoryRequest,
    UserInteractionHistoryResponse, InteractionAnalyticsRequest,
    InteractionAnalyticsResponse, PostInteractionSummaryResponse
)
from dependencies.pagination import PaginationParams, create_pagination_response


class WebInteractionService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def toggle_like(
        self,
        post_id: UUID,
        user: User
    ) -> InteractionResponse:
        """
        Toggle like status for a post.
        
        Args:
            post_id: Post ID to like/unlike
            user: User performing the action
            
        Returns:
            InteractionResponse with result
        """
        # Verify post exists
        post = await self._get_post_by_id(post_id)
        if not post:
            return InteractionResponse(
                success=False,
                action="error",
                message="Post not found",
                post_id=post_id,
                user_id=user.id,
                interaction_counts=InteractionCountsResponse(),
                timestamp=datetime.utcnow()
            )
        
        # Check if user has already liked the post
        existing_like = await self._get_user_like(post_id, user.id)
        
        if existing_like:
            # Unlike the post
            await self.db.delete(existing_like)
            action = "unliked"
            message = "Post unliked successfully"
        else:
            # Like the post
            like = Like(
                user_id=user.id,
                post_id=post_id,
                created_at=datetime.utcnow()
            )
            self.db.add(like)
            action = "liked"
            message = "Post liked successfully"
        
        await self.db.commit()
        
        # Get updated interaction counts
        interaction_counts = await self._get_interaction_counts(post_id)
        
        return InteractionResponse(
            success=True,
            action=action,
            message=message,
            post_id=post_id,
            user_id=user.id,
            interaction_counts=interaction_counts,
            redirect_url=f"/posts/{post.slug}",
            timestamp=datetime.utcnow()
        )
    
    async def toggle_bookmark(
        self,
        post_id: UUID,
        user: User
    ) -> InteractionResponse:
        """
        Toggle bookmark status for a post.
        
        Args:
            post_id: Post ID to bookmark/unbookmark
            user: User performing the action
            
        Returns:
            InteractionResponse with result
        """
        # Verify post exists
        post = await self._get_post_by_id(post_id)
        if not post:
            return InteractionResponse(
                success=False,
                action="error",
                message="Post not found",
                post_id=post_id,
                user_id=user.id,
                interaction_counts=InteractionCountsResponse(),
                timestamp=datetime.utcnow()
            )
        
        # Check if user has already bookmarked the post
        existing_bookmark = await self._get_user_bookmark(post_id, user.id)
        
        if existing_bookmark:
            # Remove bookmark
            await self.db.delete(existing_bookmark)
            action = "unbookmarked"
            message = "Post removed from bookmarks"
        else:
            # Add bookmark
            bookmark = Bookmark(
                user_id=user.id,
                post_id=post_id,
                created_at=datetime.utcnow()
            )
            self.db.add(bookmark)
            action = "bookmarked"
            message = "Post bookmarked successfully"
        
        await self.db.commit()
        
        # Get updated interaction counts
        interaction_counts = await self._get_interaction_counts(post_id)
        
        return InteractionResponse(
            success=True,
            action=action,
            message=message,
            post_id=post_id,
            user_id=user.id,
            interaction_counts=interaction_counts,
            redirect_url=f"/posts/{post.slug}",
            timestamp=datetime.utcnow()
        )
    
    async def record_view(
        self,
        post_id: UUID,
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> InteractionResponse:
        """
        Record a view for a post.
        
        Args:
            post_id: Post ID being viewed
            user: User viewing the post (optional)
            ip_address: IP address of viewer
            user_agent: User agent string
            
        Returns:
            InteractionResponse with result
        """
        # Verify post exists
        post = await self._get_post_by_id(post_id)
        if not post:
            return InteractionResponse(
                success=False,
                action="error",
                message="Post not found",
                post_id=post_id,
                user_id=user.id if user else None,
                interaction_counts=InteractionCountsResponse(),
                timestamp=datetime.utcnow()
            )
        
        # Check for duplicate view (same user/IP in last hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        existing_view_query = select(View).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time
            )
        )
        
        if user:
            existing_view_query = existing_view_query.where(View.user_id == user.id)
        elif ip_address:
            existing_view_query = existing_view_query.where(View.ip_address == ip_address)
        
        existing_view = await self.db.scalar(existing_view_query)
        
        if not existing_view:
            # Record new view
            view = View(
                user_id=user.id if user else None,
                post_id=post_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.utcnow()
            )
            self.db.add(view)
            await self.db.commit()
        
        # Get updated interaction counts
        interaction_counts = await self._get_interaction_counts(post_id)
        
        return InteractionResponse(
            success=True,
            action="viewed",
            message="View recorded",
            post_id=post_id,
            user_id=user.id if user else None,
            interaction_counts=interaction_counts,
            timestamp=datetime.utcnow()
        )
    
    async def get_interaction_status(
        self,
        post_id: UUID,
        user: Optional[User] = None
    ) -> InteractionStatusResponse:
        """
        Get user's interaction status with a post.
        
        Args:
            post_id: Post ID
            user: User to check status for
            
        Returns:
            InteractionStatusResponse with status
        """
        # Get interaction counts
        interaction_counts = await self._get_interaction_counts(post_id)
        
        # Default status for anonymous users
        if not user:
            return InteractionStatusResponse(
                post_id=post_id,
                user_id=None,
                user_has_liked=False,
                user_has_bookmarked=False,
                user_has_commented=False,
                user_has_viewed=False,
                can_like=False,
                can_bookmark=False,
                can_comment=False,
                interaction_counts=interaction_counts
            )
        
        # Check user's interactions
        has_liked = await self._get_user_like(post_id, user.id) is not None
        has_bookmarked = await self._get_user_bookmark(post_id, user.id) is not None
        has_commented = await self._user_has_commented(post_id, user.id)
        has_viewed = await self._user_has_viewed(post_id, user.id)
        
        # Check permissions
        can_interact = user.role != "banned"
        
        return InteractionStatusResponse(
            post_id=post_id,
            user_id=user.id,
            user_has_liked=has_liked,
            user_has_bookmarked=has_bookmarked,
            user_has_commented=has_commented,
            user_has_viewed=has_viewed,
            can_like=can_interact,
            can_bookmark=can_interact,
            can_comment=can_interact,
            interaction_counts=interaction_counts,
            last_interaction=await self._get_last_interaction_time(post_id, user.id)
        )
    
    async def bulk_interaction(
        self,
        request: BulkInteractionRequest,
        user: User
    ) -> BulkInteractionResponse:
        """
        Perform bulk interaction operations.
        
        Args:
            request: Bulk interaction request
            user: User performing the actions
            
        Returns:
            BulkInteractionResponse with results
        """
        results = []
        errors = []
        processed_count = 0
        failed_count = 0
        
        for post_id in request.post_ids:
            try:
                if request.action == "like":
                    result = await self.toggle_like(post_id, user)
                elif request.action == "unlike":
                    result = await self.toggle_like(post_id, user)
                elif request.action == "bookmark":
                    result = await self.toggle_bookmark(post_id, user)
                elif request.action == "unbookmark":
                    result = await self.toggle_bookmark(post_id, user)
                else:
                    raise ValueError(f"Invalid action: {request.action}")
                
                results.append(result)
                if result.success:
                    processed_count += 1
                else:
                    failed_count += 1
                    errors.append({
                        "post_id": str(post_id),
                        "error": result.message
                    })
                    
            except Exception as e:
                failed_count += 1
                errors.append({
                    "post_id": str(post_id),
                    "error": str(e)
                })
        
        success = failed_count == 0
        message = f"Processed {processed_count} posts"
        if failed_count > 0:
            message += f", {failed_count} failed"
        
        return BulkInteractionResponse(
            success=success,
            message=message,
            processed_count=processed_count,
            failed_count=failed_count,
            results=results,
            errors=errors
        )
    
    async def get_user_interaction_history(
        self,
        user: User,
        request: UserInteractionHistoryRequest,
        pagination: PaginationParams
    ) -> UserInteractionHistoryResponse:
        """
        Get user's interaction history.
        
        Args:
            user: User to get history for
            request: History request parameters
            pagination: Pagination parameters
            
        Returns:
            UserInteractionHistoryResponse with history
        """
        interactions = []
        
        # Get likes
        if not request.interaction_type or request.interaction_type == "like":
            likes_query = select(Like).where(Like.user_id == user.id).options(
                selectinload(Like.post)
            )
            
            if request.start_date:
                likes_query = likes_query.where(Like.created_at >= request.start_date)
            if request.end_date:
                likes_query = likes_query.where(Like.created_at <= request.end_date)
            
            likes_result = await self.db.execute(likes_query)
            likes = likes_result.scalars().all()
            
            for like in likes:
                interactions.append({
                    "id": str(like.id),
                    "type": "like",
                    "post_id": str(like.post_id),
                    "post_title": like.post.title,
                    "post_slug": like.post.slug,
                    "created_at": like.created_at.isoformat(),
                    "metadata": {}
                })
        
        # Get bookmarks
        if not request.interaction_type or request.interaction_type == "bookmark":
            bookmarks_query = select(Bookmark).where(Bookmark.user_id == user.id).options(
                selectinload(Bookmark.post)
            )
            
            if request.start_date:
                bookmarks_query = bookmarks_query.where(Bookmark.created_at >= request.start_date)
            if request.end_date:
                bookmarks_query = bookmarks_query.where(Bookmark.created_at <= request.end_date)
            
            bookmarks_result = await self.db.execute(bookmarks_query)
            bookmarks = bookmarks_result.scalars().all()
            
            for bookmark in bookmarks:
                interactions.append({
                    "id": str(bookmark.id),
                    "type": "bookmark",
                    "post_id": str(bookmark.post_id),
                    "post_title": bookmark.post.title,
                    "post_slug": bookmark.post.slug,
                    "created_at": bookmark.created_at.isoformat(),
                    "metadata": {}
                })
        
        # Sort by created_at descending
        interactions.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total_count = len(interactions)
        start_idx = pagination.offset
        end_idx = start_idx + pagination.limit
        paginated_interactions = interactions[start_idx:end_idx]
        
        # Calculate summary
        summary = {}
        for interaction in interactions:
            interaction_type = interaction["type"]
            summary[interaction_type] = summary.get(interaction_type, 0) + 1
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        return UserInteractionHistoryResponse(
            interactions=paginated_interactions,
            total_count=total_count,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages=pagination_response.total_pages,
            has_next=pagination_response.has_next,
            has_prev=pagination_response.has_prev,
            summary=summary
        )
    
    async def _get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        """Get post by ID."""
        query = select(Post).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_user_like(self, post_id: UUID, user_id: UUID) -> Optional[Like]:
        """Get user's like for a post."""
        query = select(Like).where(
            and_(Like.post_id == post_id, Like.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_user_bookmark(self, post_id: UUID, user_id: UUID) -> Optional[Bookmark]:
        """Get user's bookmark for a post."""
        query = select(Bookmark).where(
            and_(Bookmark.post_id == post_id, Bookmark.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_interaction_counts(self, post_id: UUID) -> InteractionCountsResponse:
        """Get interaction counts for a post."""
        # Get likes count
        likes_query = select(func.count(Like.id)).where(Like.post_id == post_id)
        likes_count = await self.db.scalar(likes_query) or 0
        
        # Get bookmarks count
        bookmarks_query = select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        bookmarks_count = await self.db.scalar(bookmarks_query) or 0
        
        # Get views count
        views_query = select(func.count(View.id)).where(View.post_id == post_id)
        views_count = await self.db.scalar(views_query) or 0
        
        # Get comments count
        from models.comment import Comment
        comments_query = select(func.count(Comment.id)).where(Comment.post_id == post_id)
        comments_count = await self.db.scalar(comments_query) or 0
        
        return InteractionCountsResponse(
            likes_count=likes_count,
            bookmarks_count=bookmarks_count,
            comments_count=comments_count,
            views_count=views_count,
            shares_count=0  # TODO: Implement shares
        )
    
    async def _user_has_commented(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if user has commented on a post."""
        from models.comment import Comment
        query = select(Comment.id).where(
            and_(Comment.post_id == post_id, Comment.user_id == user_id)
        )
        result = await self.db.scalar(query)
        return result is not None
    
    async def _user_has_viewed(self, post_id: UUID, user_id: UUID) -> bool:
        """Check if user has viewed a post."""
        query = select(View.id).where(
            and_(View.post_id == post_id, View.user_id == user_id)
        )
        result = await self.db.scalar(query)
        return result is not None
    
    async def _get_last_interaction_time(self, post_id: UUID, user_id: UUID) -> Optional[datetime]:
        """Get the time of user's last interaction with a post."""
        # Get latest like
        like_query = select(Like.created_at).where(
            and_(Like.post_id == post_id, Like.user_id == user_id)
        ).order_by(desc(Like.created_at))
        
        # Get latest bookmark
        bookmark_query = select(Bookmark.created_at).where(
            and_(Bookmark.post_id == post_id, Bookmark.user_id == user_id)
        ).order_by(desc(Bookmark.created_at))
        
        # Get latest view
        view_query = select(View.created_at).where(
            and_(View.post_id == post_id, View.user_id == user_id)
        ).order_by(desc(View.created_at))
        
        # Get latest comment
        from models.comment import Comment
        comment_query = select(Comment.created_at).where(
            and_(Comment.post_id == post_id, Comment.user_id == user_id)
        ).order_by(desc(Comment.created_at))
        
        # Execute all queries
        like_time = await self.db.scalar(like_query)
        bookmark_time = await self.db.scalar(bookmark_query)
        view_time = await self.db.scalar(view_query)
        comment_time = await self.db.scalar(comment_query)
        
        # Find the latest time
        times = [t for t in [like_time, bookmark_time, view_time, comment_time] if t is not None]
        return max(times) if times else None 