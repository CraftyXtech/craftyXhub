import asyncio
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.site_settings import SiteSettings


logger = logging.getLogger(__name__)


class MarketDataService:
    CACHE_TTL = timedelta(minutes=5)
    QUOTE_URL = "https://api.twelvedata.com/quote"
    MOCK_MARKET_BASES = {
        "IXIC": {"price": 18245.66, "percent_change": 0.48, "currency": "USD"},
        "GSPC": {"price": 5298.34, "percent_change": 0.35, "currency": "USD"},
        "BTC/USD": {"price": 67240.15, "percent_change": 0.84, "currency": "USD"},
        "ETH/USD": {"price": 3248.80, "percent_change": 0.62, "currency": "USD"},
        "EUR/USD": {"price": 1.0826, "percent_change": 0.18, "currency": "USD"},
        "GBP/USD": {"price": 1.2741, "percent_change": -0.12, "currency": "USD"},
    }

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value in (None, "", "NaN"):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _decorate_cached_items(
        cls,
        cache: list[dict] | None,
        *,
        is_stale: bool,
    ) -> list[dict]:
        items = deepcopy(cache or [])
        for item in items:
            item["is_stale"] = is_stale
        return items

    @classmethod
    def _filter_cached_items_for_watchlist(
        cls,
        watchlist: list[dict],
        cache: list[dict] | None,
        *,
        is_stale: bool,
    ) -> list[dict]:
        cached_by_symbol: dict[str, dict] = {}
        for item in cache or []:
            symbol = str(item.get("symbol") or "").strip()
            if symbol:
                cached_by_symbol[symbol] = item

        filtered_items: list[dict] = []
        for watch_item in watchlist:
            symbol = str(watch_item.get("symbol") or "").strip()
            if not symbol:
                continue
            cached_item = cached_by_symbol.get(symbol)
            if not cached_item:
                continue

            merged_item = deepcopy(cached_item)
            merged_item["symbol"] = symbol
            merged_item["label"] = watch_item.get("label") or merged_item.get("label") or symbol
            merged_item["is_stale"] = is_stale
            filtered_items.append(merged_item)

        return filtered_items

    @classmethod
    def _build_mock_market_strip(cls, watchlist: list[dict]) -> list[dict]:
        mock_items: list[dict] = []
        for item in watchlist:
            symbol = str(item.get("symbol") or "").strip()
            if not symbol:
                continue

            base = cls.MOCK_MARKET_BASES.get(
                symbol,
                {"price": 100.0, "percent_change": 0.12, "currency": "USD"},
            )
            base_price = float(base["price"])
            percent_change = float(base["percent_change"])
            previous_close = base_price / (1 + (percent_change / 100)) if percent_change else base_price
            change = base_price - previous_close

            mock_items.append(
                {
                    "symbol": symbol,
                    "label": item.get("label") or symbol,
                    "price": round(base_price, 4) if base_price < 10 else round(base_price, 2),
                    "change": round(change, 4) if abs(change) < 10 else round(change, 2),
                    "percent_change": round(percent_change, 2),
                    "currency": base.get("currency"),
                    "is_up": percent_change >= 0,
                    "is_stale": False,
                    "is_mock": True,
                }
            )

        return mock_items

    @classmethod
    async def _fetch_quote(
        cls,
        client: httpx.AsyncClient,
        item: dict,
    ) -> dict | None:
        response = await client.get(
            cls.QUOTE_URL,
            params={
                "symbol": item["symbol"],
                "apikey": settings.TWELVEDATA_API_KEY,
            },
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") == "error":
            raise ValueError(payload.get("message") or "Market provider returned an error")

        price = cls._to_float(payload.get("close") or payload.get("price"))
        change = cls._to_float(payload.get("change"))
        percent_change = cls._to_float(
            payload.get("percent_change")
            or payload.get("rolling_1d_change")
            or payload.get("rolling_change")
        )
        is_up = change > 0 if change is not None else None

        return {
            "symbol": item["symbol"],
            "label": item.get("label") or item["symbol"],
            "price": price,
            "change": change,
            "percent_change": percent_change,
            "currency": payload.get("currency"),
            "is_up": is_up,
            "is_stale": False,
        }

    @classmethod
    async def _fetch_market_quotes(cls, watchlist: list[dict]) -> list[dict]:
        if not settings.TWELVEDATA_API_KEY:
            return []

        async with httpx.AsyncClient(timeout=10.0) as client:
            results = await asyncio.gather(
                *(cls._fetch_quote(client, item) for item in watchlist),
                return_exceptions=True,
            )

        quotes: list[dict] = []
        for item, result in zip(watchlist, results):
            if isinstance(result, Exception):
                logger.warning("Failed to fetch market quote for %s: %s", item.get("symbol"), result)
                continue
            if result:
                quotes.append(result)
        return quotes

    @classmethod
    async def get_market_strip(
        cls,
        session: AsyncSession,
        site_settings: SiteSettings,
    ) -> tuple[list[dict], datetime | None]:
        watchlist = [
            item for item in (site_settings.market_watchlist or [])
            if isinstance(item, dict) and item.get("enabled", True) and item.get("symbol")
        ]
        if not watchlist:
            return [], site_settings.market_cache_updated_at

        now = datetime.utcnow()
        cache = site_settings.market_cache or []
        updated_at = site_settings.market_cache_updated_at
        cache_is_fresh = bool(updated_at and updated_at >= now - cls.CACHE_TTL and cache)

        if cache_is_fresh:
            return cls._filter_cached_items_for_watchlist(
                watchlist,
                cache,
                is_stale=False,
            ), updated_at

        if not settings.TWELVEDATA_API_KEY:
            return cls._build_mock_market_strip(watchlist), None

        try:
            fresh_quotes = await cls._fetch_market_quotes(watchlist)
        except Exception as exc:  # pragma: no cover - defensive branch
            logger.warning("Failed to refresh market strip: %s", exc)
            fresh_quotes = []

        if fresh_quotes:
            site_settings.market_cache = fresh_quotes
            site_settings.market_cache_updated_at = now
            session.add(site_settings)
            await session.commit()
            return cls._decorate_cached_items(fresh_quotes, is_stale=False), now

        if cache:
            return cls._filter_cached_items_for_watchlist(
                watchlist,
                cache,
                is_stale=True,
            ), updated_at

        return [], None
