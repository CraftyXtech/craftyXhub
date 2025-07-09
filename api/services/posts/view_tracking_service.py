"""
View Tracking Service

Service for tracking post views and analytics following SubPRD-PostAPI.md specifications.
"""

from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.dialects.postgresql import insert

from models.interactions import View
from models.user import User
from models.post import Post


class ViewTrackingService:
    """Service class for tracking post views and analytics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def track_view(
        self,
        post_id: UUID,
        ip_address: str,
        user_agent: str,
        user_id: Optional[UUID] = None,
        referrer: Optional[str] = None
    ) -> bool:
        """
        Track a post view with deduplication logic.
        
        Args:
            post_id: UUID of the post being viewed
            ip_address: IP address of the viewer
            user_agent: User agent string
            user_id: Optional authenticated user ID
            referrer: Optional referrer URL
            
        Returns:
            True if view was recorded, False if duplicate
        """
        # Check if post exists and is published
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
            return False

        # Implement deduplication logic
        # Don't count multiple views from same IP/user within 1 hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        duplicate_conditions = [
            View.post_id == post_id,
            View.created_at > cutoff_time
        ]

        if user_id:
            # For authenticated users, deduplicate by user_id
            duplicate_conditions.append(View.user_id == user_id)
        else:
            # For anonymous users, deduplicate by IP address
            duplicate_conditions.append(
                and_(
                    View.ip_address == ip_address,
                    View.user_id.is_(None)
                )
            )

        duplicate_query = select(View).where(and_(*duplicate_conditions))
        duplicate_result = await self.db.execute(duplicate_query)
        existing_view = duplicate_result.scalar_one_or_none()

        if existing_view:
            # This is a duplicate view, don't record it
            return False

        # Record the new view
        new_view = View(
            post_id=post_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            created_at=datetime.utcnow()
        )

        self.db.add(new_view)
        await self.db.commit()
        return True

    async def get_view_count(self, post_id: UUID) -> int:
        """
        Get total view count for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Total number of views
        """
        query = select(func.count(View.id)).where(View.post_id == post_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_unique_view_count(self, post_id: UUID) -> int:
        """
        Get unique view count for a post (distinct IP addresses).
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Number of unique viewers
        """
        query = select(func.count(func.distinct(View.ip_address))).where(
            View.post_id == post_id
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_authenticated_view_count(self, post_id: UUID) -> int:
        """
        Get view count from authenticated users only.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            Number of authenticated user views
        """
        query = select(func.count(View.id)).where(
            and_(
                View.post_id == post_id,
                View.user_id.is_not(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_recent_views(
        self, 
        post_id: UUID, 
        hours: int = 24,
        limit: int = 50
    ) -> list:
        """
        Get recent views for a post within specified hours.
        
        Args:
            post_id: UUID of the post
            hours: Number of hours to look back
            limit: Maximum number of views to return
            
        Returns:
            List of recent view records
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = select(View).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time
            )
        ).order_by(desc(View.created_at)).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_view_analytics(
        self, 
        post_id: UUID,
        days: int = 30
    ) -> dict:
        """
        Get view analytics for a post over specified days.
        
        Args:
            post_id: UUID of the post
            days: Number of days to analyze
            
        Returns:
            Dictionary with analytics data
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Total views
        total_views_query = select(func.count(View.id)).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time
            )
        )
        total_views_result = await self.db.execute(total_views_query)
        total_views = total_views_result.scalar() or 0

        # Unique viewers
        unique_viewers_query = select(func.count(func.distinct(View.ip_address))).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time
            )
        )
        unique_viewers_result = await self.db.execute(unique_viewers_query)
        unique_viewers = unique_viewers_result.scalar() or 0

        # Authenticated vs anonymous views
        auth_views_query = select(func.count(View.id)).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time,
                View.user_id.is_not(None)
            )
        )
        auth_views_result = await self.db.execute(auth_views_query)
        authenticated_views = auth_views_result.scalar() or 0

        anonymous_views = total_views - authenticated_views

        # Daily view counts (simplified)
        daily_views_query = select(
            func.date(View.created_at).label('view_date'),
            func.count(View.id).label('view_count')
        ).where(
            and_(
                View.post_id == post_id,
                View.created_at > cutoff_time
            )
        ).group_by(func.date(View.created_at)).order_by(func.date(View.created_at))

        daily_views_result = await self.db.execute(daily_views_query)
        daily_views = [
            {
                'date': row.view_date,
                'views': row.view_count
            }
            for row in daily_views_result
        ]

        return {
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'authenticated_views': authenticated_views,
            'anonymous_views': anonymous_views,
            'daily_views': daily_views,
            'average_daily_views': total_views / days if days > 0 else 0
        }

    async def get_top_referrers(
        self, 
        post_id: UUID, 
        limit: int = 10
    ) -> list:
        """
        Get top referrers for a post.
        
        Args:
            post_id: UUID of the post
            limit: Maximum number of referrers to return
            
        Returns:
            List of top referrers with counts
        """
        query = select(
            View.referrer,
            func.count(View.id).label('count')
        ).where(
            and_(
                View.post_id == post_id,
                View.referrer.is_not(None),
                View.referrer != ''
            )
        ).group_by(View.referrer).order_by(desc('count')).limit(limit)

        result = await self.db.execute(query)
        return [
            {
                'referrer': row.referrer,
                'count': row.count
            }
            for row in result
        ]

    async def get_user_view_history(
        self, 
        user_id: UUID,
        limit: int = 50
    ) -> list:
        """
        Get view history for a specific user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of views to return
            
        Returns:
            List of user's view history
        """
        query = select(View).where(
            View.user_id == user_id
        ).order_by(desc(View.created_at)).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def has_user_viewed_post(
        self, 
        user_id: UUID, 
        post_id: UUID
    ) -> bool:
        """
        Check if a user has viewed a specific post.
        
        Args:
            user_id: UUID of the user
            post_id: UUID of the post
            
        Returns:
            True if user has viewed the post, False otherwise
        """
        query = select(View).where(
            and_(
                View.user_id == user_id,
                View.post_id == post_id
            )
        ).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def delete_old_views(self, days: int = 90) -> int:
        """
        Delete old view records to maintain database performance.
        
        Args:
            days: Number of days to keep (delete older records)
            
        Returns:
            Number of deleted records
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get count before deletion
        count_query = select(func.count(View.id)).where(
            View.created_at < cutoff_time
        )
        count_result = await self.db.execute(count_query)
        delete_count = count_result.scalar() or 0

        # Delete old records
        delete_query = View.__table__.delete().where(
            View.created_at < cutoff_time
        )
        await self.db.execute(delete_query)
        await self.db.commit()

        return delete_count 