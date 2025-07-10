from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Post, Comment, Category, Tag
from models.interactions import View, Like, Bookmark
from models.audit import ContentApproval
from core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        try:
            user_counts = await self.db.execute(
                select(
                    func.count(User.id).label('total'),
                    func.sum(func.case((User.role == 'admin', 1), else_=0)).label('admins'),
                    func.sum(func.case((User.role == 'editor', 1), else_=0)).label('editors'),
                    func.sum(func.case((User.role == 'user', 1), else_=0)).label('regular_users')
                )
            )
            counts = user_counts.first()
            
            activity_counts = await self.db.execute(
                select(
                    func.sum(func.case((User.email_verified_at.is_not(None), 1), else_=0)).label('verified'),
                    func.sum(func.case((User.email_verified_at.is_(None), 1), else_=0)).label('unverified')
                )
            )
            activity = activity_counts.first()
            
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_signups_query = select(User).where(
                User.created_at >= thirty_days_ago
            ).order_by(desc(User.created_at)).limit(10)
            
            recent_signups_result = await self.db.execute(recent_signups_query)
            recent_signups = recent_signups_result.scalars().all()
            
            growth_metrics = await self._calculate_user_growth()
            
            return {
                'total': counts.total or 0,
                'admins': counts.admins or 0,
                'editors': counts.editors or 0,
                'regular_users': counts.regular_users or 0,
                'active_users': activity.verified or 0,
                'inactive_users': activity.unverified or 0,
                'verified_users': activity.verified or 0,
                'unverified_users': activity.unverified or 0,
                'recent_signups': recent_signups,
                'growth_metrics': growth_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {str(e)}")
            return {
                'total': 0, 'admins': 0, 'editors': 0, 'regular_users': 0,
                'active_users': 0, 'inactive_users': 0, 'verified_users': 0,
                'unverified_users': 0, 'recent_signups': [], 'growth_metrics': {}
            }

    async def get_content_overview(self, user_role: str = "admin", user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get content overview statistics filtered by user role."""
        try:
            post_query = select(Post)
            if user_role == "editor" and user_id:
                post_query = post_query.where(Post.user_id == user_id)
            
            status_counts = await self.db.execute(
                select(
                    func.count(Post.id).label('total'),
                    func.sum(func.case((Post.status == 'published', 1), else_=0)).label('published'),
                    func.sum(func.case((Post.status == 'draft', 1), else_=0)).label('draft'),
                    func.sum(func.case((Post.status == 'under_review', 1), else_=0)).label('under_review'),
                    func.sum(func.case((Post.status == 'rejected', 1), else_=0)).label('rejected'),
                    func.sum(func.case((Post.status == 'archived', 1), else_=0)).label('archived')
                ).select_from(post_query.subquery())
            )
            counts = status_counts.first()
            
            comment_query = select(Comment)
            if user_role == "editor" and user_id:
                comment_query = comment_query.join(Post).where(Post.user_id == user_id)
            
            comment_counts = await self.db.execute(
                select(
                    func.count(Comment.id).label('total'),
                    func.sum(func.case((Comment.status == 'approved', 1), else_=0)).label('approved'),
                    func.sum(func.case((Comment.status == 'pending', 1), else_=0)).label('pending')
                ).select_from(comment_query.subquery())
            )
            comment_stats = comment_counts.first()
            
            like_count = await self._get_like_count(user_role, user_id)
            view_stats = await self._get_view_statistics(user_role, user_id)
            
            most_viewed = await self._get_most_viewed_posts(user_role, user_id, limit=5)
            most_active = await self._get_most_active_users(limit=5)
            
           
            category_stats = await self._get_posts_by_category(user_role, user_id)
          
            recent_activity = await self._get_recent_activity(user_role, user_id)
            
            return {
                'total_posts': counts.total or 0,
                'published_posts': counts.published or 0,
                'draft_posts': counts.draft or 0,
                'scheduled_posts': 0,  # TODO: Implement scheduled posts
                'under_review_posts': counts.under_review or 0,
                'rejected_posts': counts.rejected or 0,
                'total_views': view_stats['total_views'],
                'unique_viewers': view_stats['unique_viewers'],
                'total_comments': comment_stats.total or 0,
                'approved_comments': comment_stats.approved or 0,
                'pending_comments': comment_stats.pending or 0,
                'total_likes': like_count,
                'most_viewed_posts': most_viewed,
                'most_active_users': most_active,
                'posts_by_category': category_stats,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            logger.error(f"Failed to get content overview: {str(e)}")
            return {
                'total_posts': 0, 'published_posts': 0, 'draft_posts': 0,
                'scheduled_posts': 0, 'under_review_posts': 0, 'rejected_posts': 0,
                'total_views': 0, 'unique_viewers': 0, 'total_comments': 0,
                'approved_comments': 0, 'pending_comments': 0, 'total_likes': 0,
                'most_viewed_posts': [], 'most_active_users': [], 
                'posts_by_category': [], 'recent_activity': {}
            }

    async def get_view_trends(self, period: str = "month", user_role: str = "admin", user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get view trends data for charts."""
        try:
            
            end_date = datetime.utcnow()
            if period == "day":
                start_date = end_date - timedelta(days=1)
                date_format = "%H"  # Hourly
                labels = [f"{i:02d}:00" for i in range(24)]
            elif period == "week":
                start_date = end_date - timedelta(days=7)
                date_format = "%Y-%m-%d"  # Daily
                labels = [(end_date - timedelta(days=i)).strftime("%m/%d") for i in range(6, -1, -1)]
            elif period == "year":
                start_date = end_date - timedelta(days=365)
                date_format = "%Y-%m"  # Monthly
                labels = [(end_date - timedelta(days=30*i)).strftime("%Y-%m") for i in range(11, -1, -1)]
            else:  # month
                start_date = end_date - timedelta(days=30)
                date_format = "%Y-%m-%d"  # Daily
                labels = [(end_date - timedelta(days=i)).strftime("%m/%d") for i in range(29, -1, -1)]
            
           
            view_query = select(View).where(
                View.created_at >= start_date,
                View.created_at <= end_date
            )
            
           
            if user_role == "editor" and user_id:
                view_query = view_query.join(Post).where(Post.user_id == user_id)
            
           
            if period == "day":
               
                view_counts = await self.db.execute(
                    select(
                        func.extract('hour', View.created_at).label('period'),
                        func.count(View.id).label('count')
                    ).where(
                        View.created_at >= start_date,
                        View.created_at <= end_date
                    ).group_by(func.extract('hour', View.created_at))
                )
            else:
               
                view_counts = await self.db.execute(
                    select(
                        func.date(View.created_at).label('period'),
                        func.count(View.id).label('count')
                    ).where(
                        View.created_at >= start_date,
                        View.created_at <= end_date
                    ).group_by(func.date(View.created_at))
                )
            
           
            data_dict = {str(row.period): row.count for row in view_counts}
            data = []
            
            for label in labels:
                if period == "day":
                   
                    hour = int(label.split(":")[0])
                    data.append(data_dict.get(str(hour), 0))
                else:
                   
                    data.append(data_dict.get(label, 0))
            
            return {
                'labels': labels,
                'data': data,
                'period': period
            }
            
        except Exception as e:
            logger.error(f"Failed to get view trends: {str(e)}")
            return {'labels': [], 'data': [], 'period': period}

    async def get_approval_queue(self) -> Dict[str, Any]:
        """Get content needing approval (admin only)."""
        try:
           
            pending_posts_query = select(Post).where(
                Post.status == 'under_review'
            ).options(selectinload(Post.author), selectinload(Post.category)).limit(10)
            
            pending_posts_result = await self.db.execute(pending_posts_query)
            pending_posts = pending_posts_result.scalars().all()
            
           
            pending_comments_count = await self.db.execute(
                select(func.count(Comment.id)).where(Comment.status == 'pending')
            )
            pending_comments = pending_comments_count.scalar() or 0
            
           
            rejected_posts_count = await self.db.execute(
                select(func.count(Post.id)).where(Post.status == 'rejected')
            )
            rejected_posts = rejected_posts_count.scalar() or 0
            
            return {
                'pending_posts': pending_posts,
                'pending_comments': pending_comments,
                'rejected_posts_count': rejected_posts
            }
            
        except Exception as e:
            logger.error(f"Failed to get approval queue: {str(e)}")
            return {'pending_posts': [], 'pending_comments': 0, 'rejected_posts_count': 0}

    async def get_recent_posts(self, user_role: str = "admin", user_id: Optional[UUID] = None, limit: int = 10) -> List[Post]:
        """Get recent posts filtered by user role."""
        try:
            query = select(Post).options(
                selectinload(Post.author), 
                selectinload(Post.category),
                selectinload(Post.tags)
            )
            
            if user_role == "editor" and user_id:
                query = query.where(Post.user_id == user_id)
            else:
               
                query = query.where(Post.status == 'published')
            
            query = query.order_by(desc(Post.created_at)).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Failed to get recent posts: {str(e)}")
            return []


    async def _calculate_user_growth(self) -> Dict[str, float]:
        """Calculate user growth metrics."""
        try:
            now = datetime.utcnow()

            yesterday = now - timedelta(days=1)
            daily_new = await self.db.execute(
                select(func.count(User.id)).where(User.created_at >= yesterday)
            )
            daily_growth = daily_new.scalar() or 0
            
            
            week_ago = now - timedelta(days=7)
            weekly_new = await self.db.execute(
                select(func.count(User.id)).where(User.created_at >= week_ago)
            )
            weekly_growth = weekly_new.scalar() or 0
            
            
            month_ago = now - timedelta(days=30)
            monthly_new = await self.db.execute(
                select(func.count(User.id)).where(User.created_at >= month_ago)
            )
            monthly_growth = monthly_new.scalar() or 0
            
            
            year_ago = now - timedelta(days=365)
            yearly_new = await self.db.execute(
                select(func.count(User.id)).where(User.created_at >= year_ago)
            )
            yearly_growth = yearly_new.scalar() or 0
            
            return {
                'daily_growth': float(daily_growth),
                'weekly_growth': float(weekly_growth),
                'monthly_growth': float(monthly_growth),
                'yearly_growth': float(yearly_growth)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate user growth: {str(e)}")
            return {'daily_growth': 0.0, 'weekly_growth': 0.0, 'monthly_growth': 0.0, 'yearly_growth': 0.0}

    async def _get_like_count(self, user_role: str, user_id: Optional[UUID]) -> int:
        """Get total like count filtered by user role."""
        try:
            if user_role == "editor" and user_id:
                result = await self.db.execute(
                    select(func.count(Like.id))
                    .join(Post, Like.post_id == Post.id)
                    .where(Post.user_id == user_id)
                )
            else:
                result = await self.db.execute(select(func.count(Like.id)))
            
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Failed to get like count: {str(e)}")
            return 0

    async def _get_view_statistics(self, user_role: str, user_id: Optional[UUID]) -> Dict[str, int]:
        """Get view statistics filtered by user role."""
        try:
            if user_role == "editor" and user_id:
                total_views = await self.db.execute(
                    select(func.count(View.id))
                    .join(Post, View.post_id == Post.id)
                    .where(Post.user_id == user_id)
                )
                unique_viewers = await self.db.execute(
                    select(func.count(func.distinct(View.user_id)))
                    .join(Post, View.post_id == Post.id)
                    .where(Post.user_id == user_id)
                )
            else:
                total_views = await self.db.execute(select(func.count(View.id)))
                unique_viewers = await self.db.execute(
                    select(func.count(func.distinct(View.user_id)))
                )
            
            return {
                'total_views': total_views.scalar() or 0,
                'unique_viewers': unique_viewers.scalar() or 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get view statistics: {str(e)}")
            return {'total_views': 0, 'unique_viewers': 0}

    async def _get_most_viewed_posts(self, user_role: str, user_id: Optional[UUID], limit: int) -> List[Dict[str, Any]]:
        """Get most viewed posts with statistics."""
        try:
            if user_role == "editor" and user_id:
                query = select(
                    Post.id, Post.title, Post.slug,
                    func.count(View.id).label('view_count'),
                    func.count(Like.id).label('like_count'),
                    func.count(Comment.id).label('comment_count'),
                    Post.published_at
                ).select_from(Post)\
                .outerjoin(View, Post.id == View.post_id)\
                .outerjoin(Like, Post.id == Like.post_id)\
                .outerjoin(Comment, and_(Post.id == Comment.post_id, Comment.status == 'approved'))\
                .where(Post.user_id == user_id, Post.status == 'published')\
                .group_by(Post.id, Post.title, Post.slug, Post.published_at)\
                .order_by(desc('view_count'))\
                .limit(limit)
            else:
                query = select(
                    Post.id, Post.title, Post.slug,
                    func.count(View.id).label('view_count'),
                    func.count(Like.id).label('like_count'),
                    func.count(Comment.id).label('comment_count'),
                    Post.published_at
                ).select_from(Post)\
                .outerjoin(View, Post.id == View.post_id)\
                .outerjoin(Like, Post.id == Like.post_id)\
                .outerjoin(Comment, and_(Post.id == Comment.post_id, Comment.status == 'approved'))\
                .where(Post.status == 'published')\
                .group_by(Post.id, Post.title, Post.slug, Post.published_at)\
                .order_by(desc('view_count'))\
                .limit(limit)
            
            result = await self.db.execute(query)
            return [
                {
                    'id': row.id,
                    'title': row.title,
                    'slug': row.slug,
                    'view_count': row.view_count or 0,
                    'like_count': row.like_count or 0,
                    'comment_count': row.comment_count or 0,
                    'published_at': row.published_at
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Failed to get most viewed posts: {str(e)}")
            return []

    async def _get_most_active_users(self, limit: int) -> List[Dict[str, Any]]:
        """Get most active users by post count."""
        try:
            query = select(
                User.id, User.name, User.email, User.avatar,
                func.count(Post.id).label('post_count'),
                func.count(Comment.id).label('comment_count')
            ).select_from(User)\
            .outerjoin(Post, and_(User.id == Post.user_id, Post.status == 'published'))\
            .outerjoin(Comment, and_(User.id == Comment.user_id, Comment.status == 'approved'))\
            .group_by(User.id, User.name, User.email, User.avatar)\
            .order_by(desc('post_count'))\
            .limit(limit)
            
            result = await self.db.execute(query)
            return [
                {
                    'id': row.id,
                    'name': row.name,
                    'email': row.email,
                    'avatar': row.avatar,
                    'post_count': row.post_count or 0,
                    'comment_count': row.comment_count or 0
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Failed to get most active users: {str(e)}")
            return []

    async def _get_posts_by_category(self, user_role: str, user_id: Optional[UUID]) -> List[Dict[str, Any]]:
        """Get post distribution by category."""
        try:
            if user_role == "editor" and user_id:
                query = select(
                    Category.id, Category.name, Category.slug,
                    func.count(Post.id).label('post_count')
                ).select_from(Category)\
                .outerjoin(Post, and_(Category.id == Post.category_id, Post.user_id == user_id))\
                .group_by(Category.id, Category.name, Category.slug)\
                .order_by(desc('post_count'))
            else:
                query = select(
                    Category.id, Category.name, Category.slug,
                    func.count(Post.id).label('post_count')
                ).select_from(Category)\
                .outerjoin(Post, and_(Category.id == Post.category_id, Post.status == 'published'))\
                .group_by(Category.id, Category.name, Category.slug)\
                .order_by(desc('post_count'))
            
            result = await self.db.execute(query)
            return [
                {
                    'id': row.id,
                    'name': row.name,
                    'slug': row.slug,
                    'post_count': row.post_count or 0
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Failed to get posts by category: {str(e)}")
            return []

    async def _get_recent_activity(self, user_role: str, user_id: Optional[UUID]) -> Dict[str, int]:
        """Get recent activity metrics (last 7 days)."""
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
           
            post_filter = Post.created_at >= seven_days_ago
            if user_role == "editor" and user_id:
                post_filter = and_(post_filter, Post.user_id == user_id)
            
            new_posts = await self.db.execute(
                select(func.count(Post.id)).where(post_filter)
            )
            
           
            comment_filter = Comment.created_at >= seven_days_ago
            if user_role == "editor" and user_id:
                comment_filter = and_(
                    comment_filter,
                    Comment.post_id.in_(
                        select(Post.id).where(Post.user_id == user_id)
                    )
                )
            
            new_comments = await self.db.execute(
                select(func.count(Comment.id)).where(comment_filter)
            )
            
           
            new_users = 0
            if user_role == "admin":
                new_users_result = await self.db.execute(
                    select(func.count(User.id)).where(User.created_at >= seven_days_ago)
                )
                new_users = new_users_result.scalar() or 0
            
            view_filter = View.created_at >= seven_days_ago
            if user_role == "editor" and user_id:
                view_filter = and_(
                    view_filter,
                    View.post_id.in_(
                        select(Post.id).where(Post.user_id == user_id)
                    )
                )
            
            total_views = await self.db.execute(
                select(func.count(View.id)).where(view_filter)
            )
            
            return {
                'new_posts_7_days': new_posts.scalar() or 0,
                'new_comments_7_days': new_comments.scalar() or 0,
                'new_users_7_days': new_users,
                'total_views_7_days': total_views.scalar() or 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {str(e)}")
            return {'new_posts_7_days': 0, 'new_comments_7_days': 0, 'new_users_7_days': 0, 'total_views_7_days': 0} 