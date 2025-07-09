"""
Posts API Router for CraftyXhub

API endpoints for post management following SubPRD-PostAPI.md specifications.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import optional_authentication
from models.user import User
from schemas.post import (
    PostListQuery,
    PostDetailResponse,
    PaginatedPostsResponse,
    PostStatsResponse,
    PostViewRequest
)
from services.posts import PostService, ViewTrackingService


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get(
    "",
    response_model=PaginatedPostsResponse,
    status_code=status.HTTP_200_OK,
    summary="List Published Posts",
    description="Get paginated list of published posts with filtering and search capabilities"
)
async def list_posts(
    category: Optional[str] = Query(None, description="Category slug for filtering"),
    search: Optional[str] = Query(None, description="Search term for title, excerpt, content, and tags"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(9, ge=1, le=50, description="Number of posts per page (max 50)"),
    sort_by: str = Query("published_at", description="Field to sort by"),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PaginatedPostsResponse:
    """
    Get paginated list of published posts.
    
    - **category**: Filter by category slug
    - **search**: Search across title, excerpt, content, and tags
    - **page**: Page number (default: 1)
    - **per_page**: Posts per page (default: 9, max: 50)
    - **sort_by**: Sort field (published_at, created_at, title, like_count, view_count)
    - **sort_direction**: Sort direction (asc, desc)
    
    Returns paginated list of published posts with author, category, and tags.
    Only posts with status='published' and published_at is not null are returned.
    """
    # Create query object
    query = PostListQuery(
        category=category,
        search=search,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    # Get posts using service
    post_service = PostService(db)
    try:
        posts_response = await post_service.get_published_posts(query, current_user)
        return posts_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve posts"
        )


@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Post Details",
    description="Get individual post details with view tracking and interaction status"
)
async def get_post(
    post_id: UUID,
    request: Request,
    view_request: PostViewRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PostDetailResponse:
    """
    Get individual post details with automatic view tracking.
    
    - **post_id**: UUID of the post to retrieve
    
    Returns full post details including:
    - Complete post content
    - Author information
    - Category and tags
    - Like and view counts
    - User interaction status (if authenticated)
    - Comments enabled status
    - Estimated reading time
    
    Automatically tracks the view with IP address, user agent, and user ID if authenticated.
    Returns 404 for non-existent or unpublished posts.
    """
    # Get post details
    post_service = PostService(db)
    post = await post_service.get_post_by_id(post_id, current_user)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Track the view
    view_service = ViewTrackingService(db)
    try:
        # Get IP address from request
        ip_address = request.client.host if request.client else "unknown"
        
        # Get user agent from headers
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Get referrer from headers
        referrer = request.headers.get("referer")
        
        # Track the view (fire and forget, don't fail if tracking fails)
        await view_service.track_view(
            post_id=post_id,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=current_user.id if current_user else None,
            referrer=referrer
        )
    except Exception:
        # View tracking failure shouldn't prevent post retrieval
        pass
    
    return post


@router.get(
    "/{post_id}/stats",
    response_model=PostStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Post Statistics",
    description="Get detailed statistics for a post including engagement metrics"
)
async def get_post_stats(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PostStatsResponse:
    """
    Get detailed statistics for a post.
    
    - **post_id**: UUID of the post
    
    Returns detailed statistics including:
    - Like count
    - View count
    - Comment count
    - Bookmark count
    - Share count
    - Latest interaction timestamps
    
    Returns 404 for non-existent or unpublished posts.
    """
    post_service = PostService(db)
    stats = await post_service.get_post_stats(post_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return stats


@router.get(
    "/search/advanced",
    response_model=list[PostDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Advanced Post Search",
    description="Advanced search functionality with enhanced filtering options"
)
async def search_posts(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Category slug filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> list[PostDetailResponse]:
    """
    Advanced search for posts with enhanced filtering.
    
    - **q**: Search query (minimum 2 characters)
    - **category**: Optional category filter by slug
    - **limit**: Maximum number of results (default: 10, max: 50)
    
    Searches across:
    - Post title
    - Post excerpt
    - Post content
    - Tag names
    - Category names
    
    Returns list of matching posts ordered by relevance.
    """
    post_service = PostService(db)
    try:
        posts = await post_service.search_posts(
            search_term=q,
            category=category,
            limit=limit
        )
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get(
    "/category/{category_slug}",
    response_model=PaginatedPostsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Posts by Category",
    description="Get paginated posts filtered by category slug"
)
async def get_posts_by_category(
    category_slug: str,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(9, ge=1, le=50, description="Number of posts per page (max 50)"),
    sort_by: str = Query("published_at", description="Field to sort by"),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PaginatedPostsResponse:
    """
    Get posts filtered by category slug.
    
    - **category_slug**: Category slug to filter by
    - **page**: Page number (default: 1)
    - **per_page**: Posts per page (default: 9, max: 50)
    - **sort_by**: Sort field
    - **sort_direction**: Sort direction
    
    Returns paginated list of posts in the specified category.
    """
    # Create query object with category filter
    query = PostListQuery(
        category=category_slug,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    # Get posts using service
    post_service = PostService(db)
    try:
        posts_response = await post_service.get_published_posts(query, current_user)
        
        # If no posts found in category, return 404
        if posts_response.pagination.total == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or no posts in category"
            )
        
        return posts_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve posts"
        )


# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc)
    )


@router.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    ) 