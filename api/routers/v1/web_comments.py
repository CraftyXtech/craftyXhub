
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params
from dependencies.web_auth import (
    get_optional_current_user, verify_user_can_comment, 
    verify_comment_ownership, get_rate_limit_info
)
from models.user import User
from services.web.comment_service import WebCommentService
from schemas.web.comments import (
    CommentCreateRequest, CommentResponse, CommentThreadResponse,
    CommentSubmissionResponse, CommentListRequest, CommentListResponse,
    CommentStatsResponse
)

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Web Comments"])


@router.get("/", response_model=CommentListResponse)
async def get_post_comments(
    post_id: UUID,
    request: Request,
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Get comments for post
    comments_response = await service.get_post_comments(
        post_id=post_id,
        pagination=pagination,
        current_user=current_user
    )
    
    return comments_response


@router.post("/", response_model=CommentSubmissionResponse)
async def create_comment(
    post_id: UUID,
    comment_data: CommentCreateRequest,
    request: Request,
    current_user: User = Depends(verify_user_can_comment),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Get client information for rate limiting
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Create comment
    comment_response = await service.create_comment(
        post_id=post_id,
        comment_data=comment_data,
        author=current_user,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    return comment_response


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    post_id: UUID,
    comment_id: UUID,
    comment_data: CommentCreateRequest,
    request: Request,
    current_user: User = Depends(verify_comment_ownership),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Update comment
    comment_response = await service.update_comment(
        comment_id=comment_id,
        comment_data=comment_data,
        current_user=current_user
    )
    
    if not comment_response:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment_response


@router.delete("/{comment_id}")
async def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    request: Request,
    current_user: User = Depends(verify_comment_ownership),
    db: AsyncSession = Depends(get_db)
):

    service = WebCommentService(db)
    
    # Delete comment
    success = await service.delete_comment(
        comment_id=comment_id,
        current_user=current_user
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {"message": "Comment deleted successfully"}


@router.get("/stats", response_model=CommentStatsResponse)
async def get_comment_stats(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Get comment statistics
    stats_response = await service.get_comment_stats(
        post_id=post_id,
        current_user=current_user
    )
    
    return stats_response


@router.get("/thread/{comment_id}", response_model=CommentThreadResponse)
async def get_comment_thread(
    post_id: UUID,
    comment_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Get comment thread
    thread_response = await service.get_comment_thread(
        comment_id=comment_id,
        current_user=current_user
    )
    
    if not thread_response:
        raise HTTPException(status_code=404, detail="Comment thread not found")
    
    return thread_response


@router.post("/{comment_id}/like")
async def toggle_comment_like(
    post_id: UUID,
    comment_id: UUID,
    request: Request,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to like comments"
        )
    
    from services.web.interaction_service import WebInteractionService
    
    service = WebInteractionService(db)
    
    # Toggle comment like
    response = await service.toggle_comment_like(
        comment_id=comment_id,
        user=current_user
    )
    
    return {
        "liked": response.is_liked,
        "like_count": response.like_count,
        "message": "Like toggled successfully"
    }


@router.post("/{comment_id}/report")
async def report_comment(
    post_id: UUID,
    comment_id: UUID,
    reason: str,
    request: Request,
    current_user: User = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required to report comments"
        )
    
    # TODO: Implement comment reporting service
    # For now, return success
    
    return {
        "message": "Comment reported successfully",
        "comment_id": comment_id,
        "reason": reason
    }


# Create a separate router for comment management without post_id prefix
comment_router = APIRouter(prefix="/comments", tags=["Comment Management"])


@comment_router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment_by_id(
    comment_id: UUID,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebCommentService(db)
    
    # Get comment by ID
    comment_response = await service.get_comment_by_id(
        comment_id=comment_id,
        current_user=current_user
    )
    
    if not comment_response:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return comment_response


@comment_router.get("/user/{user_id}", response_model=CommentListResponse)
async def get_user_comments(
    user_id: UUID,
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    service = WebCommentService(db)
    
    # Get user comments
    comments_response = await service.get_user_comments(
        user_id=user_id,
        pagination=pagination,
        current_user=current_user
    )
    
    return comments_response 