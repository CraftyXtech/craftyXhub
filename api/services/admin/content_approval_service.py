from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, desc, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Post, Comment, Category, Tag
from models.audit import ContentApproval
from core.logging import get_logger

logger = get_logger(__name__)
from .audit_service import AuditService


class ContentApprovalService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)

    async def get_pending_content(
        self,
        content_type: str = "post",
        page: int = 1,
        per_page: int = 10,
        author_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get content pending approval with pagination."""
        try:
            if content_type == "post":
                return await self._get_pending_posts(page, per_page, author_id, category_id, search)
            elif content_type == "comment":
                return await self._get_pending_comments(page, per_page, search)
            else:
                return [], 0
                
        except Exception as e:
            logger.error(f"Failed to get pending content: {str(e)}")
            return [], 0

    async def approve_post(
        self,
        admin_id: UUID,
        post_id: UUID,
        feedback: Optional[str] = None,
        notify_author: bool = True
    ) -> Dict[str, Any]:
        """Approve a post for publication."""
        try:
            # Get the post
            post_result = await self.db.execute(
                select(Post).options(selectinload(Post.author))
                .where(Post.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                return {'success': False, 'message': 'Post not found'}
            
            if post.status != 'under_review':
                return {'success': False, 'message': 'Post is not pending approval'}
            
            # Update post status
            post.status = 'published'
            post.published_at = datetime.utcnow()
            post.feedback = feedback
            post.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Log the approval
            await self.audit_service.log_content_approval(
                admin_id=admin_id,
                content_id=post_id,
                content_type='post',
                action='approved',
                feedback=feedback
            )
            
            # TODO: Send notification to author if notify_author is True
            
            logger.info(f"Post {post_id} approved by admin {admin_id}")
            
            return {
                'success': True,
                'message': 'Post approved successfully',
                'content_id': post_id,
                'content_type': 'post',
                'new_status': 'published',
                'feedback': feedback,
                'updated_at': post.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to approve post: {str(e)}")
            await self.db.rollback()
            return {'success': False, 'message': 'Failed to approve post'}

    async def reject_post(
        self,
        admin_id: UUID,
        post_id: UUID,
        feedback: str,
        notify_author: bool = True
    ) -> Dict[str, Any]:
        """Reject a post with mandatory feedback."""
        try:
            if not feedback or len(feedback.strip()) < 10:
                return {'success': False, 'message': 'Feedback is required for rejection (minimum 10 characters)'}
            
            # Get the post
            post_result = await self.db.execute(
                select(Post).options(selectinload(Post.author))
                .where(Post.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                return {'success': False, 'message': 'Post not found'}
            
            if post.status != 'under_review':
                return {'success': False, 'message': 'Post is not pending approval'}
            
            # Update post status
            post.status = 'rejected'
            post.feedback = feedback
            post.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Log the rejection
            await self.audit_service.log_content_approval(
                admin_id=admin_id,
                content_id=post_id,
                content_type='post',
                action='rejected',
                feedback=feedback
            )
            
            # TODO: Send notification to author if notify_author is True
            
            logger.info(f"Post {post_id} rejected by admin {admin_id}")
            
            return {
                'success': True,
                'message': 'Post rejected successfully',
                'content_id': post_id,
                'content_type': 'post',
                'new_status': 'rejected',
                'feedback': feedback,
                'updated_at': post.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to reject post: {str(e)}")
            await self.db.rollback()
            return {'success': False, 'message': 'Failed to reject post'}

    async def approve_comment(
        self,
        admin_id: UUID,
        comment_id: UUID,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve a comment."""
        try:
            # Get the comment
            comment_result = await self.db.execute(
                select(Comment).options(selectinload(Comment.author))
                .where(Comment.id == comment_id)
            )
            comment = comment_result.scalar_one_or_none()
            
            if not comment:
                return {'success': False, 'message': 'Comment not found'}
            
            if comment.status != 'pending':
                return {'success': False, 'message': 'Comment is not pending approval'}
            
            # Update comment status
            comment.status = 'approved'
            comment.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Log the approval
            await self.audit_service.log_content_approval(
                admin_id=admin_id,
                content_id=comment_id,
                content_type='comment',
                action='approved',
                feedback=feedback
            )
            
            logger.info(f"Comment {comment_id} approved by admin {admin_id}")
            
            return {
                'success': True,
                'message': 'Comment approved successfully',
                'content_id': comment_id,
                'content_type': 'comment',
                'new_status': 'approved',
                'feedback': feedback,
                'updated_at': comment.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to approve comment: {str(e)}")
            await self.db.rollback()
            return {'success': False, 'message': 'Failed to approve comment'}

    async def reject_comment(
        self,
        admin_id: UUID,
        comment_id: UUID,
        feedback: str,
        reason: str = "inappropriate"
    ) -> Dict[str, Any]:
        """Reject a comment with feedback."""
        try:
            if not feedback or len(feedback.strip()) < 5:
                return {'success': False, 'message': 'Feedback is required for rejection (minimum 5 characters)'}
            
            # Get the comment
            comment_result = await self.db.execute(
                select(Comment).where(Comment.id == comment_id)
            )
            comment = comment_result.scalar_one_or_none()
            
            if not comment:
                return {'success': False, 'message': 'Comment not found'}
            
            if comment.status != 'pending':
                return {'success': False, 'message': 'Comment is not pending approval'}
            
            # Update comment status
            if reason == "spam":
                comment.status = 'spam'
            else:
                comment.status = 'rejected'
            
            comment.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            # Log the rejection
            await self.audit_service.log_content_approval(
                admin_id=admin_id,
                content_id=comment_id,
                content_type='comment',
                action='rejected',
                feedback=f"{reason}: {feedback}"
            )
            
            logger.info(f"Comment {comment_id} rejected as {reason} by admin {admin_id}")
            
            return {
                'success': True,
                'message': f'Comment rejected as {reason}',
                'content_id': comment_id,
                'content_type': 'comment',
                'new_status': comment.status,
                'feedback': feedback,
                'updated_at': comment.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to reject comment: {str(e)}")
            await self.db.rollback()
            return {'success': False, 'message': 'Failed to reject comment'}

    async def bulk_approve_content(
        self,
        admin_id: UUID,
        content_ids: List[UUID],
        content_type: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk approve multiple content items."""
        try:
            if content_type not in ['post', 'comment']:
                return {'success': False, 'message': 'Invalid content type'}
            
            results = []
            successful = 0
            failed = 0
            
            for content_id in content_ids:
                if content_type == 'post':
                    result = await self.approve_post(admin_id, content_id, feedback, notify_author=False)
                else:
                    result = await self.approve_comment(admin_id, content_id, feedback)
                
                results.append({
                    'content_id': content_id,
                    'success': result['success'],
                    'message': result['message'],
                    'new_status': result.get('new_status')
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
            
            logger.info(f"Bulk approval completed by admin {admin_id}: {successful} successful, {failed} failed")
            
            return {
                'total_requested': len(content_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed bulk approval: {str(e)}")
            return {
                'total_requested': len(content_ids),
                'successful': 0,
                'failed': len(content_ids),
                'results': []
            }

    async def bulk_reject_content(
        self,
        admin_id: UUID,
        content_ids: List[UUID],
        content_type: str,
        feedback: str
    ) -> Dict[str, Any]:
        """Bulk reject multiple content items."""
        try:
            if content_type not in ['post', 'comment']:
                return {'success': False, 'message': 'Invalid content type'}
            
            if not feedback or len(feedback.strip()) < 5:
                return {'success': False, 'message': 'Feedback is required for bulk rejection'}
            
            results = []
            successful = 0
            failed = 0
            
            for content_id in content_ids:
                if content_type == 'post':
                    result = await self.reject_post(admin_id, content_id, feedback, notify_author=False)
                else:
                    result = await self.reject_comment(admin_id, content_id, feedback)
                
                results.append({
                    'content_id': content_id,
                    'success': result['success'],
                    'message': result['message'],
                    'new_status': result.get('new_status')
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
            
            logger.info(f"Bulk rejection completed by admin {admin_id}: {successful} successful, {failed} failed")
            
            return {
                'total_requested': len(content_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed bulk rejection: {str(e)}")
            return {
                'total_requested': len(content_ids),
                'successful': 0,
                'failed': len(content_ids),
                'results': []
            }

    async def get_rejected_content(
        self,
        content_type: str = "post",
        page: int = 1,
        per_page: int = 10,
        author_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get rejected content with pagination."""
        try:
            if content_type == "post":
                return await self._get_rejected_posts(page, per_page, author_id, category_id)
            elif content_type == "comment":
                return await self._get_rejected_comments(page, per_page)
            else:
                return [], 0
                
        except Exception as e:
            logger.error(f"Failed to get rejected content: {str(e)}")
            return [], 0

    async def get_content_approval_history(
        self,
        content_id: Optional[UUID] = None,
        content_type: Optional[str] = None,
        admin_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[ContentApproval]:
        """Get content approval history."""
        return await self.audit_service.get_content_approval_logs(
            content_id=content_id,
            content_type=content_type,
            admin_id=admin_id,
            limit=limit
        )

    async def get_moderation_statistics(self) -> Dict[str, Any]:
        """Get content moderation statistics."""
        try:
            # Pending content counts
            pending_posts = await self.db.execute(
                select(func.count(Post.id)).where(Post.status == 'under_review')
            )
            pending_comments = await self.db.execute(
                select(func.count(Comment.id)).where(Comment.status == 'pending')
            )
            
            # Today's activity
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Posts approved/rejected today
            posts_approved_today = await self.db.execute(
                select(func.count(ContentApproval.id)).where(
                    and_(
                        ContentApproval.content_type == 'post',
                        ContentApproval.action == 'approved',
                        ContentApproval.created_at >= today_start
                    )
                )
            )
            posts_rejected_today = await self.db.execute(
                select(func.count(ContentApproval.id)).where(
                    and_(
                        ContentApproval.content_type == 'post',
                        ContentApproval.action == 'rejected',
                        ContentApproval.created_at >= today_start
                    )
                )
            )
            
            # Comments approved/rejected today
            comments_approved_today = await self.db.execute(
                select(func.count(ContentApproval.id)).where(
                    and_(
                        ContentApproval.content_type == 'comment',
                        ContentApproval.action == 'approved',
                        ContentApproval.created_at >= today_start
                    )
                )
            )
            comments_rejected_today = await self.db.execute(
                select(func.count(ContentApproval.id)).where(
                    and_(
                        ContentApproval.content_type == 'comment',
                        ContentApproval.action == 'rejected',
                        ContentApproval.created_at >= today_start
                    )
                )
            )
            
            # Spam comments today
            spam_comments_today = await self.db.execute(
                select(func.count(Comment.id)).where(
                    and_(
                        Comment.status == 'spam',
                        Comment.updated_at >= today_start
                    )
                )
            )
            
            # Average approval time (simplified calculation)
            avg_approval_time = 2.5  # TODO: Implement actual calculation
            
            return {
                'pending_posts': pending_posts.scalar() or 0,
                'pending_comments': pending_comments.scalar() or 0,
                'approved_posts_today': posts_approved_today.scalar() or 0,
                'rejected_posts_today': posts_rejected_today.scalar() or 0,
                'approved_comments_today': comments_approved_today.scalar() or 0,
                'rejected_comments_today': comments_rejected_today.scalar() or 0,
                'spam_comments_today': spam_comments_today.scalar() or 0,
                'average_approval_time_hours': avg_approval_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get moderation statistics: {str(e)}")
            return {}

    # Helper methods
    
    async def _get_pending_posts(
        self,
        page: int,
        per_page: int,
        author_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Post], int]:
        """Get pending posts with filtering."""
        try:
            # Build query
            query = select(Post).options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags)
            ).where(Post.status == 'under_review')
            
            count_query = select(func.count(Post.id)).where(Post.status == 'under_review')
            
            # Apply filters
            conditions = []
            
            if author_id:
                conditions.append(Post.user_id == author_id)
            
            if category_id:
                conditions.append(Post.category_id == category_id)
            
            if search:
                search_term = f"%{search}%"
                conditions.append(
                    or_(
                        Post.title.ilike(search_term),
                        Post.body.ilike(search_term)
                    )
                )
            
            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(desc(Post.created_at))
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Execute query
            result = await self.db.execute(query)
            posts = result.scalars().all()
            
            return posts, total
            
        except Exception as e:
            logger.error(f"Failed to get pending posts: {str(e)}")
            return [], 0

    async def _get_pending_comments(
        self,
        page: int,
        per_page: int,
        search: Optional[str] = None
    ) -> Tuple[List[Comment], int]:
        """Get pending comments with filtering."""
        try:
            # Build query
            query = select(Comment).options(
                selectinload(Comment.author),
                selectinload(Comment.post)
            ).where(Comment.status == 'pending')
            
            count_query = select(func.count(Comment.id)).where(Comment.status == 'pending')
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(Comment.content.ilike(search_term))
                count_query = count_query.where(Comment.content.ilike(search_term))
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(desc(Comment.created_at))
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Execute query
            result = await self.db.execute(query)
            comments = result.scalars().all()
            
            return comments, total
            
        except Exception as e:
            logger.error(f"Failed to get pending comments: {str(e)}")
            return [], 0

    async def _get_rejected_posts(
        self,
        page: int,
        per_page: int,
        author_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None
    ) -> Tuple[List[Post], int]:
        """Get rejected posts with filtering."""
        try:
            # Build query
            query = select(Post).options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags)
            ).where(Post.status == 'rejected')
            
            count_query = select(func.count(Post.id)).where(Post.status == 'rejected')
            
            # Apply filters
            conditions = []
            
            if author_id:
                conditions.append(Post.user_id == author_id)
            
            if category_id:
                conditions.append(Post.category_id == category_id)
            
            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(desc(Post.updated_at))
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Execute query
            result = await self.db.execute(query)
            posts = result.scalars().all()
            
            return posts, total
            
        except Exception as e:
            logger.error(f"Failed to get rejected posts: {str(e)}")
            return [], 0

    async def _get_rejected_comments(
        self,
        page: int,
        per_page: int
    ) -> Tuple[List[Comment], int]:
        """Get rejected comments with pagination."""
        try:
            # Build query
            query = select(Comment).options(
                selectinload(Comment.author),
                selectinload(Comment.post)
            ).where(Comment.status.in_(['rejected', 'spam']))
            
            count_query = select(func.count(Comment.id)).where(
                Comment.status.in_(['rejected', 'spam'])
            )
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            query = query.order_by(desc(Comment.updated_at))
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Execute query
            result = await self.db.execute(query)
            comments = result.scalars().all()
            
            return comments, total
            
        except Exception as e:
            logger.error(f"Failed to get rejected comments: {str(e)}")
            return [], 0 