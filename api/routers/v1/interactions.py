"""
Interactions API Router for CraftyXhub

API endpoints for social interactions following SubPRD-InteractionAPI.md specifications.
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import require_authentication
from models.user import User
from schemas.interaction import (
    LikeToggleResponse,
    BookmarkToggleRequest,
    BookmarkToggleResponse,
    PostInteractionsResponse,
    BatchInteractionsRequest,
    BatchInteractionsResponse
)
from services.interactions import LikeService


router = APIRouter(prefix="/posts", tags=["Interactions"])


@router.post(
    "/{post_id}/like",
    response_model=LikeToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle Post Like",
    description="Toggle like status for a post (requires authentication)"
)
async def toggle_post_like(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> LikeToggleResponse:
    """
    Toggle like status for a post.
    
    - **post_id**: UUID of the post to like/unlike
    
    Requires authentication. Toggles the like status:
    - If not liked: adds like
    - If already liked: removes like
    
    Returns current like status and updated like count.
    Operation is idempotent and atomic.
    """
    like_service = LikeService(db)
    try:
        like_response = await like_service.toggle_like(post_id, current_user.id)
        return like_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle like"
        )


@router.post(
    "/{post_id}/bookmark",
    response_model=BookmarkToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle Post Bookmark",
    description="Toggle bookmark status for a post (requires authentication)"
)
async def toggle_post_bookmark(
    post_id: UUID,
    bookmark_data: BookmarkToggleRequest = BookmarkToggleRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> BookmarkToggleResponse:
    """
    Toggle bookmark status for a post.
    
    - **post_id**: UUID of the post to bookmark/unbookmark
    - **collection_name**: Optional bookmark collection name (default: "default")
    
    Requires authentication. Toggles the bookmark status:
    - If not bookmarked: adds bookmark
    - If already bookmarked: removes bookmark
    
    Returns current bookmark status and collection name.
    """
    # TODO: Implement bookmark service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bookmark functionality not yet implemented"
    )


@router.get(
    "/{post_id}/interactions",
    response_model=PostInteractionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Post Interactions",
    description="Get interaction status and counts for a post"
)
async def get_post_interactions(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(require_authentication)
) -> PostInteractionsResponse:
    """
    Get interaction status and counts for a post.
    
    - **post_id**: UUID of the post
    
    Returns:
    - Like count and user's like status (if authenticated)
    - Bookmark count and user's bookmark status (if authenticated)
    - View count
    - Comment count
    - Share count
    
    User-specific status only returned if authenticated.
    """
    like_service = LikeService(db)
    try:
        # Get like count
        like_count = await like_service.get_like_count(post_id)
        
        # Get user's like status if authenticated
        is_liked = False
        if current_user:
            is_liked = await like_service.is_liked_by_user(post_id, current_user.id)
        
        # TODO: Implement other interaction counts
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


@router.post(
    "/batch/interactions",
    response_model=BatchInteractionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Batch Post Interactions",
    description="Get interaction status for multiple posts"
)
async def get_batch_post_interactions(
    batch_request: BatchInteractionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(require_authentication)
) -> BatchInteractionsResponse:
    """
    Get interaction status for multiple posts.
    
    - **post_ids**: List of post UUIDs (max 50)
    
    Returns interaction status for each requested post.
    User-specific status only returned if authenticated.
    Useful for post listing pages to show interaction status.
    """
    if len(batch_request.post_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 post IDs allowed per request"
        )
    
    like_service = LikeService(db)
    try:
        interactions = {}
        
        # Get like counts for all posts
        for post_id in batch_request.post_ids:
            like_count = await like_service.get_like_count(post_id)
            
            # Get user's like status if authenticated
            is_liked = False
            if current_user:
                is_liked = await like_service.is_liked_by_user(post_id, current_user.id)
            
            interactions[str(post_id)] = PostInteractionsResponse(
                post_id=post_id,
                is_liked=is_liked,
                is_bookmarked=False,  # TODO: Implement bookmark check
                like_count=like_count,
                bookmark_count=0,  # TODO: Implement bookmark count
                view_count=0,  # TODO: Implement view count
                comment_count=0,  # TODO: Implement comment count
                share_count=0  # TODO: Implement share count
            )
        
        return BatchInteractionsResponse(
            interactions=interactions,
            total_posts=len(batch_request.post_ids),
            processed_posts=len(interactions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve batch interactions"
        )


@router.get(
    "/users/me/likes",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get User's Liked Posts",
    description="Get posts liked by the current user"
)
async def get_user_likes(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of likes per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> List[dict]:
    """
    Get posts liked by the current user.
    
    - **page**: Page number (default: 1)
    - **per_page**: Likes per page (default: 20, max: 100)
    
    Returns paginated list of posts liked by the authenticated user.
    """
    like_service = LikeService(db)
    try:
        offset = (page - 1) * per_page
        likes = await like_service.get_user_likes(
            current_user.id, limit=per_page, offset=offset
        )
        
        # TODO: Convert to proper response format with post details
        return [
            {
                "post_id": str(like.post_id),
                "liked_at": like.created_at.isoformat(),
                # TODO: Add post details
            }
            for like in likes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user likes"
        )


@router.get(
    "/users/me/bookmarks",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get User's Bookmarked Posts",
    description="Get posts bookmarked by the current user"
)
async def get_user_bookmarks(
    collection: Optional[str] = Query(None, description="Filter by collection name"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of bookmarks per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> List[dict]:
    """
    Get posts bookmarked by the current user.
    
    - **collection**: Optional collection name filter
    - **page**: Page number (default: 1)
    - **per_page**: Bookmarks per page (default: 20, max: 100)
    
    Returns paginated list of posts bookmarked by the authenticated user.
    """
    # TODO: Implement bookmark service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bookmark functionality not yet implemented"
    )


@router.get(
    "/users/me/interactions",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get User's Interaction History",
    description="Get interaction history for the current user"
)
async def get_user_interaction_history(
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of interactions per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> List[dict]:
    """
    Get interaction history for the current user.
    
    - **interaction_type**: Optional filter (like, bookmark, follow, view, share)
    - **page**: Page number (default: 1)
    - **per_page**: Interactions per page (default: 20, max: 100)
    
    Returns paginated list of user's interactions across all types.
    """
    # TODO: Implement comprehensive interaction history
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Interaction history not yet implemented"
    )


# User following endpoints (separate from post interactions)
@router.post(
    "/users/{user_id}/follow",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Toggle User Follow",
    description="Toggle follow status for a user (requires authentication)"
)
async def toggle_user_follow(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> dict:
    """
    Toggle follow status for a user.
    
    - **user_id**: UUID of the user to follow/unfollow
    
    Requires authentication. Toggles the follow status:
    - If not following: adds follow
    - If already following: removes follow
    
    Returns current follow status and follower counts.
    """
    # TODO: Implement follow service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Follow functionality not yet implemented"
    )


@router.get(
    "/users/{user_id}/followers",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get User Followers",
    description="Get list of users following the specified user"
)
async def get_user_followers(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of followers per page"),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get list of users following the specified user.
    
    - **user_id**: UUID of the user
    - **page**: Page number (default: 1)
    - **per_page**: Followers per page (default: 20, max: 100)
    
    Returns paginated list of followers.
    """
    # TODO: Implement follow service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Follow functionality not yet implemented"
    )


@router.get(
    "/users/{user_id}/following",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get User Following",
    description="Get list of users followed by the specified user"
)
async def get_user_following(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of following per page"),
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """
    Get list of users followed by the specified user.
    
    - **user_id**: UUID of the user
    - **page**: Page number (default: 1)
    - **per_page**: Following per page (default: 20, max: 100)
    
    Returns paginated list of users being followed.
    """
    # TODO: Implement follow service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Follow functionality not yet implemented"
    )


# Error handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Handle validation errors"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc)
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected errors"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    ) 