"""
Comments API Router for CraftyXhub

API endpoints for comment management following SubPRD-CommentAPI.md specifications.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import optional_authentication, require_authentication
from models.user import User
from schemas.comment import (
    CommentListQuery,
    CommentCreateRequest,
    CommentUpdateRequest,
    GuestCommentRequest,
    CommentResponse,
    CommentListResponse
)
from services.comments import CommentService


router = APIRouter(prefix="/posts", tags=["Comments"])


@router.get(
    "/{post_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Post Comments",
    description="Get paginated comments for a post with hierarchical threading"
)
async def list_post_comments(
    post_id: UUID,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of comments per page"),
    sort_by: str = Query("newest", description="Sort order (newest, oldest, most_liked)"),
    include_replies: bool = Query(True, description="Include nested replies"),
    max_depth: int = Query(5, ge=1, le=10, description="Maximum reply depth to load"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> CommentListResponse:
    """
    Get paginated comments for a post with hierarchical threading.
    
    - **post_id**: UUID of the post
    - **page**: Page number (default: 1)
    - **per_page**: Comments per page (default: 20, max: 100)
    - **sort_by**: Sort order (newest, oldest, most_liked)
    - **include_replies**: Include nested replies (default: true)
    - **max_depth**: Maximum reply depth to load (default: 5, max: 10)
    
    Returns paginated list of approved comments with threading structure.
    Only approved comments are shown to public users.
    """
    # Create query object
    query = CommentListQuery(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        include_replies=include_replies,
        max_depth=max_depth
    )
    
    # Get comments using service
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


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Comment",
    description="Create a new comment on a post (requires authentication)"
)
async def create_comment(
    post_id: UUID,
    comment_data: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> CommentResponse:
    """
    Create a new comment on a post.
    
    - **post_id**: UUID of the post to comment on
    - **body**: Comment content (1-2000 characters)
    - **parent_id**: Optional parent comment ID for replies
    
    Requires authentication. Comments are auto-approved for trusted users.
    Returns the created comment with user information.
    """
    comment_service = CommentService(db)
    try:
        comment_response = await comment_service.create_comment(
            post_id, comment_data, current_user
        )
        return comment_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )


@router.post(
    "/{post_id}/comments/guest",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Guest Comment",
    description="Create a new guest comment on a post (requires moderation)"
)
async def create_guest_comment(
    post_id: UUID,
    comment_data: GuestCommentRequest,
    db: AsyncSession = Depends(get_db)
) -> CommentResponse:
    """
    Create a new guest comment on a post.
    
    - **post_id**: UUID of the post to comment on
    - **body**: Comment content (1-2000 characters)
    - **guest_name**: Name of the guest commenter
    - **guest_email**: Email of the guest commenter
    - **parent_id**: Optional parent comment ID for replies
    
    Guest comments require moderation before appearing publicly.
    Returns the created comment (will show as pending approval).
    """
    comment_service = CommentService(db)
    try:
        comment_response = await comment_service.create_guest_comment(
            post_id, comment_data
        )
        return comment_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create guest comment"
        )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Comment",
    description="Update a comment (author only)"
)
async def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
) -> CommentResponse:
    """
    Update an existing comment.
    
    - **comment_id**: UUID of the comment to update
    - **body**: Updated comment content (1-2000 characters)
    
    Only the comment author can update their own comments.
    Admins can also update any comment.
    """
    comment_service = CommentService(db)
    try:
        comment_response = await comment_service.update_comment(
            comment_id, comment_data, current_user
        )
        return comment_response
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permission" in str(e).lower() or "only" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Comment",
    description="Delete a comment (author, admin, or post author)"
)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authentication)
):
    """
    Delete a comment (soft delete to maintain thread integrity).
    
    - **comment_id**: UUID of the comment to delete
    
    Can be deleted by:
    - Comment author
    - Site admin
    - Post author
    
    Comments are soft-deleted to maintain reply thread integrity.
    """
    comment_service = CommentService(db)
    try:
        success = await comment_service.delete_comment(comment_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment"
            )
        return None
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "permission" in str(e).lower() or "don't have" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )


@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Comment",
    description="Get a specific comment with its replies"
)
async def get_comment(
    comment_id: UUID,
    include_replies: bool = Query(True, description="Include nested replies"),
    max_depth: int = Query(3, ge=1, le=10, description="Maximum reply depth to load"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> CommentResponse:
    """
    Get a specific comment with its replies.
    
    - **comment_id**: UUID of the comment
    - **include_replies**: Include nested replies (default: true)
    - **max_depth**: Maximum reply depth to load (default: 3, max: 10)
    
    Returns the comment with its reply thread if requested.
    Only approved comments are shown to public users.
    """
    comment_service = CommentService(db)
    try:
        # This would need to be implemented in the service
        # For now, return a simple error
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Individual comment retrieval not yet implemented"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve comment"
        )


@router.get(
    "/comments/{comment_id}/replies",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Comment Replies",
    description="Get replies to a specific comment"
)
async def get_comment_replies(
    comment_id: UUID,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(20, ge=1, le=100, description="Number of replies per page"),
    max_depth: int = Query(3, ge=1, le=10, description="Maximum reply depth to load"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(optional_authentication)
) -> CommentListResponse:
    """
    Get replies to a specific comment.
    
    - **comment_id**: UUID of the parent comment
    - **page**: Page number (default: 1)
    - **per_page**: Replies per page (default: 20, max: 100)
    - **max_depth**: Maximum reply depth to load (default: 3, max: 10)
    
    Returns paginated list of replies to the specified comment.
    """
    # This would need to be implemented in the service
    # For now, return a simple error
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Comment replies endpoint not yet implemented"
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