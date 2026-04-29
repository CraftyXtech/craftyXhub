from datetime import UTC, datetime, timedelta

import pytest

from core.config import settings as runtime_settings
from services.market_data import MarketDataService
from services.site_settings import SiteSettingsService


@pytest.mark.asyncio
async def test_public_settings_defaults_when_missing(client_public, monkeypatch):
    monkeypatch.setattr(runtime_settings, "TWELVEDATA_API_KEY", "")
    response = await client_public.get("/v1/settings/public")
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["identity_label"] == "MARKET WATCH"
    assert body["breaking_label"] == "BREAKING"
    assert body["daily_brief_label"] == "DAILY BRIEF"
    assert body["daily_brief_url"] == "/brief"
    assert body["active_spotlight"]["label"] == "AI PULSE"
    assert [item["label"] for item in body["market_strip"]] == [
        "NASDAQ",
        "S&P 500",
        "BTC",
        "ETH",
        "EUR/USD",
        "GBP/USD",
    ]
    assert all(item["is_mock"] is True for item in body["market_strip"])


@pytest.mark.asyncio
async def test_admin_settings_round_trip_and_spotlight_resolution(client_admin, client_public):
    now = datetime.now(UTC)
    payload = {
        "site_name": "CraftyXHub",
        "site_description": "Signals for business and technology.",
        "contact_email": "editor@craftyxhub.test",
        "posts_per_page": 12,
        "allow_comments": True,
        "allow_registration": True,
        "require_email_verification": True,
        "identity_label": "MARKET WATCH",
        "breaking_label": "BREAKING",
        "daily_brief_label": "DAILY BRIEF",
        "daily_brief_url": "/brief",
        "social_links": [
            {"platform": "x", "label": "X", "url": "https://x.example/craftyx"},
            {"platform": "linkedin", "label": "LinkedIn", "url": "https://linkedin.example/craftyx"},
        ],
        "ad_slot": {
            "enabled": True,
            "mode": "placeholder",
            "label": "ADVERTISEMENT",
            "image_url": "",
            "target_url": "",
            "background_color": "#F4F6F8",
        },
        "market_watchlist": [
            {"symbol": "BTC/USD", "label": "BTC/USD", "enabled": True},
            {"symbol": "EUR/USD", "label": "EUR/USD", "enabled": True},
        ],
        "spotlight_items": [
            {
                "label": "AI PULSE",
                "target_url": "/category/ai",
                "icon": "sparkles",
                "theme": "emerald",
                "enabled": True,
                "start_at": None,
                "end_at": None,
                "priority": 10,
                "is_default": True,
            },
            {
                "label": "GEOTECH WATCH",
                "target_url": "/category/geotech",
                "icon": "radar",
                "theme": "violet",
                "enabled": True,
                "start_at": (now - timedelta(hours=1)).isoformat(),
                "end_at": (now + timedelta(hours=1)).isoformat(),
                "priority": 100,
                "is_default": False,
            },
        ],
    }

    update_response = await client_admin.put("/v1/settings", json=payload)
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["site_description"] == payload["site_description"]

    get_response = await client_admin.get("/v1/settings")
    assert get_response.status_code == 200, get_response.text
    get_body = get_response.json()
    assert get_body["contact_email"] == "editor@craftyxhub.test"
    assert get_body["social_links"][0]["platform"] == "x"

    public_response = await client_public.get("/v1/settings/public")
    assert public_response.status_code == 200, public_response.text
    public_body = public_response.json()
    assert public_body["active_spotlight"]["label"] == "GEOTECH WATCH"
    assert public_body["social_links"][1]["platform"] == "linkedin"


@pytest.mark.asyncio
async def test_public_settings_serves_cached_market_strip_when_provider_fails(
    client_public,
    test_session,
    monkeypatch,
):
    site_settings = await SiteSettingsService.get_or_create(test_session)
    site_settings.market_watchlist = [
        {"symbol": "BTC/USD", "label": "BTC/USD", "enabled": True},
    ]
    site_settings.market_cache = [
        {
            "symbol": "BTC/USD",
            "label": "BTC/USD",
            "price": 64500.12,
            "change": 200.0,
            "percent_change": 0.31,
            "currency": "USD",
            "is_up": True,
            "is_stale": False,
        }
    ]
    site_settings.market_cache_updated_at = datetime.utcnow() - timedelta(minutes=15)
    test_session.add(site_settings)
    await test_session.commit()

    monkeypatch.setattr(runtime_settings, "TWELVEDATA_API_KEY", "demo-key")

    async def failing_fetch(cls, watchlist):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(MarketDataService, "_fetch_market_quotes", classmethod(failing_fetch))

    response = await client_public.get("/v1/settings/public")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["market_strip"][0]["label"] == "BTC/USD"
    assert body["market_strip"][0]["is_stale"] is True


@pytest.mark.asyncio
async def test_public_settings_filters_cached_market_strip_to_current_watchlist(
    client_public,
    test_session,
):
    site_settings = await SiteSettingsService.get_or_create(test_session)
    site_settings.market_watchlist = [
        {"symbol": "EUR/USD", "label": "Euro/Dollar", "enabled": True},
        {"symbol": "BTC/USD", "label": "Bitcoin", "enabled": True},
    ]
    site_settings.market_cache = [
        {
            "symbol": "BTC/USD",
            "label": "Old Bitcoin Label",
            "price": 64500.12,
            "change": 200.0,
            "percent_change": 0.31,
            "currency": "USD",
            "is_up": True,
            "is_stale": False,
        },
        {
            "symbol": "ETH/USD",
            "label": "ETH/USD",
            "price": 3100.0,
            "change": -10.0,
            "percent_change": -0.32,
            "currency": "USD",
            "is_up": False,
            "is_stale": False,
        },
        {
            "symbol": "EUR/USD",
            "label": "Old EUR Label",
            "price": 1.08,
            "change": 0.01,
            "percent_change": 0.5,
            "currency": "USD",
            "is_up": True,
            "is_stale": False,
        },
    ]
    site_settings.market_cache_updated_at = datetime.utcnow()
    test_session.add(site_settings)
    await test_session.commit()

    response = await client_public.get("/v1/settings/public")
    assert response.status_code == 200, response.text
    body = response.json()
    assert [item["symbol"] for item in body["market_strip"]] == ["EUR/USD", "BTC/USD"]
    assert [item["label"] for item in body["market_strip"]] == ["Euro/Dollar", "Bitcoin"]
