from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select, and_, func, or_
from sqlalchemy.orm import selectinload

from models.interactions import Like, Bookmark, View
from models.post import Post
from models.comment import Comment
from models.user import User, UserRead
from core.exceptions import ResourceNotFoundException, ValidationException


class InteractionService:
    """Service class for handling content interactions (likes, bookmarks, views)."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Like functionality
    async def like_content(self, user_id: UUID, content_type: str, content_id: UUID) -> Like:
        """Like a post or comment."""
        if content_type not in ['post', 'comment']:
            raise ValidationException("Content type must be 'post' or 'comment'")
        
        # Verify content exists
        if content_type == 'post':
            content = self.session.exec(select(Post).where(Post.id == content_id)).first()
        else:
            content = self.session.exec(select(Comment).where(Comment.id == content_id)).first()
        
        if not content:
            raise ResourceNotFoundException(f"{content_type.title()} not found")
        
        # Check if already liked
        existing_like = self.session.exec(
            select(Like).where(
                and_(
                    Like.user_id == user_id,
                    Like.likeable_type == content_type,
                    Like.likeable_id == content_id
                )
            )
        ).first()
        
        if existing_like:
            return existing_like
        
        # Create new like
        like = Like(
            user_id=user_id,
            likeable_type=content_type,
            likeable_id=content_id
        )
        self.session.add(like)
        self.session.commit()
        self.session.refresh(like)
        
        return like
    
    async def unlike_content(self, user_id: UUID, content_type: str, content_id: UUID) -> bool:
        """Unlike a post or comment."""
        like = self.session.exec(
            select(Like).where(
                and_(
                    Like.user_id == user_id,
                    Like.likeable_type == content_type,
                    Like.likeable_id == content_id
                )
            )
        ).first()
        
        if not like:
            return False
        
        self.session.delete(like)
        self.session.commit()
        return True
    
    async def is_content_liked_by_user(self, user_id: UUID, content_type: str, content_id: UUID) -> bool:
        """Check if content is liked by user."""
        like = self.session.exec(
            select(Like).where(
                and_(
                    Like.user_id == user_id,
                    Like.likeable_type == content_type,
                    Like.likeable_id == content_id
                )
            )
        ).first()
        
        return like is not None
    
    async def get_content_likes_count(self, content_type: str, content_id: UUID) -> int:
        """Get count of likes for content."""
        count = self.session.exec(
            select(func.count(Like.id)).where(
                and_(
                    Like.likeable_type == content_type,
                    Like.likeable_id == content_id
                )
            )
        ).first()
        
        return count or 0
    
    async def get_content_likers(self, content_type: str, content_id: UUID, limit: int = 50, offset: int = 0) -> List[User]:
        """Get users who liked the content."""
        likers = self.session.exec(
            select(User)
            .join(Like, Like.user_id == User.id)
            .where(
                and_(
                    Like.likeable_type == content_type,
                    Like.likeable_id == content_id
                )
            )
            .offset(offset)
            .limit(limit)
        ).all()
        
        return list(likers)
    
    # Bookmark functionality
    async def bookmark_post(self, user_id: UUID, post_id: UUID) -> Bookmark:
        """Bookmark a post."""
        # Verify post exists
        post = self.session.exec(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise ResourceNotFoundException("Post not found")
        
        # Check if already bookmarked
        existing_bookmark = self.session.exec(
            select(Bookmark).where(
                and_(Bookmark.user_id == user_id, Bookmark.post_id == post_id)
            )
        ).first()
        
        if existing_bookmark:
            return existing_bookmark
        
        # Create new bookmark
        bookmark = Bookmark(user_id=user_id, post_id=post_id)
        self.session.add(bookmark)
        self.session.commit()
        self.session.refresh(bookmark)
        
        return bookmark
    
    async def unbookmark_post(self, user_id: UUID, post_id: UUID) -> bool:
        """Remove bookmark from post."""
        bookmark = self.session.exec(
            select(Bookmark).where(
                and_(Bookmark.user_id == user_id, Bookmark.post_id == post_id)
            )
        ).first()
        
        if not bookmark:
            return False
        
        self.session.delete(bookmark)
        self.session.commit()
        return True
    
    async def is_post_bookmarked_by_user(self, user_id: UUID, post_id: UUID) -> bool:
        """Check if post is bookmarked by user."""
        bookmark = self.session.exec(
            select(Bookmark).where(
                and_(Bookmark.user_id == user_id, Bookmark.post_id == post_id)
            )
        ).first()
        
        return bookmark is not None
    
    async def get_post_bookmarks_count(self, post_id: UUID) -> int:
        """Get count of bookmarks for post."""
        count = self.session.exec(
            select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        ).first()
        
        return count or 0
    
    # View functionality
    async def record_view(self, post_id: UUID, user_id: Optional[UUID] = None, 
                         ip_address: Optional[str] = None, 
                         user_agent: Optional[str] = None) -> View:
        """Record a post view."""
        # Verify post exists
        post = self.session.exec(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise ResourceNotFoundException("Post not found")
        
        # For logged-in users, check if they've viewed this post recently (within last hour)
        if user_id:
            recent_view = self.session.exec(
                select(View).where(
                    and_(
                        View.post_id == post_id,
                        View.user_id == user_id,
                        View.viewed_at > datetime.utcnow().replace(hour=datetime.utcnow().hour - 1)
                    )
                )
            ).first()
            
            if recent_view:
                return recent_view
        
        # Create new view record
        view = View(
            post_id=post_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(view)
        self.session.commit()
        self.session.refresh(view)
        
        return view
    
    async def get_post_views_count(self, post_id: UUID) -> int:
        """Get count of views for post."""
        count = self.session.exec(
            select(func.count(View.id)).where(View.post_id == post_id)
        ).first()
        
        return count or 0
    
    async def get_post_unique_views_count(self, post_id: UUID) -> int:
        """Get count of unique views for post (by user or IP)."""
        # Count unique user views + unique anonymous IP views
        user_views = self.session.exec(
            select(func.count(func.distinct(View.user_id))).where(
                and_(View.post_id == post_id, View.user_id.isnot(None))
            )
        ).first() or 0
        
        anonymous_views = self.session.exec(
            select(func.count(func.distinct(View.ip_address))).where(
                and_(View.post_id == post_id, View.user_id.is_(None))
            )
        ).first() or 0
        
        return user_views + anonymous_views
    
    # Read tracking functionality
    async def record_read(self, user_id: UUID, post_id: UUID, progress: int = 100) -> UserRead:
        """Record that user has read a post."""
        if not 0 <= progress <= 100:
            raise ValidationException("Progress must be between 0 and 100")
        
        # Verify post exists
        post = self.session.exec(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise ResourceNotFoundException("Post not found")
        
        # Check if read record exists
        existing_read = self.session.exec(
            select(UserRead).where(
                and_(UserRead.user_id == user_id, UserRead.post_id == post_id)
            )
        ).first()
        
        if existing_read:
            # Update progress if higher
            if progress > existing_read.read_progress:
                existing_read.read_progress = progress
                existing_read.read_at = datetime.utcnow()
                self.session.commit()
                self.session.refresh(existing_read)
            return existing_read
        
        # Create new read record
        user_read = UserRead(
            user_id=user_id,
            post_id=post_id,
            read_progress=progress
        )
        self.session.add(user_read)
        self.session.commit()
        self.session.refresh(user_read)
        
        return user_read
    
    async def get_user_read_progress(self, user_id: UUID, post_id: UUID) -> Optional[int]:
        """Get user's reading progress for a post."""
        user_read = self.session.exec(
            select(UserRead).where(
                and_(UserRead.user_id == user_id, UserRead.post_id == post_id)
            )
        ).first()
        
        return user_read.read_progress if user_read else None
    
    # Analytics and statistics
    async def get_post_engagement_stats(self, post_id: UUID) -> Dict[str, Any]:
        """Get comprehensive engagement statistics for a post."""
        likes_count = await self.get_content_likes_count('post', post_id)
        bookmarks_count = await self.get_post_bookmarks_count(post_id)
        views_count = await self.get_post_views_count(post_id)
        unique_views_count = await self.get_post_unique_views_count(post_id)
        
        # Comments count
        comments_count = self.session.exec(
            select(func.count(Comment.id)).where(
                and_(Comment.post_id == post_id, Comment.status == 'approved')
            )
        ).first() or 0
        
        # Read completion rate
        total_reads = self.session.exec(
            select(func.count(UserRead.user_id)).where(UserRead.post_id == post_id)
        ).first() or 0
        
        completed_reads = self.session.exec(
            select(func.count(UserRead.user_id)).where(
                and_(UserRead.post_id == post_id, UserRead.read_progress == 100)
            )
        ).first() or 0
        
        completion_rate = (completed_reads / total_reads * 100) if total_reads > 0 else 0
        
        return {
            "likes": likes_count,
            "bookmarks": bookmarks_count,
            "comments": comments_count,
            "views": views_count,
            "unique_views": unique_views_count,
            "reads": total_reads,
            "completed_reads": completed_reads,
            "completion_rate": round(completion_rate, 2)
        }
    
    async def get_trending_posts(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending posts based on recent engagement."""
        from datetime import timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Calculate engagement score based on likes, views, and comments
        trending_posts = self.session.exec(
            select(
                Post,
                func.count(func.distinct(Like.id)).label('likes_count'),
                func.count(func.distinct(View.id)).label('views_count'),
                func.count(func.distinct(Comment.id)).label('comments_count')
            )
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
            .group_by(Post.id)
            .order_by(
                (func.count(func.distinct(Like.id)) * 3 + 
                 func.count(func.distinct(View.id)) * 1 + 
                 func.count(func.distinct(Comment.id)) * 2).desc()
            )
            .limit(limit)
        ).all()
        
        return [
            {
                "post": result[0],
                "likes_count": result[1],
                "views_count": result[2],
                "comments_count": result[3],
                "engagement_score": result[1] * 3 + result[2] * 1 + result[3] * 2
            }
            for result in trending_posts
        ]
    
    async def get_user_interaction_summary(self, user_id: UUID, post_id: UUID) -> Dict[str, Any]:
        """Get user's interaction summary with a specific post."""
        is_liked = await self.is_content_liked_by_user(user_id, 'post', post_id)
        is_bookmarked = await self.is_post_bookmarked_by_user(user_id, post_id)
        read_progress = await self.get_user_read_progress(user_id, post_id)
        
        # Check if user has viewed the post
        has_viewed = self.session.exec(
            select(View).where(
                and_(View.post_id == post_id, View.user_id == user_id)
            )
        ).first() is not None
        
        return {
            "liked": is_liked,
            "bookmarked": is_bookmarked,
            "viewed": has_viewed,
            "read_progress": read_progress
        } 