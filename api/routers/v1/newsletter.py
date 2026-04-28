from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from models import User
from schemas.newsletter import (
    NewsletterSubscribeRequest,
    NewsletterSubscriberResponse,
    NewsletterSubscribeResponse,
)
from services.newsletter import NewsletterService
from services.user.auth import get_current_admin_or_moderator


router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.post(
    "/subscribe",
    response_model=NewsletterSubscribeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_to_newsletter(
    payload: NewsletterSubscribeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> NewsletterSubscribeResponse:
    subscriber, already_subscribed = await NewsletterService.subscribe(session, payload)
    return NewsletterSubscribeResponse(
        subscriber=subscriber,
        already_subscribed=already_subscribed,
    )


@router.get("/subscribers", response_model=list[NewsletterSubscriberResponse])
async def list_newsletter_subscribers(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    return await NewsletterService.list_recent(session, limit=limit)
