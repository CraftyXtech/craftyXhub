from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    POST_LIKE = "post_like"
    POST_COMMENT = "post_comment"
    POST_BOOKMARK = "post_bookmark"
    COMMENT_REPLY = "comment_reply"
    NEW_FOLLOWER = "new_follower"
    NEW_POST_FROM_FOLLOWING = "new_post_from_following"
    POST_PUBLISHED = "post_published"
    POST_FLAGGED = "post_flagged"
    POST_UNFLAGGED = "post_unflagged"
    POST_REPORTED = "post_reported"
    WELCOME = "welcome"
    EMAIL_VERIFIED = "email_verified"


class NotificationBase(BaseModel):
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    action_url: Optional[str] = Field(None, max_length=500)


class NotificationCreate(NotificationBase):
    recipient_id: int = Field(..., gt=0)
    sender_id: Optional[int] = Field(None, gt=0)
    post_id: Optional[int] = Field(None, gt=0)
    comment_id: Optional[int] = Field(None, gt=0)


class NotificationResponse(NotificationBase):
    id: int
    uuid: str
    recipient_id: int
    sender_id: Optional[int] = None
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    email_sent: bool
    created_at: datetime
    updated_at: datetime
    
    # Related data
    sender_username: Optional[str] = None
    sender_avatar: Optional[str] = None
    post_title: Optional[str] = None
    post_slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationStats(BaseModel):
    total: int = Field(..., ge=0)
    unread: int = Field(..., ge=0)
    read: int = Field(..., ge=0)


class MarkAsReadResponse(BaseModel):
    success: bool = True
    message: str = "Notification marked as read"


class MarkAllAsReadResponse(BaseModel):
    message: str
    count: int = Field(..., ge=0)


class DeleteNotificationResponse(BaseModel):
    message: str = "Notification deleted successfully"
    success: bool = True


class DeleteAllNotificationsResponse(BaseModel):
    message: str
    count: int = Field(..., ge=0)


class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    post_likes: bool = True
    post_comments: bool = True
    post_bookmarks: bool = True
    comment_replies: bool = True
    new_followers: bool = True
    new_posts_from_following: bool = True

    model_config = ConfigDict(from_attributes=True)


class BulkNotificationCreate(BaseModel):
    recipient_ids: list[int] = Field(..., min_length=1)
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    sender_id: Optional[int] = Field(None, gt=0)
    post_id: Optional[int] = Field(None, gt=0)
    comment_id: Optional[int] = Field(None, gt=0)
    action_url: Optional[str] = Field(None, max_length=500)


class NotificationFilter(BaseModel):
    notification_type: Optional[NotificationType] = None
    is_read: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sender_id: Optional[int] = Field(None, gt=0)

    model_config = ConfigDict(from_attributes=True)