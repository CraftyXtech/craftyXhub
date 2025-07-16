

from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload

from models.post import Post
from models.user import User
from models.category import Category
from models.tag import Tag
from models.interactions import Like, Bookmark, View
from models.comment import Comment
from schemas.post import (
    PostListQuery, 
    PostSummaryResponse, 
    PostDetailResponse, 
    PaginationMeta,
    PaginatedPostsResponse,
    AuthorResponse,
    CategoryResponse,
    TagResponse,
    PostStatsResponse
)


class PostService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_published_posts(
        self, 
        query: PostListQuery,
        current_user: Optional[User] = None
    ) -> PaginatedPostsResponse:
        """
        Get paginated list of published posts with filtering and search.
        
        Args:
            query: Query parameters for filtering and pagination
            current_user: Optional authenticated user for interaction status
            
        Returns:
            PaginatedPostsResponse with posts and pagination metadata
        """
        # Build base query for published posts only
        base_query = select(Post).where(
            and_(
                Post.status == "published",
                Post.published_at.is_not(None)
            )
        )

        # Apply category filter
        if query.category:
            category_subquery = select(Category.id).where(Category.slug == query.category)
            base_query = base_query.where(Post.category_id.in_(category_subquery))

        # Apply search filter
        if query.search:
            search_term = f"%{query.search}%"
            # Search across title, excerpt, body, and related tags/categories
            search_conditions = or_(
                Post.title.ilike(search_term),
                Post.excerpt.ilike(search_term),
                Post.body.ilike(search_term)
            )
            base_query = base_query.where(search_conditions)

        # Apply sorting
        if query.sort_by == "published_at":
            sort_column = Post.published_at
        elif query.sort_by == "created_at":
            sort_column = Post.created_at
        elif query.sort_by == "title":
            sort_column = Post.title
        else:
            sort_column = Post.published_at

        if query.sort_direction == "desc":
            base_query = base_query.order_by(desc(sort_column))
        else:
            base_query = base_query.order_by(asc(sort_column))

        # Get total count for pagination
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (query.page - 1) * query.per_page
        posts_query = base_query.options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        ).offset(offset).limit(query.per_page)

        # Execute query
        result = await self.db.execute(posts_query)
        posts = result.scalars().all()

        # Get interaction counts for each post
        post_summaries = []
        for post in posts:
            # Get like count
            like_count_query = select(func.count(Like.id)).where(Like.post_id == post.id)
            like_count_result = await self.db.execute(like_count_query)
            like_count = like_count_result.scalar() or 0

            # Get view count
            view_count_query = select(func.count(View.id)).where(View.post_id == post.id)
            view_count_result = await self.db.execute(view_count_query)
            view_count = view_count_result.scalar() or 0

            # Create response object
            post_summary = PostSummaryResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                featured_image_path=post.generated_image_path,
                published_at=post.published_at,
                author=AuthorResponse(
                    id=post.author.id,
                    name=post.author.name,
                    avatar=post.author.avatar
                ),
                category=CategoryResponse(
                    id=post.category.id,
                    name=post.category.name,
                    slug=post.category.slug,
                    description=post.category.description
                ) if post.category else None,
                tags=[
                    TagResponse(
                        id=tag.id,
                        name=tag.name,
                        slug=tag.slug
                    ) for tag in post.tags
                ],
                like_count=like_count,
                view_count=view_count,
                difficulty_level=post.difficulty_level,
                estimated_reading_time=self._calculate_reading_time(post.body)
            )
            post_summaries.append(post_summary)

        # Create pagination metadata
        pagination = PaginationMeta(
            page=query.page,
            per_page=query.per_page,
            total=total,
            total_pages=(total + query.per_page - 1) // query.per_page,
            has_next=query.page * query.per_page < total,
            has_prev=query.page > 1
        )

        # Create applied filters dict
        filters = {
            "category": query.category,
            "search": query.search,
            "sort_by": query.sort_by,
            "sort_direction": query.sort_direction
        }

        return PaginatedPostsResponse(
            data=post_summaries,
            pagination=pagination,
            filters=filters
        )

    async def get_post_by_id(
        self, 
        post_id: UUID,
        current_user: Optional[User] = None
    ) -> Optional[PostDetailResponse]:
        """
        Get individual post details with interaction status.
        
        Args:
            post_id: UUID of the post to retrieve
            current_user: Optional authenticated user for interaction status
            
        Returns:
            PostDetailResponse if found and published, None otherwise
        """
        # Query for published post only
        query = select(Post).where(
            and_(
                Post.id == post_id,
                Post.status == "published",
                Post.published_at.is_not(None)
            )
        ).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )

        result = await self.db.execute(query)
        post = result.scalar_one_or_none()

        if not post:
            return None

        # Get interaction counts
        like_count_query = select(func.count(Like.id)).where(Like.post_id == post.id)
        like_count_result = await self.db.execute(like_count_query)
        like_count = like_count_result.scalar() or 0

        view_count_query = select(func.count(View.id)).where(View.post_id == post.id)
        view_count_result = await self.db.execute(view_count_query)
        view_count = view_count_result.scalar() or 0

        # Check user interaction status if authenticated
        is_liked = None
        is_bookmarked = None
        if current_user:
            # Check if user liked the post
            like_query = select(Like).where(
                and_(Like.post_id == post.id, Like.user_id == current_user.id)
            )
            like_result = await self.db.execute(like_query)
            is_liked = like_result.scalar_one_or_none() is not None

            # Check if user bookmarked the post
            bookmark_query = select(Bookmark).where(
                and_(Bookmark.post_id == post.id, Bookmark.user_id == current_user.id)
            )
            bookmark_result = await self.db.execute(bookmark_query)
            is_bookmarked = bookmark_result.scalar_one_or_none() is not None

        # Create response object
        post_detail = PostDetailResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            body=post.body,
            excerpt=post.excerpt,
            featured_image_path=post.generated_image_path,
            published_at=post.published_at,
            author=AuthorResponse(
                id=post.author.id,
                name=post.author.name,
                avatar=post.author.avatar
            ),
            category=CategoryResponse(
                id=post.category.id,
                name=post.category.name,
                slug=post.category.slug,
                description=post.category.description
            ) if post.category else None,
            tags=[
                TagResponse(
                    id=tag.id,
                    name=tag.name,
                    slug=tag.slug
                ) for tag in post.tags
            ],
            like_count=like_count,
            view_count=view_count,
            is_liked=is_liked,
            is_bookmarked=is_bookmarked,
            comments_enabled=post.comments_enabled,
            difficulty_level=post.difficulty_level,
            estimated_reading_time=self._calculate_reading_time(post.body),
            created_at=post.created_at,
            updated_at=post.updated_at
        )

        return post_detail

    async def get_post_stats(self, post_id: UUID) -> Optional[PostStatsResponse]:
        """
        Get detailed statistics for a post.
        
        Args:
            post_id: UUID of the post
            
        Returns:
            PostStatsResponse if post exists, None otherwise
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
            return None

        # Get various counts
        like_count_query = select(func.count(Like.id)).where(Like.post_id == post_id)
        like_count_result = await self.db.execute(like_count_query)
        like_count = like_count_result.scalar() or 0

        view_count_query = select(func.count(View.id)).where(View.post_id == post_id)
        view_count_result = await self.db.execute(view_count_query)
        view_count = view_count_result.scalar() or 0

        bookmark_count_query = select(func.count(Bookmark.id)).where(Bookmark.post_id == post_id)
        bookmark_count_result = await self.db.execute(bookmark_count_query)
        bookmark_count = bookmark_count_result.scalar() or 0

        comment_count_query = select(func.count(Comment.id)).where(
            and_(Comment.post_id == post_id, Comment.approved == True)
        )
        comment_count_result = await self.db.execute(comment_count_query)
        comment_count = comment_count_result.scalar() or 0

        # Get latest interaction timestamps
        latest_view_query = select(func.max(View.created_at)).where(View.post_id == post_id)
        latest_view_result = await self.db.execute(latest_view_query)
        last_viewed_at = latest_view_result.scalar()

        latest_like_query = select(func.max(Like.created_at)).where(Like.post_id == post_id)
        latest_like_result = await self.db.execute(latest_like_query)
        last_liked_at = latest_like_result.scalar()

        return PostStatsResponse(
            post_id=post_id,
            like_count=like_count,
            view_count=view_count,
            comment_count=comment_count,
            bookmark_count=bookmark_count,
            share_count=0,  # To be implemented later
            last_viewed_at=last_viewed_at,
            last_liked_at=last_liked_at
        )

    async def search_posts(
        self,
        search_term: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[PostSummaryResponse]:
        """
        Advanced search functionality for posts.
        
        Args:
            search_term: Search query
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of matching posts
        """
        # Build search query
        search_conditions = or_(
            Post.title.ilike(f"%{search_term}%"),
            Post.excerpt.ilike(f"%{search_term}%"),
            Post.body.ilike(f"%{search_term}%")
        )

        query = select(Post).where(
            and_(
                Post.status == "published",
                Post.published_at.is_not(None),
                search_conditions
            )
        )

        # Apply category filter if provided
        if category:
            category_subquery = select(Category.id).where(Category.slug == category)
            query = query.where(Post.category_id.in_(category_subquery))

        # Order by relevance (could be enhanced with full-text search)
        query = query.order_by(desc(Post.published_at)).limit(limit)

        # Load relationships
        query = query.options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )

        result = await self.db.execute(query)
        posts = result.scalars().all()

        # Convert to response objects
        post_summaries = []
        for post in posts:
            # Get interaction counts (simplified for search)
            like_count_query = select(func.count(Like.id)).where(Like.post_id == post.id)
            like_count_result = await self.db.execute(like_count_query)
            like_count = like_count_result.scalar() or 0

            view_count_query = select(func.count(View.id)).where(View.post_id == post.id)
            view_count_result = await self.db.execute(view_count_query)
            view_count = view_count_result.scalar() or 0

            post_summary = PostSummaryResponse(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                featured_image_path=post.generated_image_path,
                published_at=post.published_at,
                author=AuthorResponse(
                    id=post.author.id,
                    name=post.author.name,
                    avatar=post.author.avatar
                ),
                category=CategoryResponse(
                    id=post.category.id,
                    name=post.category.name,
                    slug=post.category.slug,
                    description=post.category.description
                ) if post.category else None,
                tags=[
                    TagResponse(
                        id=tag.id,
                        name=tag.name,
                        slug=tag.slug
                    ) for tag in post.tags
                ],
                like_count=like_count,
                view_count=view_count,
                difficulty_level=post.difficulty_level,
                estimated_reading_time=self._calculate_reading_time(post.body)
            )
            post_summaries.append(post_summary)

        return post_summaries

    def _calculate_reading_time(self, content: str) -> int:
        """
        Calculate estimated reading time in minutes.
        
        Args:
            content: Post content
            
        Returns:
            Estimated reading time in minutes
        """
        if not content:
            return 0
        
        # Average reading speed is 200-250 words per minute
        words_per_minute = 225
        word_count = len(content.split())
        reading_time = max(1, round(word_count / words_per_minute))
        
        return reading_time 