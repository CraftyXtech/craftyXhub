import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.post.comment import  CommentService
from services.user.auth import get_current_active_user
from database.connection import get_db_session
from models import User
from schemas.comment import CommentCreate, CommentResponse, CommentListResponse
from fastapi import Query

router = APIRouter(prefix="/comments", tags=["comments"])



@router.get("/{post_uuid}/comments", response_model=CommentListResponse)
async def get_post_comments(
        post_uuid: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    comments =  await CommentService.get_post_comments(session, post_uuid, skip=skip, limit=limit)
    return CommentListResponse(comments=comments)


@router.post("/{post_uuid}/comments", response_model=CommentResponse)
async def create_comment(
        post_uuid: str,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await CommentService.create_comment(session, post_uuid, comment_data, current_user.id)


@router.put("/{comment_uuid}", response_model=CommentResponse)
async def update_comment(
    comment_uuid: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    db_comment = await CommentService.get_comment_by_uuid(session, comment_uuid)  
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if db_comment.author.id != current_user.id or not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment")

    updated_comment = await CommentService.update_comment(session, db_comment, comment_data)
    return updated_comment


@router.put("/{comment_uuid}/approve", response_model=CommentResponse)
async def approve_comment(
    comment_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    db_comment = await CommentService.get_comment_by_uuid(session, comment_uuid)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to approve comments")

    approved_comment = await CommentService.approve_comment(session, db_comment)
    return approved_comment

@router.delete("/{comment_uuid}", response_model=bool)
async def delete_comment(
    comment_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    db_comment = await CommentService.get_comment_by_uuid(session, comment_uuid)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if db_comment.author.id != current_user.id or not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")

    return await CommentService.delete_comment(session, db_comment)