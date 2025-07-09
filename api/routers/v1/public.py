"""
Public API Router for CraftyXhub

Aggregates common public endpoints for easy access without authentication.
This router provides a clean public API interface for frontend applications.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import optional_authentication
from models.user import User
from schemas.post import (
    PostListQuery,
    PostDetailResponse,
    PaginatedPostsResponse,
    PostStatsResponse
)
from schemas.comment import (
    CommentListQuery,
    CommentListResponse
)
from schemas.interaction import PostInteractionsResponse
from services.posts import PostService
from services.comments import CommentService
from services.interactions import LikeService


router = APIRouter(prefix="/public", tags=["Public API"])


@router.get(
    "/posts",
    response_model=PaginatedPostsResponse,
    status_code=status.HTTP_200_OK,
    summary="Public Posts Listing",
    description="Get paginated list of published posts (public access)"
)
async def get_public_posts(
    category: Optional[str] = Query(None, description="Category slug for filtering"),
    search: Optional[str] = Query(None, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(9, ge=1, le=50, description="Posts per page"),
    sort_by: str = Query("published_at", description="Sort field"),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PaginatedPostsResponse:
    """
    Public endpoint for getting published posts.
    
    This endpoint provides the same functionality as the authenticated posts endpoint
    but is explicitly marked as public for frontend routing purposes.
    """
    query = PostListQuery(
        category=category,
        search=search,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
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
    "/posts/{post_id}",
    response_model=PostDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Public Post Details",
    description="Get individual post details (public access)"
)
async def get_public_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PostDetailResponse:
    """
    Public endpoint for getting individual post details.
    
    This endpoint provides the same functionality as the authenticated post endpoint
    but is explicitly marked as public for frontend routing purposes.
    """
    post_service = PostService(db)
    post = await post_service.get_post_by_id(post_id, current_user)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.get(
    "/posts/{post_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Public Post Comments",
    description="Get comments for a post (public access)"
)
async def get_public_post_comments(
    post_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Comments per page"),
    sort_by: str = Query("newest", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> CommentListResponse:
    """
    Public endpoint for getting post comments.
    
    Only approved comments are returned for public access.
    """
    query = CommentListQuery(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        include_replies=True,
        max_depth=5
    )
    
    comment_service = CommentService(db)
    try:
        comments_response = await comment_service.get_post_comments(
            post_id, query, current_user
        )
        return comments_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve comments"
        )


@router.get(
    "/posts/{post_id}/interactions",
    response_model=PostInteractionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Public Post Interactions",
    description="Get interaction counts for a post (public access)"
)
async def get_public_post_interactions(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> PostInteractionsResponse:
    """
    Public endpoint for getting post interaction counts.
    
    User-specific status (is_liked, is_bookmarked) only returned if authenticated.
    """
    like_service = LikeService(db)
    try:
        # Get like count
        like_count = await like_service.get_like_count(post_id)
        
        # Get user's like status if authenticated
        is_liked = False
        if current_user:
            is_liked = await like_service.is_liked_by_user(post_id, current_user.id)
        
        return PostInteractionsResponse(
            post_id=post_id,
            is_liked=is_liked,
            is_bookmarked=False,  # TODO: Implement bookmark check
            like_count=like_count,
            bookmark_count=0,  # TODO: Implement bookmark count
            view_count=0,  # TODO: Implement view count
            comment_count=0,  # TODO: Implement comment count
            share_count=0  # TODO: Implement share count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve post interactions"
        )


@router.get(
    "/categories",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    summary="Public Categories",
    description="Get list of available categories (public access)"
)
async def get_public_categories(
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """
    Public endpoint for getting available categories.
    
    Returns list of categories with basic information.
    """
    # TODO: Implement category service
    return [
        {"id": "1", "name": "Technology", "slug": "technology"},
        {"id": "2", "name": "Design", "slug": "design"},
        {"id": "3", "name": "Development", "slug": "development"}
    ]


@router.get(
    "/tags",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    summary="Public Tags",
    description="Get list of popular tags (public access)"
)
async def get_public_tags(
    limit: int = Query(20, ge=1, le=100, description="Number of tags to return"),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """
    Public endpoint for getting popular tags.
    
    Returns list of tags ordered by usage frequency.
    """
    # TODO: Implement tag service
    return [
        {"id": "1", "name": "Python", "slug": "python", "count": 25},
        {"id": "2", "name": "JavaScript", "slug": "javascript", "count": 20},
        {"id": "3", "name": "React", "slug": "react", "count": 15}
    ]


@router.get(
    "/stats",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Public Statistics",
    description="Get public platform statistics"
)
async def get_public_stats(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Public endpoint for getting platform statistics.
    
    Returns basic statistics about the platform.
    """
    # TODO: Implement statistics service
    return {
        "total_posts": 150,
        "total_users": 50,
        "total_comments": 300,
        "total_likes": 500
    } 