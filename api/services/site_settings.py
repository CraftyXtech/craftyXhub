from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.site_settings import SiteSettings
from schemas.settings import (
    PublicSiteSettingsResponse,
    ResolvedSpotlightItem,
    SiteSettingsResponse,
    SiteSettingsUpdate,
    SpotlightItem,
)
from services.market_data import MarketDataService


class SiteSettingsService:
    SINGLETON_KEY = "default"

    @staticmethod
    async def get_or_create(session: AsyncSession) -> SiteSettings:
        result = await session.execute(
            select(SiteSettings).where(SiteSettings.singleton_key == SiteSettingsService.SINGLETON_KEY)
        )
        site_settings = result.scalar_one_or_none()
        if site_settings:
            return site_settings

        site_settings = SiteSettings(singleton_key=SiteSettingsService.SINGLETON_KEY)
        session.add(site_settings)
        await session.commit()
        await session.refresh(site_settings)
        return site_settings

    @staticmethod
    def _normalize_spotlights(items: list[dict]) -> list[dict]:
        parsed = [SpotlightItem.model_validate(item).model_dump(mode="json") for item in items]
        default_found = False
        for item in parsed:
            if item.get("is_default") and not default_found:
                default_found = True
                continue
            item["is_default"] = False

        if parsed and not default_found:
            parsed[0]["is_default"] = True

        return parsed

    @staticmethod
    def _normalize_schedule_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)

    @staticmethod
    def _resolve_spotlight(items: list[dict]) -> ResolvedSpotlightItem | None:
        if not items:
            return None

        now = datetime.utcnow()
        parsed = [
            SpotlightItem.model_validate(item)
            for item in items
            if isinstance(item, dict) and item.get("enabled", True)
        ]
        if not parsed:
            return None

        active = [
            item
            for item in parsed
            if (
                SiteSettingsService._normalize_schedule_datetime(item.start_at) is None
                or SiteSettingsService._normalize_schedule_datetime(item.start_at) <= now
            )
            and (
                SiteSettingsService._normalize_schedule_datetime(item.end_at) is None
                or SiteSettingsService._normalize_schedule_datetime(item.end_at) >= now
            )
        ]
        ranked_active = sorted(active, key=lambda item: item.priority, reverse=True)
        if ranked_active:
            chosen = ranked_active[0]
        else:
            defaults = sorted(
                [item for item in parsed if item.is_default],
                key=lambda item: item.priority,
                reverse=True,
            )
            chosen = defaults[0] if defaults else sorted(parsed, key=lambda item: item.priority, reverse=True)[0]

        return ResolvedSpotlightItem(
            label=chosen.label,
            target_url=chosen.target_url,
            icon=chosen.icon,
            theme=chosen.theme,
        )

    @staticmethod
    async def get_admin_settings(session: AsyncSession) -> SiteSettingsResponse:
        site_settings = await SiteSettingsService.get_or_create(session)
        return SiteSettingsResponse.model_validate(site_settings)

    @staticmethod
    async def update_settings(
        session: AsyncSession,
        payload: SiteSettingsUpdate,
    ) -> SiteSettingsResponse:
        site_settings = await SiteSettingsService.get_or_create(session)
        data = payload.model_dump(mode="json")
        data["spotlight_items"] = SiteSettingsService._normalize_spotlights(data.get("spotlight_items", []))

        for field, value in data.items():
            setattr(site_settings, field, value)

        session.add(site_settings)
        await session.commit()
        await session.refresh(site_settings)
        return SiteSettingsResponse.model_validate(site_settings)

    @staticmethod
    async def get_public_settings(session: AsyncSession) -> PublicSiteSettingsResponse:
        site_settings = await SiteSettingsService.get_or_create(session)
        market_strip, market_updated_at = await MarketDataService.get_market_strip(session, site_settings)

        return PublicSiteSettingsResponse(
            identity_label=site_settings.identity_label,
            breaking_label=site_settings.breaking_label,
            daily_brief_label=site_settings.daily_brief_label,
            daily_brief_url=site_settings.daily_brief_url,
            ad_slot=site_settings.ad_slot,
            social_links=site_settings.social_links,
            active_spotlight=SiteSettingsService._resolve_spotlight(site_settings.spotlight_items or []),
            market_strip=market_strip,
            market_updated_at=market_updated_at,
        )
