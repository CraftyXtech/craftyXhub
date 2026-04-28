from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.newsletter import NewsletterSubscriber
from schemas.newsletter import NewsletterSubscribeRequest


class NewsletterService:
    @staticmethod
    async def subscribe(
        session: AsyncSession,
        payload: NewsletterSubscribeRequest,
    ) -> tuple[NewsletterSubscriber, bool]:
        email = payload.email.lower()
        result = await session.execute(
            select(NewsletterSubscriber).where(
                func.lower(NewsletterSubscriber.email) == email
            )
        )
        subscriber = result.scalar_one_or_none()

        if subscriber:
            already_subscribed = subscriber.is_active
            subscriber.is_active = True
            subscriber.source = payload.source
            await session.commit()
            await session.refresh(subscriber)
            return subscriber, already_subscribed

        subscriber = NewsletterSubscriber(
            email=email,
            source=payload.source,
            is_active=True,
        )
        session.add(subscriber)
        await session.commit()
        await session.refresh(subscriber)
        return subscriber, False

    @staticmethod
    async def list_recent(
        session: AsyncSession,
        *,
        limit: int = 10,
    ) -> list[NewsletterSubscriber]:
        result = await session.execute(
            select(NewsletterSubscriber)
            .where(NewsletterSubscriber.is_active.is_(True))
            .order_by(
                NewsletterSubscriber.created_at.desc(),
                NewsletterSubscriber.id.desc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def active_count(session: AsyncSession) -> int:
        return (
            await session.scalar(
                select(func.count(NewsletterSubscriber.id)).where(
                    NewsletterSubscriber.is_active.is_(True)
                )
            )
            or 0
        )
