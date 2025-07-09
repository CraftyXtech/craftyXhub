"""
Web profile service for public-facing API endpoints.

Handles user profile management, preferences, and activity tracking
for the public web interface.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from models.post import Post
from models.interactions import Like, Bookmark, View
from models.comment import Comment
from schemas.web.profile import (
    UserDetailResponse, UserActivityStatsResponse, PostWithInteractionResponse,
    PaginatedPostsResponse, UserPreferencesRequest, UserPreferencesResponse,
    UserActivityResponse, UserProfileResponse, UserProfileUpdateRequest,
    UserReadingGoalsRequest, UserReadingGoalsResponse, UserCollectionRequest,
    UserCollectionResponse, UserNotificationSettingsRequest,
    UserNotificationSettingsResponse, UserPrivacySettingsRequest,
    UserPrivacySettingsResponse
)
from dependencies.pagination import PaginationParams, create_pagination_response


class WebProfileService:
    """Service for handling public web profile operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_profile(
        self,
        user_id: UUID,
        viewer: Optional[User] = None
    ) -> Optional[UserProfileResponse]:
        """
        Get complete user profile.
        
        Args:
            user_id: User ID to get profile for
            viewer: User viewing the profile (optional)
            
        Returns:
            UserProfileResponse if found, None otherwise
        """
        # Get user
        user = await self._get_user_by_id(user_id)
        if not user:
            return None
        
        # Check privacy settings
        if not await self._can_view_profile(user, viewer):
            return None
        
        # Get user details
        user_detail = await self._convert_to_user_detail(user)
        
        # Get activity statistics
        activity_stats = await self._get_user_activity_stats(user_id)
        
        # Get liked posts (limited)
        liked_posts = await self._get_user_liked_posts(user_id, PaginationParams(page=1, per_page=6))
        
        # Get bookmarked posts (limited)
        bookmarked_posts = await self._get_user_bookmarked_posts(user_id, PaginationParams(page=1, per_page=6))
        
        # Get user preferences
        preferences = await self._get_user_preferences(user_id)
        
        # Get recent activity
        recent_activity = await self._get_user_recent_activity(user_id, limit=10)
        
        # Get achievements (placeholder)
        achievements = []
        
        # Get reading goals (placeholder)
        reading_goals = {}
        
        return UserProfileResponse(
            user=user_detail,
            statistics=activity_stats,
            liked_posts=liked_posts,
            bookmarked_posts=bookmarked_posts,
            preferences=preferences,
            recent_activity=recent_activity,
            achievements=achievements,
            reading_goals=reading_goals
        )
    
    async def update_user_profile(
        self,
        user_id: UUID,
        update_data: UserProfileUpdateRequest,
        user: User
    ) -> UserDetailResponse:
        """
        Update user profile information.
        
        Args:
            user_id: User ID to update
            update_data: Profile update data
            user: User performing the update
            
        Returns:
            Updated UserDetailResponse
        """
        # Verify user can update this profile
        if user_id != user.id and user.role not in ["admin"]:
            raise ValueError("You can only update your own profile")
        
        # Get user
        target_user = await self._get_user_by_id(user_id)
        if not target_user:
            raise ValueError("User not found")
        
        # Update fields
        if update_data.name is not None:
            target_user.name = update_data.name
        if update_data.bio is not None:
            target_user.bio = update_data.bio
        if update_data.location is not None:
            target_user.location = update_data.location
        if update_data.website is not None:
            target_user.website = update_data.website
        if update_data.social_links is not None:
            target_user.social_links = update_data.social_links
        
        target_user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(target_user)
        
        return await self._convert_to_user_detail(target_user)
    
    async def get_user_liked_posts(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        viewer: Optional[User] = None
    ) -> PaginatedPostsResponse:
        """
        Get user's liked posts.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            viewer: User viewing the posts (optional)
            
        Returns:
            PaginatedPostsResponse with liked posts
        """
        # Check if viewer can see this user's liked posts
        user = await self._get_user_by_id(user_id)
        if not user or not await self._can_view_activity(user, viewer):
            return PaginatedPostsResponse(
                posts=[],
                pagination=create_pagination_response(1, pagination.per_page, 0),
                total_count=0
            )
        
        return await self._get_user_liked_posts(user_id, pagination)
    
    async def get_user_bookmarked_posts(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        viewer: Optional[User] = None
    ) -> PaginatedPostsResponse:
        """
        Get user's bookmarked posts.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            viewer: User viewing the posts (optional)
            
        Returns:
            PaginatedPostsResponse with bookmarked posts
        """
        # Check if viewer can see this user's bookmarks
        user = await self._get_user_by_id(user_id)
        if not user or not await self._can_view_activity(user, viewer):
            return PaginatedPostsResponse(
                posts=[],
                pagination=create_pagination_response(1, pagination.per_page, 0),
                total_count=0
            )
        
        return await self._get_user_bookmarked_posts(user_id, pagination)
    
    async def update_user_preferences(
        self,
        user_id: UUID,
        preferences_data: UserPreferencesRequest,
        user: User
    ) -> UserPreferencesResponse:
        """
        Update user preferences.
        
        Args:
            user_id: User ID to update preferences for
            preferences_data: Preferences update data
            user: User performing the update
            
        Returns:
            Updated UserPreferencesResponse
        """
        # Verify user can update these preferences
        if user_id != user.id:
            raise ValueError("You can only update your own preferences")
        
        # Update preferences (this would typically be stored in a separate table)
        # For now, we'll store in user metadata or a separate preferences table
        
        # TODO: Implement actual preferences storage
        
        return UserPreferencesResponse(
            newsletter_enabled=preferences_data.newsletter_enabled or True,
            personalization_enabled=preferences_data.personalization_enabled or True,
            preferred_categories=[],
            content_recommendations=preferences_data.content_recommendations or True,
            email_notifications=preferences_data.email_notifications or True,
            reading_reminders=preferences_data.reading_reminders or False,
            dark_mode=preferences_data.dark_mode or False,
            language=preferences_data.language or "en",
            timezone=preferences_data.timezone or "UTC",
            privacy_settings=preferences_data.privacy_settings or {},
            last_updated=datetime.utcnow()
        )
    
    async def get_user_activity_history(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        viewer: Optional[User] = None
    ) -> List[UserActivityResponse]:
        """
        Get user's activity history.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            viewer: User viewing the activity (optional)
            
        Returns:
            List of UserActivityResponse
        """
        # Check if viewer can see this user's activity
        user = await self._get_user_by_id(user_id)
        if not user or not await self._can_view_activity(user, viewer):
            return []
        
        return await self._get_user_recent_activity(user_id, pagination.limit, pagination.offset)
    
    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _can_view_profile(self, user: User, viewer: Optional[User]) -> bool:
        """Check if viewer can view user's profile."""
        # TODO: Implement privacy settings check
        return True
    
    async def _can_view_activity(self, user: User, viewer: Optional[User]) -> bool:
        """Check if viewer can view user's activity."""
        # TODO: Implement privacy settings check
        return True
    
    async def _convert_to_user_detail(self, user: User) -> UserDetailResponse:
        """Convert user model to detail response."""
        return UserDetailResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            avatar=user.avatar,
            bio=user.bio,
            joined_at=user.created_at,
            role=user.role,
            is_verified=user.email_verified_at is not None,
            social_links=getattr(user, 'social_links', {}),
            location=getattr(user, 'location', None),
            website=getattr(user, 'website', None)
        )
    
    async def _get_user_activity_stats(self, user_id: UUID) -> UserActivityStatsResponse:
        """Get user activity statistics."""
        # Get posts count
        posts_query = select(func.count(Post.id)).where(Post.user_id == user_id)
        posts_count = await self.db.scalar(posts_query) or 0
        
        # Get likes count
        likes_query = select(func.count(Like.id)).where(Like.user_id == user_id)
        likes_count = await self.db.scalar(likes_query) or 0
        
        # Get bookmarks count
        bookmarks_query = select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        bookmarks_count = await self.db.scalar(bookmarks_query) or 0
        
        # Get comments count
        comments_query = select(func.count(Comment.id)).where(Comment.user_id == user_id)
        comments_count = await self.db.scalar(comments_query) or 0
        
        # Get views count (posts viewed by user)
        views_query = select(func.count(View.id)).where(View.user_id == user_id)
        views_count = await self.db.scalar(views_query) or 0
        
        # Calculate member since days
        user = await self._get_user_by_id(user_id)
        member_since_days = (datetime.utcnow() - user.created_at).days if user else 0
        
        # Determine engagement level
        total_interactions = likes_count + bookmarks_count + comments_count
        if total_interactions > 100:
            engagement_level = "high"
        elif total_interactions > 20:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        return UserActivityStatsResponse(
            posts_count=posts_count,
            likes_count=likes_count,
            bookmarks_count=bookmarks_count,
            comments_count=comments_count,
            views_count=views_count,
            reading_streak=0,  # TODO: Implement reading streak
            total_reading_time=0,  # TODO: Implement reading time tracking
            favorite_categories=[],  # TODO: Implement favorite categories
            engagement_level=engagement_level,
            last_activity=None,  # TODO: Implement last activity tracking
            member_since_days=member_since_days
        )
    
    async def _get_user_liked_posts(
        self,
        user_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedPostsResponse:
        """Get user's liked posts."""
        # Get liked posts with pagination
        query = select(Like).where(Like.user_id == user_id).options(
            selectinload(Like.post).selectinload(Post.author),
            selectinload(Like.post).selectinload(Post.category),
            selectinload(Like.post).selectinload(Post.tags)
        ).order_by(desc(Like.created_at))
        
        # Get total count
        count_query = select(func.count(Like.id)).where(Like.user_id == user_id)
        total_count = await self.db.scalar(count_query) or 0
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await self.db.execute(query)
        likes = result.scalars().all()
        
        # Convert to response format
        posts = []
        for like in likes:
            post_response = await self._convert_to_post_with_interaction(
                like.post, like.created_at, "like"
            )
            posts.append(post_response)
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        return PaginatedPostsResponse(
            posts=posts,
            pagination=pagination_response,
            total_count=total_count
        )
    
    async def _get_user_bookmarked_posts(
        self,
        user_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedPostsResponse:
        """Get user's bookmarked posts."""
        # Get bookmarked posts with pagination
        query = select(Bookmark).where(Bookmark.user_id == user_id).options(
            selectinload(Bookmark.post).selectinload(Post.author),
            selectinload(Bookmark.post).selectinload(Post.category),
            selectinload(Bookmark.post).selectinload(Post.tags)
        ).order_by(desc(Bookmark.created_at))
        
        # Get total count
        count_query = select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        total_count = await self.db.scalar(count_query) or 0
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await self.db.execute(query)
        bookmarks = result.scalars().all()
        
        # Convert to response format
        posts = []
        for bookmark in bookmarks:
            post_response = await self._convert_to_post_with_interaction(
                bookmark.post, bookmark.created_at, "bookmark"
            )
            posts.append(post_response)
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        return PaginatedPostsResponse(
            posts=posts,
            pagination=pagination_response,
            total_count=total_count
        )
    
    async def _get_user_preferences(self, user_id: UUID) -> UserPreferencesResponse:
        """Get user preferences."""
        # TODO: Implement actual preferences retrieval
        return UserPreferencesResponse(
            newsletter_enabled=True,
            personalization_enabled=True,
            preferred_categories=[],
            content_recommendations=True,
            email_notifications=True,
            reading_reminders=False,
            dark_mode=False,
            language="en",
            timezone="UTC",
            privacy_settings={},
            last_updated=datetime.utcnow()
        )
    
    async def _get_user_recent_activity(
        self,
        user_id: UUID,
        limit: int = 10,
        offset: int = 0
    ) -> List[UserActivityResponse]:
        """Get user's recent activity."""
        activities = []
        
        # Get recent likes
        likes_query = select(Like).where(Like.user_id == user_id).options(
            selectinload(Like.post)
        ).order_by(desc(Like.created_at)).limit(limit)
        
        likes_result = await self.db.execute(likes_query)
        likes = likes_result.scalars().all()
        
        for like in likes:
            if like.post:
                activity = UserActivityResponse(
                    id=like.id,
                    activity_type="like",
                    post=await self._convert_to_post_summary(like.post),
                    created_at=like.created_at,
                    metadata={},
                    is_public=True
                )
                activities.append(activity)
        
        # Get recent bookmarks
        bookmarks_query = select(Bookmark).where(Bookmark.user_id == user_id).options(
            selectinload(Bookmark.post)
        ).order_by(desc(Bookmark.created_at)).limit(limit)
        
        bookmarks_result = await self.db.execute(bookmarks_query)
        bookmarks = bookmarks_result.scalars().all()
        
        for bookmark in bookmarks:
            if bookmark.post:
                activity = UserActivityResponse(
                    id=bookmark.id,
                    activity_type="bookmark",
                    post=await self._convert_to_post_summary(bookmark.post),
                    created_at=bookmark.created_at,
                    metadata={},
                    is_public=True
                )
                activities.append(activity)
        
        # Sort by created_at descending
        activities.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply offset and limit
        return activities[offset:offset + limit]
    
    async def _convert_to_post_with_interaction(
        self,
        post: Post,
        interaction_date: datetime,
        interaction_type: str
    ) -> PostWithInteractionResponse:
        """Convert post to post with interaction response."""
        from schemas.web.posts import PostSummaryResponse
        
        post_summary = await self._convert_to_post_summary(post)
        
        return PostWithInteractionResponse(
            post=post_summary,
            interaction_date=interaction_date,
            interaction_type=interaction_type,
            reading_status=None,
            notes=None,
            tags_added=[]
        )
    
    async def _convert_to_post_summary(self, post: Post) -> "PostSummaryResponse":
        """Convert post to summary response."""
        from schemas.web.posts import PostSummaryResponse, AuthorSummaryResponse
        
        author_response = AuthorSummaryResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar,
            bio=post.author.bio,
            role=post.author.role
        )
        
        return PostSummaryResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            featured_image_path=post.generated_image_path,
            published_at=post.published_at,
            reading_time=self._calculate_reading_time(post.body),
            author=author_response,
            category=None,  # TODO: Convert category if needed
            tags=[],  # TODO: Convert tags if needed
            interaction_counts=None  # TODO: Get interaction counts if needed
        )
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        if not content:
            return 0
        
        # Average reading speed: 200 words per minute
        words = len(content.split())
        reading_time = max(1, round(words / 200))
        return reading_time 