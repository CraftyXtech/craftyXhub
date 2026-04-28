from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


SourceType = Literal[
    "rss",
    "competitor",
    "category",
    "search_console",
    "trending",
]
ApprovalStatus = Literal["pending", "approved", "dismissed", "rejected"]
QualityStatus = Literal["not_checked", "passed", "needs_review", "blocked"]


class ContentSourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_type: SourceType
    url: Optional[HttpUrl] = None
    category_id: Optional[int] = None
    is_active: bool = True
    source_metadata: dict[str, Any] | None = None


class ContentSourceResponse(BaseModel):
    uuid: str
    name: str
    source_type: str
    url: Optional[str] = None
    category_id: Optional[int] = None
    is_active: bool
    source_metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchConsoleImportRow(BaseModel):
    query: str = Field(..., min_length=1, max_length=255)
    clicks: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    ctr: float | None = Field(default=None, ge=0)
    position: float | None = Field(default=None, ge=0)
    page: Optional[str] = Field(default=None, max_length=1000)
    category_id: Optional[int] = None


class TrendingImportRow(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="manual", max_length=100)
    score: float = Field(default=0, ge=0)
    url: Optional[HttpUrl] = None
    category_id: Optional[int] = None


class ImportResponse(BaseModel):
    imported: int = Field(..., ge=0)


class TopicBriefGenerateRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=25)
    include_rss: bool = True
    include_imports: bool = True
    include_site_search: bool = True
    include_content_gaps: bool = True


class TopicBriefResponse(BaseModel):
    uuid: str
    title: str
    angle: Optional[str] = None
    audience: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    source_signals: list[dict[str, Any]] = Field(default_factory=list)
    category_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicBriefStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "dismissed"]


class QualityReviewResponse(BaseModel):
    uuid: str
    post_uuid: str
    checks: dict[str, Any]
    needs_human_review: bool
    score: int
    status: QualityStatus
    override_reason: Optional[str] = None
    created_at: datetime
    approved_at: Optional[datetime] = None


class QualityOverrideRequest(BaseModel):
    override_reason: str = Field(..., min_length=3, max_length=1000)


class DistributionAssetResponse(BaseModel):
    uuid: str
    post_uuid: str
    platform: str
    content: str
    asset_metadata: dict[str, Any] | None = None
    tracked_url: Optional[str] = None
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None


class DistributionStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


class PostIntelligenceStatus(BaseModel):
    post_uuid: str
    quality_status: QualityStatus = "not_checked"
    quality_score: Optional[int] = None
    needs_human_review: bool = False
    distribution_pending: int = 0
    distribution_approved: int = 0


class PostStatusListResponse(BaseModel):
    statuses: dict[str, PostIntelligenceStatus]
