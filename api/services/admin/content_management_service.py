"""
Content Management Service

Provides comprehensive content analytics, moderation workflows, performance tracking,
and administrative insights for effective content governance and platform optimization.
Follows SubPRD-ContentManagementService.md specifications.
"""

from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, text
from sqlalchemy.orm import selectinload, joinedload

from models.post import Post
from models.user import User
from models.category import Category
from models.tag import Tag
from models.comment import Comment
from models.interactions import Like, Bookmark, View
from schemas.admin.dashboard import (
    ContentOverviewResponse, ViewTrendsResponse, ContentApprovalResponse,
    PostPerformanceResponse, UserActivityResponse, CategoryStatsResponse,
    TagStatsResponse, UserContributorResponse, UserGrowthMetricsResponse,
    PostApprovalResponse, CommentApprovalResponse, DailySignupResponse
)
from schemas.post import PostSummaryResponse
from schemas.user import UserSummaryResponse
from core.exceptions import ContentManagementError


class ContentManagementService:
    """Service for content analytics and administrative insights."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_content_overview(self) -> ContentOverviewResponse:
        """
        Get comprehensive content overview statistics.
        
        Returns:
            ContentOverviewResponse: Complete content analytics data
        """
        try:
            # Get post statistics
            post_stats = await self._get_post_statistics()
            
            # Get engagement statistics
            engagement_stats = await self._get_engagement_statistics()
            
            # Get trending content data
            trending_data = await self._get_trending_content()
            
            # Get recent activity (last 7 days)
            recent_activity = await self._get_recent_activity()
            
            # Get most viewed posts
            most_viewed = await self._get_most_viewed_posts()
            
            # Get most active users
            most_active = await self._get_most_active_users()
            
            # Get category distribution
            category_stats = await self._get_category_distribution()
            
            # Get popular tags
            popular_tags = await self._get_popular_tags()
            
            return ContentOverviewResponse(
                **post_stats,
                **engagement_stats,
                **recent_activity,
                most_viewed_posts=most_viewed,
                most_active_users=most_active,
                posts_by_category=category_stats,
                popular_tags=popular_tags
            )
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get content overview: {str(e)}")
    
    async def get_view_trends(self, period: str = 'week') -> ViewTrendsResponse:
        """
        Get view trend analysis for specified period.
        
        Args:
            period: Time period ('day', 'week', 'month', 'year')
            
        Returns:
            ViewTrendsResponse: View trend data with charts
        """
        try:
            # Calculate date range
            start_date, end_date = self._get_date_range(period)
            
            # Get view data aggregated by date
            view_data = await self._aggregate_view_trends(start_date, end_date)
            
            # Format data for charts
            formatted_data = self._format_trend_data(view_data, start_date, end_date, period)
            
            return ViewTrendsResponse(
                period=period,
                start_date=start_date,
                end_date=end_date,
                **formatted_data
            )
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get view trends: {str(e)}")
    
    async def get_content_needing_approval(self) -> ContentApprovalResponse:
        """
        Get content requiring approval and moderation.
        
        Returns:
            ContentApprovalResponse: Content pending approval
        """
        try:
            # Get posts under review
            pending_posts_query = select(Post).where(
                Post.status == 'under_review'
            ).options(
                selectinload(Post.author),
                selectinload(Post.category)
            ).order_by(Post.created_at.desc())
            
            pending_posts_result = await self.db.execute(pending_posts_query)
            pending_posts = pending_posts_result.scalars().all()
            
            # Get unapproved comments
            pending_comments_query = select(Comment).where(
                Comment.approved == False
            ).options(
                selectinload(Comment.user),
                selectinload(Comment.post)
            ).order_by(Comment.created_at.desc())
            
            pending_comments_result = await self.db.execute(pending_comments_query)
            pending_comments = pending_comments_result.scalars().all()
            
            # Calculate average approval time (placeholder)
            avg_approval_time = await self._calculate_average_approval_time()
            
            # Format responses
            pending_posts_response = [
                PostApprovalResponse(
                    id=post.id,
                    title=post.title,
                    author=UserSummaryResponse.from_orm(post.author),
                    submitted_at=post.created_at,
                    category=post.category.name if post.category else None,
                    excerpt=post.excerpt,
                    status=post.status
                ) for post in pending_posts
            ]
            
            pending_comments_response = [
                CommentApprovalResponse(
                    id=comment.id,
                    body=comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
                    author=UserSummaryResponse.from_orm(comment.user),
                    post_title=comment.post.title,
                    submitted_at=comment.created_at
                ) for comment in pending_comments
            ]
            
            return ContentApprovalResponse(
                pending_posts=pending_posts_response,
                pending_comments=pending_comments_response,
                total_pending=len(pending_posts) + len(pending_comments),
                average_approval_time=avg_approval_time
            )
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get approval content: {str(e)}")
    
    async def get_user_activity_stats(self) -> List[UserActivityResponse]:
        """
        Get user activity statistics and engagement levels.
        
        Returns:
            List[UserActivityResponse]: User activity data
        """
        try:
            # Complex query to get user activity stats
            query = select(
                User.id,
                User.name,
                User.email,
                User.created_at,
                User.updated_at,
                func.count(Post.id.distinct()).label('posts_count'),
                func.count(Comment.id.distinct()).label('comments_count'),
                func.count(Like.id.distinct()).label('likes_received'),
                func.count(View.id.distinct()).label('total_views')
            ).select_from(User)\
            .outerjoin(Post, User.id == Post.user_id)\
            .outerjoin(Comment, User.id == Comment.user_id)\
            .outerjoin(Like, Post.id == Like.post_id)\
            .outerjoin(View, Post.id == View.post_id)\
            .group_by(User.id, User.name, User.email, User.created_at, User.updated_at)\
            .order_by(desc('posts_count'))
            
            result = await self.db.execute(query)
            user_stats = result.all()
            
            # Format response
            activities = []
            for stats in user_stats:
                engagement_level = self._calculate_engagement_level(
                    stats.posts_count, stats.comments_count, stats.likes_received
                )
                
                activities.append(UserActivityResponse(
                    id=stats.id,
                    name=stats.name,
                    email=stats.email,
                    posts_count=stats.posts_count or 0,
                    comments_count=stats.comments_count or 0,
                    likes_received=stats.likes_received or 0,
                    total_views=stats.total_views or 0,
                    engagement_level=engagement_level,
                    last_active=stats.updated_at,
                    join_date=stats.created_at
                ))
            
            return activities[:50]  # Return top 50 most active users
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get user activity stats: {str(e)}")
    
    async def get_popular_content(self, timeframe: str = 'week') -> List[PostPerformanceResponse]:
        """
        Get popular content based on engagement metrics.
        
        Args:
            timeframe: Time period for popularity calculation
            
        Returns:
            List[PostPerformanceResponse]: Popular content data
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow()
            if timeframe == 'day':
                cutoff_date -= timedelta(days=1)
            elif timeframe == 'week':
                cutoff_date -= timedelta(weeks=1)
            elif timeframe == 'month':
                cutoff_date -= timedelta(days=30)
            elif timeframe == 'year':
                cutoff_date -= timedelta(days=365)
            
            # Query for popular posts
            query = select(
                Post.id,
                Post.title,
                Post.slug,
                Post.published_at,
                Post.user_id,
                Post.category_id,
                func.count(View.id.distinct()).label('view_count'),
                func.count(Like.id.distinct()).label('like_count'),
                func.count(Comment.id.distinct()).label('comment_count'),
                func.count(Bookmark.id.distinct()).label('bookmark_count')
            ).select_from(Post)\
            .outerjoin(View, and_(Post.id == View.post_id, View.viewed_at >= cutoff_date))\
            .outerjoin(Like, Post.id == Like.post_id)\
            .outerjoin(Comment, Post.id == Comment.post_id)\
            .outerjoin(Bookmark, Post.id == Bookmark.post_id)\
            .where(
                and_(
                    Post.status == 'published',
                    Post.published_at.isnot(None),
                    Post.published_at >= cutoff_date
                )
            )\
            .options(
                selectinload(Post.author),
                selectinload(Post.category)
            )\
            .group_by(Post.id, Post.title, Post.slug, Post.published_at, Post.user_id, Post.category_id)\
            .order_by(desc('view_count'), desc('like_count'))\
            .limit(20)
            
            result = await self.db.execute(query)
            popular_posts = result.all()
            
            # Format response
            performances = []
            for post_data in popular_posts:
                # Get the actual post object for relationships
                post_query = select(Post).where(Post.id == post_data.id)\
                    .options(selectinload(Post.author), selectinload(Post.category))
                post_result = await self.db.execute(post_query)
                post = post_result.scalar_one()
                
                engagement_score = self._calculate_engagement_score(
                    post_data.view_count, post_data.like_count, 
                    post_data.comment_count, post_data.bookmark_count
                )
                
                performances.append(PostPerformanceResponse(
                    id=post.id,
                    title=post.title,
                    slug=post.slug,
                    author=UserSummaryResponse.from_orm(post.author),
                    published_at=post.published_at,
                    view_count=post_data.view_count or 0,
                    like_count=post_data.like_count or 0,
                    comment_count=post_data.comment_count or 0,
                    bookmark_count=post_data.bookmark_count or 0,
                    engagement_score=engagement_score,
                    category=post.category.name if post.category else None
                ))
            
            return performances
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get popular content: {str(e)}")
    
    async def get_category_performance(self) -> List[CategoryStatsResponse]:
        """
        Get category performance and distribution statistics.
        
        Returns:
            List[CategoryStatsResponse]: Category performance data
        """
        try:
            # Query category statistics
            query = select(
                Category.id,
                Category.name,
                Category.slug,
                func.count(Post.id.distinct()).label('posts_count'),
                func.count(View.id.distinct()).label('total_views'),
                func.avg(
                    func.count(Like.id.distinct()) + 
                    func.count(Comment.id.distinct())
                ).label('avg_engagement')
            ).select_from(Category)\
            .outerjoin(Post, Category.id == Post.category_id)\
            .outerjoin(View, Post.id == View.post_id)\
            .outerjoin(Like, Post.id == Like.post_id)\
            .outerjoin(Comment, Post.id == Comment.post_id)\
            .group_by(Category.id, Category.name, Category.slug)\
            .order_by(desc('posts_count'))
            
            result = await self.db.execute(query)
            category_stats = result.all()
            
            # Calculate growth rates (placeholder - would need historical data)
            performances = []
            for stats in category_stats:
                performances.append(CategoryStatsResponse(
                    id=stats.id,
                    name=stats.name,
                    slug=stats.slug,
                    posts_count=stats.posts_count or 0,
                    total_views=stats.total_views or 0,
                    average_engagement=float(stats.avg_engagement or 0),
                    growth_rate=0.0  # Placeholder - requires historical comparison
                ))
            
            return performances
            
        except Exception as e:
            raise ContentManagementError(f"Failed to get category performance: {str(e)}")
    
    # Helper methods
    async def _get_post_statistics(self) -> Dict[str, int]:
        """Get basic post count statistics."""
        total_posts = await self.db.scalar(select(func.count(Post.id)))
        published_posts = await self.db.scalar(
            select(func.count(Post.id)).where(Post.status == 'published')
        )
        draft_posts = await self.db.scalar(
            select(func.count(Post.id)).where(Post.status == 'draft')
        )
        scheduled_posts = await self.db.scalar(
            select(func.count(Post.id)).where(Post.status == 'scheduled')
        )
        pending_review = await self.db.scalar(
            select(func.count(Post.id)).where(Post.status == 'under_review')
        )
        
        return {
            'total_posts': total_posts or 0,
            'published_posts': published_posts or 0,
            'draft_posts': draft_posts or 0,
            'scheduled_posts': scheduled_posts or 0,
            'pending_review_posts': pending_review or 0
        }
    
    async def _get_engagement_statistics(self) -> Dict[str, int]:
        """Get engagement statistics."""
        total_views = await self.db.scalar(select(func.count(View.id)))
        unique_viewers = await self.db.scalar(
            select(func.count(View.user_id.distinct())).where(View.user_id.isnot(None))
        )
        total_comments = await self.db.scalar(select(func.count(Comment.id)))
        total_likes = await self.db.scalar(select(func.count(Like.id)))
        
        return {
            'total_views': total_views or 0,
            'unique_viewers': unique_viewers or 0,
            'total_comments': total_comments or 0,
            'total_likes': total_likes or 0
        }
    
    async def _get_recent_activity(self) -> Dict[str, int]:
        """Get recent activity (last 7 days)."""
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        recent_posts = await self.db.scalar(
            select(func.count(Post.id)).where(Post.created_at >= cutoff)
        )
        recent_views = await self.db.scalar(
            select(func.count(View.id)).where(View.viewed_at >= cutoff)
        )
        recent_comments = await self.db.scalar(
            select(func.count(Comment.id)).where(Comment.created_at >= cutoff)
        )
        
        return {
            'recent_posts': recent_posts or 0,
            'recent_views': recent_views or 0,
            'recent_comments': recent_comments or 0
        }
    
    async def _get_most_viewed_posts(self) -> List[PostPerformanceResponse]:
        """Get most viewed posts."""
        query = select(
            Post.id,
            Post.title,
            Post.slug,
            Post.published_at,
            func.count(View.id).label('view_count')
        ).select_from(Post)\
        .outerjoin(View, Post.id == View.post_id)\
        .where(Post.status == 'published')\
        .options(selectinload(Post.author), selectinload(Post.category))\
        .group_by(Post.id, Post.title, Post.slug, Post.published_at)\
        .order_by(desc('view_count'))\
        .limit(10)
        
        result = await self.db.execute(query)
        posts_data = result.all()
        
        performances = []
        for post_data in posts_data:
            # Get full post with relationships
            post_query = select(Post).where(Post.id == post_data.id)\
                .options(selectinload(Post.author), selectinload(Post.category))
            post_result = await self.db.execute(post_query)
            post = post_result.scalar_one()
            
            performances.append(PostPerformanceResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                author=UserSummaryResponse.from_orm(post.author),
                published_at=post.published_at,
                view_count=post_data.view_count or 0,
                like_count=0,  # Would need separate query
                comment_count=0,  # Would need separate query
                bookmark_count=0,  # Would need separate query
                engagement_score=0.0,
                category=post.category.name if post.category else None
            ))
        
        return performances
    
    async def _get_most_active_users(self) -> List[UserActivityResponse]:
        """Get most active users."""
        query = select(
            User.id,
            User.name,
            User.email,
            User.created_at,
            User.updated_at,
            func.count(Post.id).label('posts_count')
        ).select_from(User)\
        .outerjoin(Post, User.id == Post.user_id)\
        .group_by(User.id, User.name, User.email, User.created_at, User.updated_at)\
        .order_by(desc('posts_count'))\
        .limit(10)
        
        result = await self.db.execute(query)
        users_data = result.all()
        
        activities = []
        for user_data in users_data:
            activities.append(UserActivityResponse(
                id=user_data.id,
                name=user_data.name,
                email=user_data.email,
                posts_count=user_data.posts_count or 0,
                comments_count=0,  # Would need separate query
                likes_received=0,  # Would need separate query
                total_views=0,  # Would need separate query
                engagement_level='medium',
                last_active=user_data.updated_at,
                join_date=user_data.created_at
            ))
        
        return activities
    
    async def _get_category_distribution(self) -> List[CategoryStatsResponse]:
        """Get category distribution."""
        query = select(
            Category.id,
            Category.name,
            Category.slug,
            func.count(Post.id).label('posts_count')
        ).select_from(Category)\
        .outerjoin(Post, Category.id == Post.category_id)\
        .group_by(Category.id, Category.name, Category.slug)\
        .order_by(desc('posts_count'))
        
        result = await self.db.execute(query)
        category_data = result.all()
        
        stats = []
        for cat_data in category_data:
            stats.append(CategoryStatsResponse(
                id=cat_data.id,
                name=cat_data.name,
                slug=cat_data.slug,
                posts_count=cat_data.posts_count or 0,
                total_views=0,  # Would need separate query
                average_engagement=0.0,
                growth_rate=0.0
            ))
        
        return stats
    
    async def _get_popular_tags(self) -> List[TagStatsResponse]:
        """Get popular tags."""
        # This would require a proper post_tags relationship table
        # For now, return empty list
        return []
    
    def _get_date_range(self, period: str) -> Tuple[date, date]:
        """Calculate date range for given period."""
        end_date = date.today()
        
        if period == 'day':
            start_date = end_date - timedelta(days=1)
        elif period == 'week':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(weeks=1)
        
        return start_date, end_date
    
    async def _aggregate_view_trends(self, start_date: date, end_date: date) -> List[Tuple[date, int]]:
        """Aggregate view data by date."""
        query = select(
            func.date(View.viewed_at).label('view_date'),
            func.count(View.id).label('view_count')
        ).where(
            and_(
                View.viewed_at >= start_date,
                View.viewed_at <= end_date
            )
        ).group_by(func.date(View.viewed_at))\
        .order_by('view_date')
        
        result = await self.db.execute(query)
        return result.all()
    
    def _format_trend_data(self, view_data: List[Tuple[date, int]], 
                          start_date: date, end_date: date, period: str) -> Dict[str, Any]:
        """Format trend data for charts."""
        # Create complete date range
        current_date = start_date
        labels = []
        data = []
        view_dict = {item[0]: item[1] for item in view_data}
        
        while current_date <= end_date:
            labels.append(current_date.strftime('%Y-%m-%d'))
            data.append(view_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        total_views = sum(data)
        avg_views = total_views / len(data) if data else 0
        peak_day = labels[data.index(max(data))] if data else None
        peak_views = max(data) if data else 0
        
        return {
            'labels': labels,
            'data': data,
            'total_views': total_views,
            'average_daily_views': avg_views,
            'peak_day': peak_day,
            'peak_views': peak_views
        }
    
    async def _calculate_average_approval_time(self) -> Optional[float]:
        """Calculate average approval time in hours."""
        # Placeholder - would need approval timestamp tracking
        return 24.0
    
    def _calculate_engagement_level(self, posts: int, comments: int, likes: int) -> str:
        """Calculate user engagement level."""
        total_engagement = posts * 3 + comments * 2 + likes
        
        if total_engagement >= 50:
            return 'high'
        elif total_engagement >= 20:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_engagement_score(self, views: int, likes: int, comments: int, bookmarks: int) -> float:
        """Calculate engagement score for posts."""
        if views == 0:
            return 0.0
        
        # Weighted engagement calculation
        engagement = (likes * 0.3 + comments * 0.4 + bookmarks * 0.3)
        return round((engagement / views) * 100, 2) 