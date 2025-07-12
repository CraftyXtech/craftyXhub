from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import Session, select, and_, func, or_, desc
from sqlalchemy import text

from models.post import Post
from models.user import User, UserRead
from models.interactions import Like, Bookmark, View, Follow
from models.comment import Comment
from models.tag import Tag


class AnalyticsService:
    """Service class for analytics and reporting."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Post Analytics
    async def get_post_performance_metrics(self, post_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance metrics for a post."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic engagement metrics
        total_likes = self.session.exec(
            select(func.count(Like.id)).where(
                and_(Like.likeable_id == post_id, Like.likeable_type == 'post')
            )
        ).first() or 0
        
        total_bookmarks = self.session.exec(
            select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        ).first() or 0
        
        total_views = self.session.exec(
            select(func.count(View.id)).where(View.post_id == post_id)
        ).first() or 0
        
        total_comments = self.session.exec(
            select(func.count(Comment.id)).where(
                and_(Comment.post_id == post_id, Comment.status == 'approved')
            )
        ).first() or 0
        
        # Recent activity (within specified days)
        recent_likes = self.session.exec(
            select(func.count(Like.id)).where(
                and_(
                    Like.likeable_id == post_id,
                    Like.likeable_type == 'post',
                    Like.created_at >= since_date
                )
            )
        ).first() or 0
        
        recent_views = self.session.exec(
            select(func.count(View.id)).where(
                and_(View.post_id == post_id, View.viewed_at >= since_date)
            )
        ).first() or 0
        
        # Reading metrics
        total_reads = self.session.exec(
            select(func.count(UserRead.user_id)).where(UserRead.post_id == post_id)
        ).first() or 0
        
        completed_reads = self.session.exec(
            select(func.count(UserRead.user_id)).where(
                and_(UserRead.post_id == post_id, UserRead.read_progress == 100)
            )
        ).first() or 0
        
        avg_read_progress = self.session.exec(
            select(func.avg(UserRead.read_progress)).where(UserRead.post_id == post_id)
        ).first() or 0
        
        # Engagement rate calculation
        engagement_rate = 0
        if total_views > 0:
            engagement_actions = total_likes + total_bookmarks + total_comments
            engagement_rate = (engagement_actions / total_views) * 100
        
        return {
            "post_id": post_id,
            "period_days": days,
            "total_metrics": {
                "likes": total_likes,
                "bookmarks": total_bookmarks,
                "views": total_views,
                "comments": total_comments,
                "reads": total_reads,
                "completed_reads": completed_reads
            },
            "recent_metrics": {
                "likes": recent_likes,
                "views": recent_views
            },
            "performance_indicators": {
                "engagement_rate": round(engagement_rate, 2),
                "completion_rate": round((completed_reads / total_reads * 100) if total_reads > 0 else 0, 2),
                "avg_read_progress": round(float(avg_read_progress or 0), 2)
            }
        }
    
    async def get_posts_ranking(self, metric: str = 'engagement', limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """Get top-performing posts ranked by specified metric."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        if metric == 'engagement':
            # Rank by combined engagement score
            posts = self.session.exec(
                select(
                    Post,
                    func.count(func.distinct(Like.id)).label('likes'),
                    func.count(func.distinct(Bookmark.id)).label('bookmarks'),
                    func.count(func.distinct(View.id)).label('views'),
                    func.count(func.distinct(Comment.id)).label('comments')
                )
                .outerjoin(Like, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
                .outerjoin(Bookmark, Bookmark.post_id == Post.id)
                .outerjoin(View, View.post_id == Post.id)
                .outerjoin(Comment, and_(Comment.post_id == Post.id, Comment.status == 'approved'))
                .where(Post.status == 'published')
                .group_by(Post.id)
                .order_by(
                    (func.count(func.distinct(Like.id)) * 3 + 
                     func.count(func.distinct(Bookmark.id)) * 4 + 
                     func.count(func.distinct(View.id)) * 1 + 
                     func.count(func.distinct(Comment.id)) * 2).desc()
                )
                .limit(limit)
            ).all()
            
        elif metric == 'views':
            posts = self.session.exec(
                select(Post, func.count(View.id).label('views'))
                .join(View, View.post_id == Post.id)
                .where(and_(Post.status == 'published', View.viewed_at >= since_date))
                .group_by(Post.id)
                .order_by(desc('views'))
                .limit(limit)
            ).all()
            
        elif metric == 'likes':
            posts = self.session.exec(
                select(Post, func.count(Like.id).label('likes'))
                .join(Like, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
                .where(and_(Post.status == 'published', Like.created_at >= since_date))
                .group_by(Post.id)
                .order_by(desc('likes'))
                .limit(limit)
            ).all()
            
        else:
            raise ValueError("Invalid metric. Choose from: engagement, views, likes")
        
        return [
            {
                "post": result[0],
                "metrics": {k: v for k, v in zip(['likes', 'bookmarks', 'views', 'comments'], result[1:]) if len(result) > 1}
            }
            for result in posts
        ]
    
    # User Analytics
    async def get_user_analytics(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics for a user."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Content creation metrics
        total_posts = self.session.exec(
            select(func.count(Post.id)).where(Post.user_id == user_id)
        ).first() or 0
        
        published_posts = self.session.exec(
            select(func.count(Post.id)).where(
                and_(Post.user_id == user_id, Post.status == 'published')
            )
        ).first() or 0
        
        recent_posts = self.session.exec(
            select(func.count(Post.id)).where(
                and_(Post.user_id == user_id, Post.created_at >= since_date)
            )
        ).first() or 0
        
        # Engagement received on user's posts
        posts_likes = self.session.exec(
            select(func.count(Like.id))
            .select_from(Like)
            .join(Post, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
            .where(Post.user_id == user_id)
        ).first() or 0
        
        posts_views = self.session.exec(
            select(func.count(View.id))
            .select_from(View)
            .join(Post, View.post_id == Post.id)
            .where(Post.user_id == user_id)
        ).first() or 0
        
        posts_comments = self.session.exec(
            select(func.count(Comment.id))
            .select_from(Comment)
            .join(Post, Comment.post_id == Post.id)
            .where(and_(Post.user_id == user_id, Comment.status == 'approved'))
        ).first() or 0
        
        # User activity metrics
        likes_given = self.session.exec(
            select(func.count(Like.id)).where(Like.user_id == user_id)
        ).first() or 0
        
        bookmarks_made = self.session.exec(
            select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        ).first() or 0
        
        comments_made = self.session.exec(
            select(func.count(Comment.id)).where(
                and_(Comment.user_id == user_id, Comment.status == 'approved')
            )
        ).first() or 0
        
        # Social metrics
        followers_count = self.session.exec(
            select(func.count(Follow.id)).where(Follow.followed_id == user_id)
        ).first() or 0
        
        following_count = self.session.exec(
            select(func.count(Follow.id)).where(Follow.follower_id == user_id)
        ).first() or 0
        
        return {
            "user_id": user_id,
            "period_days": days,
            "content_metrics": {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "recent_posts": recent_posts,
                "posts_likes_received": posts_likes,
                "posts_views_received": posts_views,
                "posts_comments_received": posts_comments
            },
            "activity_metrics": {
                "likes_given": likes_given,
                "bookmarks_made": bookmarks_made,
                "comments_made": comments_made
            },
            "social_metrics": {
                "followers": followers_count,
                "following": following_count
            }
        }
    
    # Platform Analytics
    async def get_platform_overview(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-wide analytics overview."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # User metrics
        total_users = self.session.exec(select(func.count(User.id))).first() or 0
        new_users = self.session.exec(
            select(func.count(User.id)).where(User.created_at >= since_date)
        ).first() or 0
        
        active_users = self.session.exec(
            select(func.count(func.distinct(Like.user_id)))
            .select_from(Like)
            .where(Like.created_at >= since_date)
        ).first() or 0
        
        # Content metrics
        total_posts = self.session.exec(
            select(func.count(Post.id)).where(Post.status == 'published')
        ).first() or 0
        
        new_posts = self.session.exec(
            select(func.count(Post.id)).where(
                and_(Post.status == 'published', Post.created_at >= since_date)
            )
        ).first() or 0
        
        # Engagement metrics
        total_likes = self.session.exec(
            select(func.count(Like.id)).where(Like.created_at >= since_date)
        ).first() or 0
        
        total_views = self.session.exec(
            select(func.count(View.id)).where(View.viewed_at >= since_date)
        ).first() or 0
        
        total_comments = self.session.exec(
            select(func.count(Comment.id)).where(
                and_(Comment.status == 'approved', Comment.created_at >= since_date)
            )
        ).first() or 0
        
        return {
            "period_days": days,
            "user_metrics": {
                "total_users": total_users,
                "new_users": new_users,
                "active_users": active_users
            },
            "content_metrics": {
                "total_posts": total_posts,
                "new_posts": new_posts
            },
            "engagement_metrics": {
                "total_likes": total_likes,
                "total_views": total_views,
                "total_comments": total_comments
            }
        }
    
    async def get_trending_tags(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending tags based on recent activity."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        trending_tags = self.session.exec(
            select(
                Tag,
                func.count(func.distinct(Like.id)).label('likes'),
                func.count(func.distinct(View.id)).label('views'),
                func.count(func.distinct(Comment.id)).label('comments')
            )
            .join(Post, Tag.posts.property.secondary.c.tag_id == Tag.id)
            .outerjoin(Like, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
            .outerjoin(View, View.post_id == Post.id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .where(
                and_(
                    Post.status == 'published',
                    or_(
                        Like.created_at >= since_date,
                        View.viewed_at >= since_date,
                        Comment.created_at >= since_date
                    )
                )
            )
            .group_by(Tag.id)
            .order_by(
                (func.count(func.distinct(Like.id)) * 2 + 
                 func.count(func.distinct(View.id)) * 1 + 
                 func.count(func.distinct(Comment.id)) * 3).desc()
            )
            .limit(limit)
        ).all()
        
        return [
            {
                "tag": result[0],
                "activity_score": result[1] * 2 + result[2] * 1 + result[3] * 3,
                "metrics": {
                    "likes": result[1],
                    "views": result[2],
                    "comments": result[3]
                }
            }
            for result in trending_tags
        ]
    
    async def get_engagement_timeline(self, days: int = 30, granularity: str = 'daily') -> List[Dict[str, Any]]:
        """Get engagement timeline data."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        if granularity == 'daily':
            date_format = '%Y-%m-%d'
            date_trunc = 'day'
        elif granularity == 'hourly':
            date_format = '%Y-%m-%d %H:00'
            date_trunc = 'hour'
        else:
            raise ValueError("Granularity must be 'daily' or 'hourly'")
        
        # This is a simplified version - in production, you'd want to use proper date functions
        timeline_data = []
        current_date = since_date
        
        while current_date <= datetime.utcnow():
            next_date = current_date + (timedelta(days=1) if granularity == 'daily' else timedelta(hours=1))
            
            likes = self.session.exec(
                select(func.count(Like.id)).where(
                    and_(Like.created_at >= current_date, Like.created_at < next_date)
                )
            ).first() or 0
            
            views = self.session.exec(
                select(func.count(View.id)).where(
                    and_(View.viewed_at >= current_date, View.viewed_at < next_date)
                )
            ).first() or 0
            
            comments = self.session.exec(
                select(func.count(Comment.id)).where(
                    and_(Comment.created_at >= current_date, Comment.created_at < next_date)
                )
            ).first() or 0
            
            timeline_data.append({
                "date": current_date.strftime(date_format),
                "likes": likes,
                "views": views,
                "comments": comments,
                "total_engagement": likes + views + comments
            })
            
            current_date = next_date
        
        return timeline_data
    
    async def get_content_performance_by_category(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get content performance metrics grouped by category."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        from models.category import Category
        
        category_stats = self.session.exec(
            select(
                Category,
                func.count(func.distinct(Post.id)).label('posts_count'),
                func.count(func.distinct(Like.id)).label('likes'),
                func.count(func.distinct(View.id)).label('views'),
                func.count(func.distinct(Comment.id)).label('comments')
            )
            .join(Post, Post.category_id == Category.id)
            .outerjoin(Like, and_(Like.likeable_id == Post.id, Like.likeable_type == 'post'))
            .outerjoin(View, View.post_id == Post.id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .where(
                and_(
                    Post.status == 'published',
                    Post.created_at >= since_date
                )
            )
            .group_by(Category.id)
            .order_by(desc('posts_count'))
        ).all()
        
        return [
            {
                "category": result[0],
                "metrics": {
                    "posts_count": result[1],
                    "likes": result[2],
                    "views": result[3],
                    "comments": result[4],
                    "engagement_score": result[2] * 2 + result[3] * 1 + result[4] * 3
                }
            }
            for result in category_stats
        ] 