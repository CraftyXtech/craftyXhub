"""
Web post service for public-facing API endpoints.

Handles post listing, viewing, search, and related functionality
for the public web interface.
"""

import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.post import Post
from models.user import User
from models.category import Category
from models.tag import Tag
from models.comment import Comment
from models.interactions import Like, Bookmark
from schemas.web.posts import (
    PostListFilters, PostSummaryResponse, PostListResponse,
    PostDetailResponse, CategoryWithCountResponse, SEODataResponse,
    RelatedPostResponse, PostSearchResponse, SearchSuggestionResponse
)
from dependencies.pagination import PaginationParams, create_pagination_response


class WebPostService:
    """Service for handling public web post operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_posts_list(
        self,
        filters: PostListFilters,
        pagination: PaginationParams,
        user: Optional[User] = None
    ) -> PostListResponse:
        """
        Get paginated list of published posts with filtering and search.
        
        Args:
            filters: Post list filters
            pagination: Pagination parameters
            user: Current user (optional)
            
        Returns:
            PostListResponse with posts and metadata
        """
        # Build base query for published posts
        query = select(Post).where(
            and_(
                Post.status == "published",
                Post.published_at.isnot(None)
            )
        ).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.comments)
        )
        
        # Apply search filter
        if filters.q:
            search_vector = func.to_tsvector('english', Post.title + ' ' + Post.body)
            search_query = func.plainto_tsquery('english', filters.q)
            query = query.where(search_vector.match(search_query))
        
        # Apply category filter
        if filters.category:
            query = query.join(Category).where(Category.slug == filters.category)
        
        # Apply tag filter
        if filters.tag:
            query = query.join(Post.tags).where(Tag.slug == filters.tag)
        
        # Apply sorting
        sort_column = getattr(Post, filters.sort_by, Post.published_at)
        if filters.sort_direction == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.db.scalar(count_query)
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await self.db.execute(query)
        posts = result.scalars().all()
        
        # Convert to response format
        post_responses = []
        for post in posts:
            post_response = await self._convert_to_summary_response(post, user)
            post_responses.append(post_response)
        
        # Get categories with counts
        categories = await self._get_categories_with_counts()
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        return PostListResponse(
            posts=post_responses,
            pagination=pagination_response,
            categories=categories,
            filters=filters,
            total_count=total_count
        )
    
    async def get_post_by_slug(
        self,
        slug: str,
        user: Optional[User] = None
    ) -> Optional[PostDetailResponse]:
        """
        Get detailed post by slug.
        
        Args:
            slug: Post slug
            user: Current user (optional)
            
        Returns:
            PostDetailResponse if found, None otherwise
        """
        # Get post with all relationships
        query = select(Post).where(
            and_(
                Post.slug == slug,
                Post.status == "published",
                Post.published_at.isnot(None)
            )
        ).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
            selectinload(Post.comments).selectinload(Comment.user)
        )
        
        result = await self.db.execute(query)
        post = result.scalar_one_or_none()
        
        if not post:
            return None
        
        # Track view if user provided
        if user:
            await self._track_post_view(post.id, user.id)
        
        # Get related posts
        related_posts = await self._get_related_posts(post, limit=5)
        
        # Build response
        return await self._convert_to_detail_response(post, user, related_posts)
    
    async def search_posts(
        self,
        query: str,
        filters: Dict[str, Any],
        pagination: PaginationParams,
        user: Optional[User] = None
    ) -> PostSearchResponse:
        """
        Advanced post search with analytics.
        
        Args:
            query: Search query
            filters: Additional filters
            pagination: Pagination parameters
            user: Current user (optional)
            
        Returns:
            PostSearchResponse with results and metadata
        """
        start_time = time.time()
        
        # Build search query
        search_query = select(Post).where(
            and_(
                Post.status == "published",
                Post.published_at.isnot(None)
            )
        ).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )
        
        # Apply full-text search
        if query:
            search_vector = func.to_tsvector('english', Post.title + ' ' + Post.body)
            search_tsquery = func.plainto_tsquery('english', query)
            search_query = search_query.where(search_vector.match(search_tsquery))
        
        # Apply additional filters
        if filters.get('category'):
            search_query = search_query.join(Category).where(Category.slug == filters['category'])
        
        if filters.get('tag'):
            search_query = search_query.join(Post.tags).where(Tag.slug == filters['tag'])
        
        # Get total count
        count_query = select(func.count()).select_from(search_query.subquery())
        total_count = await self.db.scalar(count_query)
        
        # Apply pagination
        search_query = search_query.offset(pagination.offset).limit(pagination.limit)
        
        # Execute query
        result = await self.db.execute(search_query)
        posts = result.scalars().all()
        
        # Convert to response format
        post_responses = []
        for post in posts:
            post_response = await self._convert_to_summary_response(post, user)
            post_responses.append(post_response)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Create pagination response
        pagination_response = create_pagination_response(
            pagination.page, pagination.per_page, total_count
        )
        
        # Get search suggestions
        suggestions = await self._get_search_suggestions(query)
        
        return PostSearchResponse(
            posts=post_responses,
            pagination=pagination_response,
            search_query=query,
            search_results_count=total_count,
            search_time=search_time,
            filters_applied=filters,
            suggestions=suggestions
        )
    
    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 10
    ) -> SearchSuggestionResponse:
        """
        Get search suggestions for a query.
        
        Args:
            query: Search query
            limit: Maximum suggestions to return
            
        Returns:
            SearchSuggestionResponse with suggestions
        """
        suggestions = await self._get_search_suggestions(query, limit)
        popular_searches = await self._get_popular_searches(limit)
        category_suggestions = await self._get_category_suggestions(query, limit)
        tag_suggestions = await self._get_tag_suggestions(query, limit)
        
        return SearchSuggestionResponse(
            query=query,
            suggestions=suggestions,
            popular_searches=popular_searches,
            category_suggestions=category_suggestions,
            tag_suggestions=tag_suggestions
        )
    
    async def _convert_to_summary_response(
        self,
        post: Post,
        user: Optional[User] = None
    ) -> PostSummaryResponse:
        """Convert post model to summary response."""
        from schemas.web.posts import (
            AuthorSummaryResponse, CategorySummaryResponse,
            TagSummaryResponse, InteractionCountsResponse
        )
        
        # Get interaction counts
        interaction_counts = await self._get_interaction_counts(post.id)
        
        # Build author response
        author_response = AuthorSummaryResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar,
            bio=post.author.bio,
            role=post.author.role
        )
        
        # Build category response
        category_response = None
        if post.category:
            category_response = CategorySummaryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            )
        
        # Build tag responses
        tag_responses = []
        for tag in post.tags:
            tag_response = TagSummaryResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
                description=tag.description
            )
            tag_responses.append(tag_response)
        
        return PostSummaryResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            featured_image_path=post.generated_image_path,
            published_at=post.published_at,
            reading_time=self._calculate_reading_time(post.body),
            author=author_response,
            category=category_response,
            tags=tag_responses,
            interaction_counts=interaction_counts
        )
    
    async def _convert_to_detail_response(
        self,
        post: Post,
        user: Optional[User] = None,
        related_posts: List[Post] = None
    ) -> PostDetailResponse:
        """Convert post model to detailed response."""
        from schemas.web.posts import (
            AuthorSummaryResponse, CategorySummaryResponse,
            TagSummaryResponse, InteractionCountsResponse,
            CommentThreadResponse, UserInteractionStatusResponse
        )
        
        # Get interaction counts
        interaction_counts = await self._get_interaction_counts(post.id)
        
        # Build author response
        author_response = AuthorSummaryResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar,
            bio=post.author.bio,
            role=post.author.role
        )
        
        # Build category response
        category_response = None
        if post.category:
            category_response = CategorySummaryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            )
        
        # Build tag responses
        tag_responses = []
        for tag in post.tags:
            tag_response = TagSummaryResponse(
                id=tag.id,
                name=tag.name,
                slug=tag.slug,
                description=tag.description
            )
            tag_responses.append(tag_response)
        
        # Build comment threads
        comment_threads = await self._build_comment_threads(post.comments)
        
        # Build related posts
        related_post_responses = []
        if related_posts:
            for related_post in related_posts:
                related_response = await self._convert_to_related_response(related_post)
                related_post_responses.append(related_response)
        
        # Build user interaction status
        interaction_status = None
        if user:
            interaction_status = await self._get_user_interaction_status(post.id, user.id)
        
        # Build SEO data
        seo_data = SEODataResponse(
            meta_title=post.title,
            meta_description=post.excerpt or post.title,
            canonical_url=f"/posts/{post.slug}",
            og_title=post.title,
            og_description=post.excerpt or post.title,
            og_image=post.generated_image_path,
            twitter_title=post.title,
            twitter_description=post.excerpt or post.title,
            twitter_image=post.generated_image_path
        )
        
        return PostDetailResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            body=post.body,
            excerpt=post.excerpt,
            featured_image_path=post.generated_image_path,
            meta_description=post.excerpt,
            published_at=post.published_at,
            updated_at=post.updated_at,
            reading_time=self._calculate_reading_time(post.body),
            view_count=0,  # TODO: Implement view counting
            author=author_response,
            category=category_response,
            tags=tag_responses,
            comments=comment_threads,
            related_posts=related_post_responses,
            interaction_counts=interaction_counts,
            interaction_status=interaction_status,
            seo_data=seo_data
        )
    
    async def _get_interaction_counts(self, post_id: UUID) -> "InteractionCountsResponse":
        """Get interaction counts for a post."""
        from schemas.web.posts import InteractionCountsResponse
        
        # Get likes count
        likes_query = select(func.count(Like.id)).where(Like.post_id == post_id)
        likes_count = await self.db.scalar(likes_query) or 0
        
        # Get bookmarks count
        bookmarks_query = select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        bookmarks_count = await self.db.scalar(bookmarks_query) or 0
        
        # Get comments count
        comments_query = select(func.count(Comment.id)).where(Comment.post_id == post_id)
        comments_count = await self.db.scalar(comments_query) or 0
        
        return InteractionCountsResponse(
            likes_count=likes_count,
            bookmarks_count=bookmarks_count,
            comments_count=comments_count,
            views_count=0  # TODO: Implement view counting
        )
    
    async def _get_categories_with_counts(self) -> List[CategoryWithCountResponse]:
        """Get categories with post counts."""
        query = select(
            Category.id,
            Category.name,
            Category.slug,
            Category.description,
            func.count(Post.id).label('posts_count')
        ).select_from(
            Category
        ).outerjoin(
            Post,
            and_(
                Post.category_id == Category.id,
                Post.status == "published",
                Post.published_at.isnot(None)
            )
        ).group_by(
            Category.id, Category.name, Category.slug, Category.description
        ).order_by(Category.name)
        
        result = await self.db.execute(query)
        categories = result.all()
        
        category_responses = []
        for category in categories:
            category_response = CategoryWithCountResponse(
                id=category.id,
                name=category.name,
                slug=category.slug,
                posts_count=category.posts_count,
                description=category.description
            )
            category_responses.append(category_response)
        
        return category_responses
    
    async def _get_related_posts(
        self,
        post: Post,
        limit: int = 5
    ) -> List[Post]:
        """Get related posts based on category and tags."""
        # Get posts from same category or with similar tags
        query = select(Post).where(
            and_(
                Post.id != post.id,
                Post.status == "published",
                Post.published_at.isnot(None),
                or_(
                    Post.category_id == post.category_id,
                    Post.tags.any(Tag.id.in_([tag.id for tag in post.tags]))
                )
            )
        ).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        ).order_by(desc(Post.published_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        if not content:
            return 0
        
        # Average reading speed: 200 words per minute
        words = len(content.split())
        reading_time = max(1, round(words / 200))
        return reading_time
    
    async def _track_post_view(self, post_id: UUID, user_id: UUID):
        """Track post view for analytics."""
        # TODO: Implement view tracking
        pass
    
    async def _build_comment_threads(self, comments: List[Comment]) -> List["CommentThreadResponse"]:
        """Build threaded comment structure."""
        # TODO: Implement comment threading
        return []
    
    async def _convert_to_related_response(self, post: Post) -> RelatedPostResponse:
        """Convert post to related post response."""
        from schemas.web.posts import AuthorSummaryResponse, CategorySummaryResponse
        
        author_response = AuthorSummaryResponse(
            id=post.author.id,
            name=post.author.name,
            avatar=post.author.avatar,
            bio=post.author.bio,
            role=post.author.role
        )
        
        category_response = None
        if post.category:
            category_response = CategorySummaryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            )
        
        return RelatedPostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            featured_image_path=post.generated_image_path,
            published_at=post.published_at,
            reading_time=self._calculate_reading_time(post.body),
            author=author_response,
            category=category_response
        )
    
    async def _get_user_interaction_status(
        self,
        post_id: UUID,
        user_id: UUID
    ) -> "UserInteractionStatusResponse":
        """Get user's interaction status with a post."""
        from schemas.web.posts import UserInteractionStatusResponse
        
        # Check if user has liked the post
        like_query = select(Like).where(
            and_(Like.post_id == post_id, Like.user_id == user_id)
        )
        has_liked = await self.db.scalar(like_query) is not None
        
        # Check if user has bookmarked the post
        bookmark_query = select(Bookmark).where(
            and_(Bookmark.post_id == post_id, Bookmark.user_id == user_id)
        )
        has_bookmarked = await self.db.scalar(bookmark_query) is not None
        
        return UserInteractionStatusResponse(
            can_like=True,
            can_bookmark=True,
            can_comment=True,
            has_liked=has_liked,
            has_bookmarked=has_bookmarked
        )
    
    async def _get_search_suggestions(
        self,
        query: str,
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions based on query."""
        # TODO: Implement search suggestions
        return []
    
    async def _get_popular_searches(self, limit: int = 10) -> List[str]:
        """Get popular search queries."""
        # TODO: Implement popular searches tracking
        return []
    
    async def _get_category_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List["CategorySummaryResponse"]:
        """Get category suggestions based on query."""
        # TODO: Implement category suggestions
        return []
    
    async def _get_tag_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List["TagSummaryResponse"]:
        """Get tag suggestions based on query."""
        # TODO: Implement tag suggestions
        return [] 