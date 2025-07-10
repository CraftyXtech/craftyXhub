"""Dashboard Service"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload

from models.post import Post
from models.user import User
from models.category import Category
from models.interactions import View, Like, Comment
from schemas.editor.dashboard import (
    DashboardStatsRequest,
    DashboardStatsResponse,
    DashboardSummaryResponse,
    TrendingPostResponse,
    ViewTrendsResponse,
    PostDistributionResponse,
    EditorAnalyticsResponse,
    PostAnalyticsResponse,
    ViewMetricsResponse,
    EngagementMetricsResponse,
    PerformanceSummaryResponse,
    CategoryPerformanceResponse,
    EngagementTrendsResponse
)
from schemas.editor.posts import PostSummaryResponse
from schemas.post import AuthorResponse
from schemas.post import CategoryResponse, TagResponse


class DashboardService:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(
        self, 
        request: DashboardStatsRequest, 
        current_user: User
    ) -> DashboardStatsResponse:
        """Get comprehensive dashboard statistics for editor."""
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if request.period == "day":
            start_date = end_date - timedelta(days=1)
            previous_start = start_date - timedelta(days=1)
        elif request.period == "week":
            start_date = end_date - timedelta(weeks=1)
            previous_start = start_date - timedelta(weeks=1)
        elif request.period == "month":
            start_date = end_date - timedelta(days=30)
            previous_start = start_date - timedelta(days=30)
        elif request.period == "year":
            start_date = end_date - timedelta(days=365)
            previous_start = start_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
            previous_start = start_date - timedelta(days=30)
        
        # Get summary statistics
        summary = await self._get_dashboard_summary(
            current_user, start_date, end_date, previous_start
        )
        
        # Get trending posts
        trending_posts = await self._get_trending_posts(
            current_user, start_date, end_date, limit=10
        )
        
        # Get view trends
        view_trends = await self._get_view_trends(
            current_user, start_date, end_date, request.period
        )
        
        # Get post distribution
        post_distribution = await self._get_post_distribution(current_user)
        
        # Get recent posts
        recent_posts = await self._get_recent_posts(
            current_user, request.page, request.per_page
        )
        
        return DashboardStatsResponse(
            summary=summary,
            trending_posts=trending_posts,
            view_trends=view_trends,
            post_distribution=post_distribution,
            recent_posts=recent_posts
        )
    
    async def get_editor_analytics(
        self, 
        current_user: User,
        start_date: datetime,
        end_date: datetime
    ) -> EditorAnalyticsResponse:
        """Get detailed analytics for editor."""
        # Get posts analytics
        posts_analytics = await self._get_posts_analytics(
            current_user, start_date, end_date
        )
        
        # Get performance summary
        performance_summary = await self._get_performance_summary(
            current_user, start_date, end_date
        )
        
        # Get top categories
        top_categories = await self._get_top_categories(
            current_user, start_date, end_date
        )
        
        # Get engagement trends
        engagement_trends = await self._get_engagement_trends(
            current_user, start_date, end_date
        )
        
        return EditorAnalyticsResponse(
            posts_analytics=posts_analytics,
            performance_summary=performance_summary,
            top_categories=top_categories,
            engagement_trends=engagement_trends
        )
    
    async def _get_dashboard_summary(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime,
        previous_start: datetime
    ) -> DashboardSummaryResponse:
        """Get dashboard summary statistics."""
        # Total views for current period
        total_views_result = await self.db.execute(
            select(func.count(View.id))
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                View.created_at >= start_date,
                View.created_at <= end_date
            )
        )
        total_views = total_views_result.scalar() or 0
        
        # Recent views (last 7 days)
        recent_date = end_date - timedelta(days=7)
        recent_views_result = await self.db.execute(
            select(func.count(View.id))
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                View.created_at >= recent_date
            )
        )
        recent_views = recent_views_result.scalar() or 0
        
        # Previous period views for growth calculation
        previous_views_result = await self.db.execute(
            select(func.count(View.id))
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                View.created_at >= previous_start,
                View.created_at < start_date
            )
        )
        previous_views = previous_views_result.scalar() or 0
        
        # Post counts by status
        post_counts = await self.db.execute(
            select(Post.status, func.count(Post.id))
            .where(Post.user_id == current_user.id)
            .group_by(Post.status)
        )
        
        published_posts = 0
        draft_posts = 0
        scheduled_posts = 0
        pending_review_posts = 0
        
        for status, count in post_counts:
            if status == "published":
                published_posts = count
            elif status == "draft":
                draft_posts = count
            elif status == "scheduled":
                scheduled_posts = count
            elif status == "under_review":
                pending_review_posts = count
        
        # Total likes
        total_likes_result = await self.db.execute(
            select(func.count(Like.id))
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                Like.created_at >= start_date,
                Like.created_at <= end_date
            )
        )
        total_likes = total_likes_result.scalar() or 0
        
        # Total comments
        total_comments_result = await self.db.execute(
            select(func.count(Comment.id))
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                Comment.created_at >= start_date,
                Comment.created_at <= end_date,
                Comment.approved == True
            )
        )
        total_comments = total_comments_result.scalar() or 0
        
        # Calculate growth percentage
        view_growth_percentage = 0.0
        if previous_views > 0:
            view_growth_percentage = ((total_views - previous_views) / previous_views) * 100
        
        # Calculate engagement rate
        engagement_rate = 0.0
        if total_views > 0:
            engagement_rate = ((total_likes + total_comments) / total_views) * 100
        
        return DashboardSummaryResponse(
            total_views=total_views,
            recent_views=recent_views,
            published_posts=published_posts,
            draft_posts=draft_posts,
            scheduled_posts=scheduled_posts,
            pending_review_posts=pending_review_posts,
            total_likes=total_likes,
            total_comments=total_comments,
            view_growth_percentage=view_growth_percentage,
            engagement_rate=engagement_rate
        )
    
    async def _get_trending_posts(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 10
    ) -> List[TrendingPostResponse]:
        """Get trending posts for the editor."""
        # Get posts with view counts and engagement
        result = await self.db.execute(
            select(
                Post,
                func.count(View.id).label("view_count"),
                func.count(Like.id).label("likes_count"),
                func.count(Comment.id).label("comments_count")
            )
            .outerjoin(View)
            .outerjoin(Like)
            .outerjoin(Comment, and_(Comment.post_id == Post.id, Comment.approved == True))
            .where(
                Post.user_id == current_user.id,
                Post.status == "published",
                Post.published_at >= start_date,
                Post.published_at <= end_date
            )
            .group_by(Post.id)
            .order_by(desc("view_count"))
            .limit(limit)
        )
        
        trending_posts = []
        for post, view_count, likes_count, comments_count in result:
            # Calculate engagement score
            engagement_score = (likes_count * 2 + comments_count * 3) / max(view_count, 1)
            
            trending_posts.append(TrendingPostResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                view_count=view_count,
                view_growth=0,  # TODO: Calculate growth
                likes_count=likes_count,
                comments_count=comments_count,
                published_at=post.published_at,
                engagement_score=engagement_score
            ))
        
        return trending_posts
    
    async def _get_view_trends(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime,
        period: str
    ) -> ViewTrendsResponse:
        """Get view trends data for charts."""
        # Determine date grouping based on period
        if period == "day":
            date_trunc = "hour"
            date_format = "%H:00"
        elif period == "week":
            date_trunc = "day"
            date_format = "%Y-%m-%d"
        elif period == "month":
            date_trunc = "day"
            date_format = "%Y-%m-%d"
        else:
            date_trunc = "day"
            date_format = "%Y-%m-%d"
        
        # Get view counts grouped by date
        result = await self.db.execute(
            select(
                func.date_trunc(date_trunc, View.created_at).label("date"),
                func.count(View.id).label("views")
            )
            .join(Post)
            .where(
                Post.user_id == current_user.id,
                View.created_at >= start_date,
                View.created_at <= end_date
            )
            .group_by(func.date_trunc(date_trunc, View.created_at))
            .order_by("date")
        )
        
        labels = []
        data = []
        total_views = 0
        
        for date, views in result:
            labels.append(date.strftime(date_format))
            data.append(views)
            total_views += views
        
        return ViewTrendsResponse(
            labels=labels,
            data=data,
            period=period,
            total_views=total_views,
            growth_percentage=0.0  # TODO: Calculate growth
        )
    
    async def _get_post_distribution(self, current_user: User) -> PostDistributionResponse:
        """Get post distribution by status."""
        result = await self.db.execute(
            select(Post.status, func.count(Post.id))
            .where(Post.user_id == current_user.id)
            .group_by(Post.status)
        )
        
        distribution = {
            "published": 0,
            "draft": 0,
            "under_review": 0,
            "scheduled": 0,
            "rejected": 0
        }
        
        for status, count in result:
            if status in distribution:
                distribution[status] = count
        
        return PostDistributionResponse(**distribution)
    
    async def _get_recent_posts(
        self, 
        current_user: User, 
        page: int, 
        per_page: int
    ) -> List[PostSummaryResponse]:
        """Get recent posts for the editor."""
        offset = (page - 1) * per_page
        
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.author)
            )
            .where(Post.user_id == current_user.id)
            .order_by(desc(Post.updated_at))
            .offset(offset)
            .limit(per_page)
        )
        
        posts = result.scalars().all()
        recent_posts = []
        
        for post in posts:
            # Get counts
            view_count = await self._get_post_view_count(post.id)
            like_count = await self._get_post_like_count(post.id)
            comment_count = await self._get_post_comment_count(post.id)
            
            # Build response
            author = AuthorResponse(
                id=post.author.id,
                name=post.author.name,
                avatar=post.author.avatar
            )
            
            category = None
            if post.category:
                category = CategoryResponse(
                    id=post.category.id,
                    name=post.category.name,
                    slug=post.category.slug,
                    description=post.category.description
                )
            
            tags = []
            for tag in post.tags:
                tags.append(TagResponse(
                    id=tag.id,
                    name=tag.name,
                    slug=tag.slug
                ))
            
            recent_posts.append(PostSummaryResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                featured_image_path=post.featured_image_path,
                status=post.status,
                category=category,
                tags=tags,
                author=author,
                created_at=post.created_at,
                updated_at=post.updated_at,
                published_at=post.published_at,
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count
            ))
        
        return recent_posts
    
    async def _get_posts_analytics(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[PostAnalyticsResponse]:
        """Get detailed analytics for all posts."""
        # Get posts with basic info
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.category),
                selectinload(Post.tags),
                selectinload(Post.author)
            )
            .where(
                Post.user_id == current_user.id,
                Post.status == "published"
            )
            .order_by(desc(Post.published_at))
        )
        
        posts = result.scalars().all()
        posts_analytics = []
        
        for post in posts:
            # Get view metrics
            view_metrics = await self._get_view_metrics(post.id, start_date, end_date)
            
            # Get engagement metrics
            engagement_metrics = await self._get_engagement_metrics(post.id, start_date, end_date)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(view_metrics, engagement_metrics)
            
            # Build post summary
            post_summary = await self._build_post_summary(post)
            
            posts_analytics.append(PostAnalyticsResponse(
                post=post_summary,
                views=view_metrics,
                engagement=engagement_metrics,
                performance_score=performance_score
            ))
        
        return posts_analytics
    
    async def _get_performance_summary(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime
    ) -> PerformanceSummaryResponse:
        """Get performance summary for the editor."""
        # Total posts
        total_posts_result = await self.db.execute(
            select(func.count(Post.id))
            .where(
                Post.user_id == current_user.id,
                Post.status == "published"
            )
        )
        total_posts = total_posts_result.scalar() or 0
        
        # Average views per post
        avg_views_result = await self.db.execute(
            select(func.avg(func.count(View.id)))
            .select_from(Post)
            .outerjoin(View)
            .where(
                Post.user_id == current_user.id,
                Post.status == "published"
            )
            .group_by(Post.id)
        )
        average_views_per_post = float(avg_views_result.scalar() or 0)
        
        # Average engagement rate
        # This is a simplified calculation
        average_engagement_rate = 5.0  # TODO: Implement proper calculation
        
        # Top performing category
        top_category_result = await self.db.execute(
            select(Category, func.count(View.id).label("total_views"))
            .select_from(Post)
            .join(Category)
            .outerjoin(View)
            .where(
                Post.user_id == current_user.id,
                Post.status == "published"
            )
            .group_by(Category.id)
            .order_by(desc("total_views"))
            .limit(1)
        )
        
        top_category = None
        top_category_row = top_category_result.first()
        if top_category_row:
            category = top_category_row[0]
            top_category = CategoryResponse(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description
            )
        
        return PerformanceSummaryResponse(
            total_posts=total_posts,
            average_views_per_post=average_views_per_post,
            average_engagement_rate=average_engagement_rate,
            top_performing_category=top_category,
            best_performing_day="Monday",  # TODO: Calculate from data
            total_reading_time=0  # TODO: Calculate from data
        )
    
    async def _get_top_categories(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[CategoryPerformanceResponse]:
        """Get top performing categories."""
        result = await self.db.execute(
            select(
                Category,
                func.count(Post.id).label("post_count"),
                func.count(View.id).label("total_views")
            )
            .select_from(Post)
            .join(Category)
            .outerjoin(View)
            .where(
                Post.user_id == current_user.id,
                Post.status == "published"
            )
            .group_by(Category.id)
            .order_by(desc("total_views"))
            .limit(5)
        )
        
        top_categories = []
        for category, post_count, total_views in result:
            category_response = CategoryResponse(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description
            )
            
            # Calculate performance score
            performance_score = (total_views * 0.7) + (post_count * 0.3)
            
            top_categories.append(CategoryPerformanceResponse(
                category=category_response,
                post_count=post_count,
                total_views=total_views,
                average_engagement=0.0,  # TODO: Calculate
                performance_score=performance_score
            ))
        
        return top_categories
    
    async def _get_engagement_trends(
        self, 
        current_user: User, 
        start_date: datetime, 
        end_date: datetime
    ) -> EngagementTrendsResponse:
        """Get engagement trends over time."""
        # Get daily engagement data
        result = await self.db.execute(
            select(
                func.date_trunc('day', Like.created_at).label("date"),
                func.count(Like.id).label("likes"),
                func.count(Comment.id).label("comments")
            )
            .select_from(Post)
            .outerjoin(Like)
            .outerjoin(Comment, and_(Comment.post_id == Post.id, Comment.approved == True))
            .where(
                Post.user_id == current_user.id,
                or_(
                    Like.created_at >= start_date,
                    Comment.created_at >= start_date
                ),
                or_(
                    Like.created_at <= end_date,
                    Comment.created_at <= end_date
                )
            )
            .group_by(func.date_trunc('day', Like.created_at))
            .order_by("date")
        )
        
        labels = []
        likes_data = []
        comments_data = []
        shares_data = []  # TODO: Implement shares
        
        for date, likes, comments in result:
            if date:
                labels.append(date.strftime("%Y-%m-%d"))
                likes_data.append(likes or 0)
                comments_data.append(comments or 0)
                shares_data.append(0)  # TODO: Implement shares
        
        total_engagement = sum(likes_data) + sum(comments_data)
        
        return EngagementTrendsResponse(
            labels=labels,
            likes_data=likes_data,
            comments_data=comments_data,
            shares_data=shares_data,
            period="day",
            total_engagement=total_engagement,
            growth_percentage=0.0  # TODO: Calculate growth
        )
    
    # Helper methods
    
    async def _get_post_view_count(self, post_id: UUID) -> int:
        """Get view count for a post."""
        result = await self.db.execute(
            select(func.count(View.id))
            .where(View.post_id == post_id)
        )
        return result.scalar() or 0
    
    async def _get_post_like_count(self, post_id: UUID) -> int:
        """Get like count for a post."""
        result = await self.db.execute(
            select(func.count(Like.id))
            .where(Like.post_id == post_id)
        )
        return result.scalar() or 0
    
    async def _get_post_comment_count(self, post_id: UUID) -> int:
        """Get comment count for a post."""
        result = await self.db.execute(
            select(func.count(Comment.id))
            .where(Comment.post_id == post_id, Comment.approved == True)
        )
        return result.scalar() or 0
    
    async def _get_view_metrics(self, post_id: UUID, start_date: datetime, end_date: datetime) -> ViewMetricsResponse:
        """Get view metrics for a post."""
        # Total views
        total_views = await self._get_post_view_count(post_id)
        
        # Unique views (simplified - assuming all views are unique)
        unique_views = total_views
        
        # Views today
        today = datetime.utcnow().date()
        views_today_result = await self.db.execute(
            select(func.count(View.id))
            .where(
                View.post_id == post_id,
                func.date(View.created_at) == today
            )
        )
        views_today = views_today_result.scalar() or 0
        
        # Views this week
        week_start = datetime.utcnow() - timedelta(days=7)
        views_this_week_result = await self.db.execute(
            select(func.count(View.id))
            .where(
                View.post_id == post_id,
                View.created_at >= week_start
            )
        )
        views_this_week = views_this_week_result.scalar() or 0
        
        return ViewMetricsResponse(
            total_views=total_views,
            unique_views=unique_views,
            views_today=views_today,
            views_this_week=views_this_week,
            average_session_duration=120  # TODO: Calculate from data
        )
    
    async def _get_engagement_metrics(self, post_id: UUID, start_date: datetime, end_date: datetime) -> EngagementMetricsResponse:
        """Get engagement metrics for a post."""
        total_likes = await self._get_post_like_count(post_id)
        total_comments = await self._get_post_comment_count(post_id)
        total_shares = 0  # TODO: Implement shares
        
        # Calculate engagement rate
        total_views = await self._get_post_view_count(post_id)
        engagement_rate = 0.0
        if total_views > 0:
            engagement_rate = ((total_likes + total_comments + total_shares) / total_views) * 100
        
        return EngagementMetricsResponse(
            total_likes=total_likes,
            total_comments=total_comments,
            total_shares=total_shares,
            engagement_rate=engagement_rate,
            average_reading_time=180  # TODO: Calculate from data
        )
    
    def _calculate_performance_score(self, view_metrics: ViewMetricsResponse, engagement_metrics: EngagementMetricsResponse) -> float:
        """Calculate performance score for a post."""
        # Weighted score based on views and engagement
        view_score = min(view_metrics.total_views / 100, 10)  # Max 10 points for views
        engagement_score = min(engagement_metrics.engagement_rate / 10, 10)  # Max 10 points for engagement
        
        return (view_score * 0.6) + (engagement_score * 0.4)
    
    async def _build_post_summary(self, post: Post) -> PostSummaryResponse:
        """Build post summary response."""
        view_count = await self._get_post_view_count(post.id)
        like_count = await self._get_post_like_count(post.id)
        comment_count = await self._get_post_comment_count(post.id)
        
        author = AuthorResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar
        )
        
        category = None
        if post.category:
            category = CategoryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            )
        
        tags = []
        for tag in post.tags:
            tags.append(TagResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug
            ))
        
        return PostSummaryResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            featured_image_path=post.featured_image_path,
            status=post.status,
            category=category,
            tags=tags,
            author=author,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count
        ) 