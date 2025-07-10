"""
Web comment service for public-facing API endpoints.

Handles comment submission, threading, and moderation
for the public web interface.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comment import Comment
from models.post import Post
from models.user import User
from schemas.web.comments import (
    CommentCreateRequest, CommentResponse, CommentThreadResponse,
    CommentSubmissionResponse, CommentListRequest, CommentListResponse,
    CommentStatsResponse
)
from dependencies.pagination import PaginationParams, create_pagination_response


class WebCommentService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_comment(
        self,
        post_id: UUID,
        comment_data: CommentCreateRequest,
        user: User
    ) -> CommentSubmissionResponse:
        """
        Create a new comment on a post.
        
        Args:
            post_id: Post ID to comment on
            comment_data: Comment creation data
            user: User creating the comment
            
        Returns:
            CommentSubmissionResponse with result
        """
        # Verify post exists and allows comments
        post = await self._get_post_for_commenting(post_id)
        if not post:
            return CommentSubmissionResponse(
                success=False,
                message="Post not found or comments are disabled",
                redirect_url=f"/posts/{post_id}"
            )
        
        # Verify parent comment if replying
        parent_comment = None
        if comment_data.parent_id:
            parent_comment = await self._get_comment_by_id(comment_data.parent_id)
            if not parent_comment or parent_comment.post_id != post_id:
                return CommentSubmissionResponse(
                    success=False,
                    message="Invalid parent comment",
                    redirect_url=f"/posts/{post.slug}"
                )
        
        # Check comment depth limit (max 3 levels)
        if parent_comment:
            depth = await self._get_comment_depth(parent_comment)
            if depth >= 3:
                return CommentSubmissionResponse(
                    success=False,
                    message="Maximum comment depth reached",
                    redirect_url=f"/posts/{post.slug}"
                )
        
        # Create comment
        comment = Comment(
            user_id=user.id,
            post_id=post_id,
            parent_id=comment_data.parent_id,
            body=comment_data.body,
            status="approved"  # Auto-approve for now
        )
        
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        
        # Load relationships
        await self.db.refresh(comment, ['user'])
        
        # Convert to response
        comment_response = await self._convert_to_response(comment)
        
        return CommentSubmissionResponse(
            success=True,
            message="Comment posted successfully",
            comment=comment_response,
            redirect_url=f"/posts/{post.slug}#comment-{comment.id}",
            requires_moderation=False
        )
    
    async def get_post_comments(
        self,
        post_id: UUID,
        pagination: PaginationParams,
        user: Optional[User] = None
    ) -> CommentListResponse:
        """
        Get paginated comments for a post.
        
        Args:
            post_id: Post ID
            pagination: Pagination parameters
            user: Current user (optional)
            
        Returns:
            CommentListResponse with comments
        """
        # Get approved comments for the post
        query = select(Comment).where(
            and_(
                Comment.post_id == post_id,
                Comment.status == "approved"
            )
        ).options(
            selectinload(Comment.user)
        ).order_by(asc(Comment.created_at))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await self.db.execute(query)
        comments = result.scalars().all()
        
        # Build comment threads
        comment_threads = await self._build_comment_threads(comments, user)
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        return CommentListResponse(
            comments=comment_threads,
            total_count=total_count,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages=pagination_response.total_pages,
            has_next=pagination_response.has_next,
            has_prev=pagination_response.has_prev,
            post_id=post_id
        )
    
    async def update_comment(
        self,
        comment_id: UUID,
        comment_data: CommentCreateRequest,
        user: User
    ) -> CommentSubmissionResponse:
        """
        Update an existing comment.
        
        Args:
            comment_id: Comment ID to update
            comment_data: Updated comment data
            user: User updating the comment
            
        Returns:
            CommentSubmissionResponse with result
        """
        # Get comment
        comment = await self._get_comment_by_id(comment_id)
        if not comment:
            return CommentSubmissionResponse(
                success=False,
                message="Comment not found",
                redirect_url="/"
            )
        
        # Verify ownership or moderation rights
        if comment.user_id != user.id and user.role not in ["admin", "editor"]:
            return CommentSubmissionResponse(
                success=False,
                message="You can only edit your own comments",
                redirect_url=f"/posts/{comment.post.slug}"
            )
        
        # Update comment
        comment.body = comment_data.body
        comment.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(comment)
        
        # Convert to response
        comment_response = await self._convert_to_response(comment)
        
        return CommentSubmissionResponse(
            success=True,
            message="Comment updated successfully",
            comment=comment_response,
            redirect_url=f"/posts/{comment.post.slug}#comment-{comment.id}"
        )
    
    async def delete_comment(
        self,
        comment_id: UUID,
        user: User
    ) -> CommentSubmissionResponse:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID to delete
            user: User deleting the comment
            
        Returns:
            CommentSubmissionResponse with result
        """
        # Get comment
        comment = await self._get_comment_by_id(comment_id)
        if not comment:
            return CommentSubmissionResponse(
                success=False,
                message="Comment not found",
                redirect_url="/"
            )
        
        # Verify ownership or moderation rights
        if comment.user_id != user.id and user.role not in ["admin", "editor"]:
            return CommentSubmissionResponse(
                success=False,
                message="You can only delete your own comments",
                redirect_url=f"/posts/{comment.post.slug}"
            )
        
        # Delete comment (soft delete by changing status)
        comment.status = "deleted"
        comment.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return CommentSubmissionResponse(
            success=True,
            message="Comment deleted successfully",
            redirect_url=f"/posts/{comment.post.slug}"
        )
    
    async def get_comment_stats(
        self,
        post_id: UUID
    ) -> CommentStatsResponse:
        """
        Get comment statistics for a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            CommentStatsResponse with statistics
        """
        # Get total comments
        total_query = select(func.count(Comment.id)).where(Comment.post_id == post_id)
        total_comments = await self.db.scalar(total_query) or 0
        
        # Get approved comments
        approved_query = select(func.count(Comment.id)).where(
            and_(Comment.post_id == post_id, Comment.status == "approved")
        )
        approved_comments = await self.db.scalar(approved_query) or 0
        
        # Get pending comments
        pending_query = select(func.count(Comment.id)).where(
            and_(Comment.post_id == post_id, Comment.status == "pending")
        )
        pending_comments = await self.db.scalar(pending_query) or 0
        
        # Get rejected comments
        rejected_query = select(func.count(Comment.id)).where(
            and_(Comment.post_id == post_id, Comment.status == "rejected")
        )
        rejected_comments = await self.db.scalar(rejected_query) or 0
        
        # Get unique commenters
        unique_query = select(func.count(func.distinct(Comment.user_id))).where(
            Comment.post_id == post_id
        )
        unique_commenters = await self.db.scalar(unique_query) or 0
        
        # Calculate average comment length
        avg_length_query = select(func.avg(func.length(Comment.body))).where(
            Comment.post_id == post_id
        )
        avg_length = await self.db.scalar(avg_length_query) or 0.0
        
        # Get recent activity
        recent_query = select(Comment).where(
            Comment.post_id == post_id
        ).options(
            selectinload(Comment.user)
        ).order_by(desc(Comment.created_at)).limit(5)
        
        result = await self.db.execute(recent_query)
        recent_comments = result.scalars().all()
        
        recent_activity = []
        for comment in recent_comments:
            comment_response = await self._convert_to_response(comment)
            recent_activity.append(comment_response)
        
        return CommentStatsResponse(
            total_comments=total_comments,
            approved_comments=approved_comments,
            pending_comments=pending_comments,
            rejected_comments=rejected_comments,
            unique_commenters=unique_commenters,
            average_comment_length=float(avg_length),
            recent_activity=recent_activity
        )
    
    async def _get_post_for_commenting(self, post_id: UUID) -> Optional[Post]:
        """Get post and verify it allows comments."""
        query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.isnot(None),
                Post.comments_enabled == True
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_comment_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Get comment by ID with relationships."""
        query = select(Comment).where(Comment.id == comment_id).options(
            selectinload(Comment.user),
            selectinload(Comment.post)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_comment_depth(self, comment: Comment) -> int:
        """Get the depth of a comment in the thread."""
        depth = 0
        current = comment
        
        while current.parent_id:
            depth += 1
            parent_query = select(Comment).where(Comment.id == current.parent_id)
            result = await self.db.execute(parent_query)
            current = result.scalar_one_or_none()
            
            if not current:
                break
        
        return depth
    
    async def _build_comment_threads(
        self,
        comments: List[Comment],
        user: Optional[User] = None
    ) -> List[CommentThreadResponse]:
        """Build threaded comment structure."""
        # Create a map of comments by ID
        comment_map = {comment.id: comment for comment in comments}
        
        # Build thread structure
        root_comments = []
        
        for comment in comments:
            if comment.parent_id is None:
                # Root comment
                thread_response = await self._convert_to_thread_response(comment, user)
                await self._add_replies_to_thread(thread_response, comment_map, user)
                root_comments.append(thread_response)
        
        return root_comments
    
    async def _add_replies_to_thread(
        self,
        thread_response: CommentThreadResponse,
        comment_map: Dict[UUID, Comment],
        user: Optional[User] = None
    ):
        """Recursively add replies to a comment thread."""
        replies = []
        
        for comment in comment_map.values():
            if comment.parent_id == thread_response.id:
                reply_response = await self._convert_to_thread_response(comment, user)
                await self._add_replies_to_thread(reply_response, comment_map, user)
                replies.append(reply_response)
        
        thread_response.replies = replies
        thread_response.replies_count = len(replies)
    
    async def _convert_to_response(self, comment: Comment) -> CommentResponse:
        """Convert comment model to response."""
        from schemas.user import UserSummaryResponse
        
        user_response = UserSummaryResponse(
            id=comment.user.id,
            name=comment.user.name,
            avatar=comment.user.avatar,
            role=comment.user.role
        )
        
        return CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            body=comment.body,
            status=comment.status,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user=user_response,
            replies_count=0,  # Will be calculated separately
            can_edit=False,   # Will be set based on user permissions
            can_delete=False  # Will be set based on user permissions
        )
    
    async def _convert_to_thread_response(
        self,
        comment: Comment,
        user: Optional[User] = None
    ) -> CommentThreadResponse:
        """Convert comment model to thread response."""
        from schemas.user import UserSummaryResponse
        
        user_response = UserSummaryResponse(
            id=comment.user.id,
            name=comment.user.name,
            avatar=comment.user.avatar,
            role=comment.user.role
        )
        
        # Determine user permissions
        can_edit = user and (user.id == comment.user_id or user.role in ["admin", "editor"])
        can_delete = user and (user.id == comment.user_id or user.role in ["admin", "editor"])
        can_reply = user and user.role != "banned"
        
        return CommentThreadResponse(
            id=comment.id,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            body=comment.body,
            status=comment.status,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user=user_response,
            replies=[],  # Will be populated by _add_replies_to_thread
            replies_count=0,  # Will be calculated by _add_replies_to_thread
            depth=0,  # Will be calculated if needed
            can_reply=can_reply,
            can_edit=can_edit,
            can_delete=can_delete
        ) 