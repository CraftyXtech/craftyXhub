from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text

from .base import BaseTable


def default_social_links() -> list[dict]:
    return [
        {"platform": "x", "label": "X", "url": ""},
        {"platform": "facebook", "label": "Facebook", "url": ""},
        {"platform": "instagram", "label": "Instagram", "url": ""},
        {"platform": "linkedin", "label": "LinkedIn", "url": ""},
    ]


def default_ad_slot() -> dict:
    return {
        "enabled": True,
        "mode": "placeholder",
        "label": "ADVERTISEMENT",
        "image_url": "",
        "target_url": "",
        "background_color": "#F4F6F8",
    }


def default_market_watchlist() -> list[dict]:
    return [
        {"symbol": "IXIC", "label": "NASDAQ", "enabled": True},
        {"symbol": "GSPC", "label": "S&P 500", "enabled": True},
        {"symbol": "BTC/USD", "label": "BTC", "enabled": True},
        {"symbol": "ETH/USD", "label": "ETH", "enabled": True},
        {"symbol": "EUR/USD", "label": "EUR/USD", "enabled": True},
        {"symbol": "GBP/USD", "label": "GBP/USD", "enabled": True},
    ]


def default_spotlight_items() -> list[dict]:
    return [
        {
            "label": "AI PULSE",
            "target_url": "/category/ai",
            "icon": "sparkles",
            "theme": "emerald",
            "enabled": True,
            "start_at": None,
            "end_at": None,
            "priority": 100,
            "is_default": True,
        }
    ]


class SiteSettings(BaseTable):
    __tablename__ = "site_settings"

    singleton_key = Column(String(32), nullable=False, unique=True, default="default")

    site_name = Column(String(120), nullable=False, default="CraftyXHub")
    site_description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    posts_per_page = Column(Integer, nullable=False, default=10)
    allow_comments = Column(Boolean, nullable=False, default=True)
    allow_registration = Column(Boolean, nullable=False, default=True)
    require_email_verification = Column(Boolean, nullable=False, default=True)

    identity_label = Column(String(80), nullable=False, default="MARKET WATCH")
    breaking_label = Column(String(80), nullable=False, default="BREAKING")
    daily_brief_label = Column(String(80), nullable=False, default="DAILY BRIEF")
    daily_brief_url = Column(String(255), nullable=False, default="/brief")

    social_links = Column(JSON, nullable=False, default=default_social_links)
    ad_slot = Column(JSON, nullable=False, default=default_ad_slot)
    market_watchlist = Column(JSON, nullable=False, default=default_market_watchlist)
    market_cache = Column(JSON, nullable=False, default=list)
    market_cache_updated_at = Column(DateTime, nullable=True)
    spotlight_items = Column(JSON, nullable=False, default=default_spotlight_items)
