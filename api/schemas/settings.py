from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .base import BaseSchema


class SocialLinkItem(BaseModel):
    platform: str = Field(..., min_length=1, max_length=50)
    label: str = Field(..., min_length=1, max_length=50)
    url: str = ""


class AdSlotSettings(BaseModel):
    enabled: bool = True
    mode: Literal["placeholder", "image"] = "placeholder"
    label: str = Field(default="ADVERTISEMENT", min_length=1, max_length=100)
    image_url: str = ""
    target_url: str = ""
    background_color: str = "#F4F6F8"


class MarketWatchItem(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    label: str = Field(..., min_length=1, max_length=80)
    enabled: bool = True


class SpotlightItem(BaseModel):
    label: str = Field(..., min_length=1, max_length=80)
    target_url: str = Field(..., min_length=1, max_length=255)
    icon: Optional[str] = Field(default=None, max_length=40)
    theme: str = Field(default="emerald", min_length=1, max_length=40)
    enabled: bool = True
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    priority: int = 0
    is_default: bool = False


class MarketStripItem(BaseModel):
    symbol: str
    label: str
    price: Optional[float] = None
    change: Optional[float] = None
    percent_change: Optional[float] = None
    currency: Optional[str] = None
    is_up: Optional[bool] = None
    is_stale: bool = False
    is_mock: bool = False


class ResolvedSpotlightItem(BaseModel):
    label: str
    target_url: str
    icon: Optional[str] = None
    theme: str = "emerald"


class SiteSettingsBase(BaseModel):
    site_name: str = Field(default="CraftyXHub", min_length=1, max_length=120)
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    posts_per_page: int = Field(default=10, ge=1, le=50)
    allow_comments: bool = True
    allow_registration: bool = True
    require_email_verification: bool = True

    identity_label: str = Field(default="MARKET WATCH", min_length=1, max_length=80)
    breaking_label: str = Field(default="BREAKING", min_length=1, max_length=80)
    daily_brief_label: str = Field(default="DAILY BRIEF", min_length=1, max_length=80)
    daily_brief_url: str = Field(default="/brief", min_length=1, max_length=255)

    social_links: list[SocialLinkItem] = Field(default_factory=list)
    ad_slot: AdSlotSettings = Field(default_factory=AdSlotSettings)
    market_watchlist: list[MarketWatchItem] = Field(default_factory=list)
    spotlight_items: list[SpotlightItem] = Field(default_factory=list)


class SiteSettingsUpdate(SiteSettingsBase):
    pass


class SiteSettingsResponse(SiteSettingsBase, BaseSchema):
    uuid: str
    market_cache_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PublicSiteSettingsResponse(BaseModel):
    identity_label: str
    breaking_label: str
    daily_brief_label: str
    daily_brief_url: str
    ad_slot: AdSlotSettings
    social_links: list[SocialLinkItem]
    active_spotlight: Optional[ResolvedSpotlightItem] = None
    market_strip: list[MarketStripItem] = Field(default_factory=list)
    market_updated_at: Optional[datetime] = None
