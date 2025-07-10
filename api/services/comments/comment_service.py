
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, update, delete
from sqlalchemy.orm import selectinload

from models.comment import Comment
from models.post import Post
from models.user import User
from schemas.comment import (
    CommentListQuery,
    CommentCreateRequest,
    CommentUpdateRequest,
    GuestCommentRequest,
    CommentResponse,
    CommentListResponse,
    CommentStatsResponse,
    CommentUserResponse,
    PaginationMeta
)


class CommentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_post_comments(
        self,
        post_id: UUID,
        query: CommentListQuery,
        current_user: Optional[User] = None
    ) -> CommentListResponse:
        """
        Get paginated comments for a post with hierarchical threading.
        
        Args:
            post_id: UUID of the post
            query: Query parameters for pagination and filtering
            current_user: Optional authenticated user
            
        Returns:
            CommentListResponse with paginated comments and stats
        """
        # Verify post exists and is published
        post_query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.is_not(None)
            )
        )
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise ValueError("Post not found or not published")

        # Build base query for approved comments
        base_query = select(Comment).where(
            and_(
                Comment.post_id == post_id,
                Comment.approved == True,
                Comment.deleted_at.is_(None)
            )
        )

        # Apply sorting
        if query.sort_by == "newest":
            base_query = base_query.order_by(desc(Comment.created_at))
        elif query.sort_by == "oldest":
            base_query = base_query.order_by(asc(Comment.created_at))
        elif query.sort_by == "most_liked":
            # This would need a likes table for comments - simplified for now
            base_query = base_query.order_by(desc(Comment.created_at))
        else:
            base_query = base_query.order_by(desc(Comment.created_at))

        # Get top-level comments (no parent) for pagination
        top_level_query = base_query.where(Comment.parent_id.is_(None))

        # Get total count for pagination
        count_query = select(func.count()).select_from(top_level_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination to top-level comments
        offset = (query.page - 1) * query.per_page
        paginated_query = top_level_query.options(
            selectinload(Comment.user),
            selectinload(Comment.post)
        ).offset(offset).limit(query.per_page)

        # Execute query
        result = await self.db.execute(paginated_query)
        top_level_comments = result.scalars().all()

        # Build comment tree with replies if requested
        comment_responses = []
        for comment in top_level_comments:
            comment_response = await self._build_comment_tree(
                comment,
                current_user,
                query.max_depth if query.include_replies else 0
            )
            comment_responses.append(comment_response)

        # Get comment statistics
        stats = await self._get_comment_stats(post_id)

        # Create pagination metadata
        pagination = PaginationMeta(
            page=query.page,
            per_page=query.per_page,
            total=total,
            total_pages=(total + query.per_page - 1) // query.per_page,
            has_next=query.page * query.per_page < total,
            has_prev=query.page > 1
        )

        return CommentListResponse(
            comments=comment_responses,
            pagination=pagination,
            stats=stats,
            post_id=post_id
        )

    async def create_comment(
        self,
        post_id: UUID,
        comment_data: CommentCreateRequest,
        current_user: User
    ) -> CommentResponse:
        """
        Create a new comment on a post.
        
        Args:
            post_id: UUID of the post
            comment_data: Comment creation data
            current_user: Authenticated user creating the comment
            
        Returns:
            CommentResponse with created comment data
        """
        # Verify post exists, is published, and has comments enabled
        post_query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.is_not(None),
                Post.comments_enabled == True
            )
        )
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise ValueError("Post not found, not published, or comments disabled")

        # Verify parent comment exists if provided
        if comment_data.parent_id:
            parent_query = select(Comment).where(
                and_(
                    Comment.id == comment_data.parent_id,
                    Comment.post_id == post_id,
                    Comment.approved == True,
                    Comment.deleted_at.is_(None)
                )
            )
            parent_result = await self.db.execute(parent_query)
            parent_comment = parent_result.scalar_one_or_none()

            if not parent_comment:
                raise ValueError("Parent comment not found")

        # Create new comment
        new_comment = Comment(
            id=uuid4(),
            post_id=post_id,
            user_id=current_user.id,
            parent_id=comment_data.parent_id,
            body=comment_data.body,
            approved=self._should_auto_approve(current_user),
            is_guest=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)

        # Load relationships for response
        comment_with_relations = await self._load_comment_relations(new_comment.id)
        
        return await self._build_comment_response(comment_with_relations, current_user)

    async def create_guest_comment(
        self,
        post_id: UUID,
        comment_data: GuestCommentRequest
    ) -> CommentResponse:
        """
        Create a new guest comment on a post.
        
        Args:
            post_id: UUID of the post
            comment_data: Guest comment creation data
            
        Returns:
            CommentResponse with created comment data
        """
        # Verify post exists, is published, and has comments enabled
        post_query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.is_not(None),
                Post.comments_enabled == True
            )
        )
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()

        if not post:
            raise ValueError("Post not found, not published, or comments disabled")

        # Create new guest comment (requires moderation)
        new_comment = Comment(
            id=uuid4(),
            post_id=post_id,
            user_id=None,
            parent_id=comment_data.parent_id,
            body=comment_data.body,
            approved=False,  # Guest comments require moderation
            is_guest=True,
            guest_name=comment_data.guest_name,
            guest_email=comment_data.guest_email,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)

        return await self._build_comment_response(new_comment, None)

    async def update_comment(
        self,
        comment_id: UUID,
        comment_data: CommentUpdateRequest,
        current_user: User
    ) -> CommentResponse:
        """
        Update an existing comment.
        
        Args:
            comment_id: UUID of the comment to update
            comment_data: Updated comment data
            current_user: User attempting to update the comment
            
        Returns:
            CommentResponse with updated comment data
        """
        # Get comment with ownership check
        comment_query = select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            )
        )
        comment_result = await self.db.execute(comment_query)
        comment = comment_result.scalar_one_or_none()

        if not comment:
            raise ValueError("Comment not found")

        # Check permissions (author or admin)
        if comment.user_id != current_user.id and not current_user.is_admin():
            raise ValueError("You can only edit your own comments")

        # Update comment
        comment.body = comment_data.body
        comment.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(comment)

        # Load relationships for response
        comment_with_relations = await self._load_comment_relations(comment.id)
        
        return await self._build_comment_response(comment_with_relations, current_user)

    async def delete_comment(
        self,
        comment_id: UUID,
        current_user: User
    ) -> bool:
        """
        Delete a comment (soft delete to maintain thread integrity).
        
        Args:
            comment_id: UUID of the comment to delete
            current_user: User attempting to delete the comment
            
        Returns:
            True if comment was deleted successfully
        """
        # Get comment with ownership check
        comment_query = select(Comment).where(
            and_(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None)
            )
        )
        comment_result = await self.db.execute(comment_query)
        comment = comment_result.scalar_one_or_none()

        if not comment:
            raise ValueError("Comment not found")

        # Check permissions (author, admin, or post author)
        post_query = select(Post).where(Post.id == comment.post_id)
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()

        can_delete = (
            comment.user_id == current_user.id or  # Comment author
            current_user.is_admin() or  # Admin
            (post and post.user_id == current_user.id)  # Post author
        )

        if not can_delete:
            raise ValueError("You don't have permission to delete this comment")

        # Soft delete the comment
        comment.deleted_at = datetime.utcnow()
        comment.body = "[Comment deleted]"
        
        await self.db.commit()
        return True

    async def _build_comment_tree(
        self,
        comment: Comment,
        current_user: Optional[User],
        max_depth: int,
        current_depth: int = 0
    ) -> CommentResponse:
        """
        Build a hierarchical comment tree with replies.
        
        Args:
            comment: Root comment
            current_user: Optional authenticated user
            max_depth: Maximum depth to load replies
            current_depth: Current depth in the tree
            
        Returns:
            CommentResponse with nested replies
        """
        # Build base response
        comment_response = await self._build_comment_response(comment, current_user)
        comment_response.depth = current_depth

        # Load replies if within depth limit
        if current_depth < max_depth:
            replies_query = select(Comment).where(
                and_(
                    Comment.parent_id == comment.id,
                    Comment.approved == True,
                    Comment.deleted_at.is_(None)
                )
            ).options(
                selectinload(Comment.user)
            ).order_by(asc(Comment.created_at))

            replies_result = await self.db.execute(replies_query)
            replies = replies_result.scalars().all()

            # Recursively build reply tree
            reply_responses = []
            for reply in replies:
                reply_response = await self._build_comment_tree(
                    reply,
                    current_user,
                    max_depth,
                    current_depth + 1
                )
                reply_responses.append(reply_response)

            comment_response.replies = reply_responses
            comment_response.reply_count = len(reply_responses)

        return comment_response

    async def _build_comment_response(
        self,
        comment: Comment,
        current_user: Optional[User]
    ) -> CommentResponse:
        """
        Build a CommentResponse from a Comment model.
        
        Args:
            comment: Comment model instance
            current_user: Optional authenticated user
            
        Returns:
            CommentResponse with user permissions
        """
        # Build user response if not guest
        user_response = None
        if comment.user:
            user_response = CommentUserResponse(
                id=comment.user.id,
                name=comment.user.name,
                avatar=comment.user.avatar,
                role=comment.user.role
            )

        # Determine user permissions
        can_edit = False
        can_delete = False
        if current_user:
            can_edit = comment.user_id == current_user.id
            can_delete = (
                comment.user_id == current_user.id or
                current_user.is_admin()
            )

        return CommentResponse(
            id=comment.id,
            body=comment.body,
            user=user_response,
            guest_name=comment.guest_name,
            guest_email=comment.guest_email if comment.is_guest else None,
            parent_id=comment.parent_id,
            replies=[],  # Will be populated by _build_comment_tree
            reply_count=0,  # Will be calculated by _build_comment_tree
            like_count=0,  # TODO: Implement comment likes
            is_liked=None,  # TODO: Implement comment likes
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_approved=comment.approved,
            is_guest=comment.is_guest,
            can_edit=can_edit,
            can_delete=can_delete,
            can_reply=True,  # TODO: Implement reply restrictions
            depth=0,  # Will be set by _build_comment_tree
            is_deleted=comment.deleted_at is not None
        )

    async def _load_comment_relations(self, comment_id: UUID) -> Comment:
        """
        Load a comment with its relationships.
        
        Args:
            comment_id: UUID of the comment
            
        Returns:
            Comment with loaded relationships
        """
        query = select(Comment).where(Comment.id == comment_id).options(
            selectinload(Comment.user)
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def _get_comment_stats(self, post_id: UUID) -> CommentStatsResponse:
        """
        Get comment statistics for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            CommentStatsResponse with statistics
        """
        # Total comments
        total_query = select(func.count(Comment.id)).where(
            and_(
                Comment.post_id == post_id,
                Comment.deleted_at.is_(None)
            )
        )
        total_result = await self.db.execute(total_query)
        total_comments = total_result.scalar() or 0

        # Approved comments
        approved_query = select(func.count(Comment.id)).where(
            and_(
                Comment.post_id == post_id,
                Comment.approved == True,
                Comment.deleted_at.is_(None)
            )
        )
        approved_result = await self.db.execute(approved_query)
        approved_comments = approved_result.scalar() or 0

        # Pending comments
        pending_query = select(func.count(Comment.id)).where(
            and_(
                Comment.post_id == post_id,
                Comment.approved == False,
                Comment.deleted_at.is_(None)
            )
        )
        pending_result = await self.db.execute(pending_query)
        pending_comments = pending_result.scalar() or 0

        # Reply count (comments with parent_id)
        reply_query = select(func.count(Comment.id)).where(
            and_(
                Comment.post_id == post_id,
                Comment.parent_id.is_not(None),
                Comment.approved == True,
                Comment.deleted_at.is_(None)
            )
        )
        reply_result = await self.db.execute(reply_query)
        reply_count = reply_result.scalar() or 0

        # Guest vs user comments
        guest_query = select(func.count(Comment.id)).where(
            and_(
                Comment.post_id == post_id,
                Comment.is_guest == True,
                Comment.deleted_at.is_(None)
            )
        )
        guest_result = await self.db.execute(guest_query)
        guest_comments = guest_result.scalar() or 0

        user_comments = total_comments - guest_comments

        return CommentStatsResponse(
            total_comments=total_comments,
            approved_comments=approved_comments,
            pending_comments=pending_comments,
            rejected_comments=0,  # TODO: Implement rejection tracking
            reply_count=reply_count,
            guest_comments=guest_comments,
            user_comments=user_comments
        )

    def _should_auto_approve(self, user: User) -> bool:
        """
        Determine if a user's comment should be auto-approved.
        
        Args:
            user: User creating the comment
            
        Returns:
            True if comment should be auto-approved
        """
        # Auto-approve for admins and editors
        if user.is_admin() or user.is_editor():
            return True

        # TODO: Implement trust scoring or other auto-approval logic
        # For now, auto-approve all registered users
        return True 