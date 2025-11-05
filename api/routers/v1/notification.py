from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.connection import get_db_session
from services.user.notification import NotificationService
from schemas.notification import (
    NotificationResponse,
    NotificationStats,
    MarkAllAsReadResponse
)
from models import User
from services.user.auth import get_current_active_user as get_current_user


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user
    
    - **skip**: Number of notifications to skip (pagination)
    - **limit**: Maximum number of notifications to return
    - **unread_only**: If true, only return unread notifications
    """
    notifications = await NotificationService.get_user_notifications(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    response = []
    for notif in notifications:
        notif_dict = {
            "id": notif.id,
            "uuid": notif.uuid,
            "recipient_id": notif.recipient_id,
            "sender_id": notif.sender_id,
            "notification_type": notif.notification_type,
            "post_id": notif.post_id,
            "comment_id": notif.comment_id,
            "title": notif.title,
            "message": notif.message,
            "action_url": notif.action_url,
            "is_read": notif.is_read,
            "read_at": notif.read_at,
            "email_sent": notif.email_sent,
            "created_at": notif.created_at,
            "updated_at": notif.updated_at,
        }
        
        if notif.sender:
            notif_dict["sender_username"] = notif.sender.username
            if notif.sender.profile:
                notif_dict["sender_avatar"] = notif.sender.profile.avatar
        
        if notif.post:
            notif_dict["post_title"] = notif.post.title
            notif_dict["post_slug"] = notif.post.slug
        
        response.append(NotificationResponse(**notif_dict))
    
    return response


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification statistics for the current user
    
    Returns:
    - **total**: Total number of notifications
    - **unread**: Number of unread notifications
    - **read**: Number of read notifications
    """
    return await NotificationService.get_notification_stats(
        session=session,
        user_id=current_user.id
    )


@router.get("/{notification_uuid}", response_model=NotificationResponse)
async def get_notification(
    notification_uuid: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific notification by UUID
    """
    notification = await NotificationService.get_notification_by_uuid(
        session=session,
        notification_uuid=notification_uuid,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notif_dict = {
        "id": notification.id,
        "uuid": notification.uuid,
        "recipient_id": notification.recipient_id,
        "sender_id": notification.sender_id,
        "notification_type": notification.notification_type,
        "post_id": notification.post_id,
        "comment_id": notification.comment_id,
        "title": notification.title,
        "message": notification.message,
        "action_url": notification.action_url,
        "is_read": notification.is_read,
        "read_at": notification.read_at,
        "email_sent": notification.email_sent,
        "created_at": notification.created_at,
        "updated_at": notification.updated_at,
    }
    
    if notification.sender:
        notif_dict["sender_username"] = notification.sender.username
        if notification.sender.profile:
            notif_dict["sender_avatar"] = notification.sender.profile.avatar
    
    if notification.post:
        notif_dict["post_title"] = notification.post.title
        notif_dict["post_slug"] = notification.post.slug
    
    return NotificationResponse(**notif_dict)


@router.patch("/{notification_uuid}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_uuid: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as read
    """
    notification = await NotificationService.mark_as_read(
        session=session,
        notification_uuid=notification_uuid,
        user_id=current_user.id
    )
    
    notif_dict = {
        "id": notification.id,
        "uuid": notification.uuid,
        "recipient_id": notification.recipient_id,
        "sender_id": notification.sender_id,
        "notification_type": notification.notification_type,
        "post_id": notification.post_id,
        "comment_id": notification.comment_id,
        "title": notification.title,
        "message": notification.message,
        "action_url": notification.action_url,
        "is_read": notification.is_read,
        "read_at": notification.read_at,
        "email_sent": notification.email_sent,
        "created_at": notification.created_at,
        "updated_at": notification.updated_at,
    }
    
    if notification.sender:
        notif_dict["sender_username"] = notification.sender.username
        if notification.sender.profile:
            notif_dict["sender_avatar"] = notification.sender.profile.avatar
    
    if notification.post:
        notif_dict["post_title"] = notification.post.title
        notif_dict["post_slug"] = notification.post.slug
    
    return NotificationResponse(**notif_dict)


@router.patch("/read-all", response_model=MarkAllAsReadResponse)
async def mark_all_as_read(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user
    """
    count = await NotificationService.mark_all_as_read(
        session=session,
        user_id=current_user.id
    )
    
    return MarkAllAsReadResponse(
        message=f"Marked {count} notifications as read",
        count=count
    )


@router.delete("/{notification_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_uuid: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific notification
    """
    await NotificationService.delete_notification(
        session=session,
        notification_uuid=notification_uuid,
        user_id=current_user.id
    )
    return None


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_notifications(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all notifications for the current user
    """
    count = await NotificationService.delete_all_notifications(
        session=session,
        user_id=current_user.id
    )
    
    return {
        "message": f"Deleted {count} notifications",
        "count": count
    }