from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.connection import get_db_session
from models import Post, User
from schemas.content_intelligence import (
    ContentSourceCreate,
    ContentSourceResponse,
    DistributionAssetResponse,
    DistributionStatusUpdate,
    ImportResponse,
    PostStatusListResponse,
    QualityOverrideRequest,
    QualityReviewResponse,
    SearchConsoleImportRow,
    TopicBriefGenerateRequest,
    TopicBriefResponse,
    TopicBriefStatusUpdate,
    TrendingImportRow,
)
from services.content_intelligence import ContentIntelligenceService
from services.user.auth import get_current_admin_or_moderator


router = APIRouter(
    prefix="/content-intelligence",
    tags=["Content Intelligence"],
)


@router.post(
    "/sources",
    response_model=ContentSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_source(
    payload: ContentSourceCreate,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    return await ContentIntelligenceService.create_source(session, payload)


@router.get("/sources", response_model=list[ContentSourceResponse])
async def list_sources(
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    return await ContentIntelligenceService.list_sources(session)


@router.post("/imports/search-console", response_model=ImportResponse)
async def import_search_console(
    rows: list[SearchConsoleImportRow] = Body(...),
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    imported = await ContentIntelligenceService.import_search_console_rows(
        session,
        rows,
        current_user,
    )
    return ImportResponse(imported=imported)


@router.post("/imports/trending", response_model=ImportResponse)
async def import_trending(
    rows: list[TrendingImportRow] = Body(...),
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    imported = await ContentIntelligenceService.import_trending_rows(
        session,
        rows,
        current_user,
    )
    return ImportResponse(imported=imported)


@router.post("/briefs/generate", response_model=list[TopicBriefResponse])
async def generate_topic_briefs(
    payload: TopicBriefGenerateRequest,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    briefs = await ContentIntelligenceService.generate_topic_briefs(
        session,
        current_user=current_user,
        limit=payload.limit,
        include_rss=payload.include_rss,
        include_imports=payload.include_imports,
        include_site_search=payload.include_site_search,
        include_content_gaps=payload.include_content_gaps,
    )
    return [
        ContentIntelligenceService.to_topic_brief_response(brief)
        for brief in briefs
    ]


@router.get("/briefs", response_model=list[TopicBriefResponse])
async def list_topic_briefs(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    briefs = await ContentIntelligenceService.list_topic_briefs(
        session,
        status_filter=status_filter,
        limit=limit,
    )
    return [
        ContentIntelligenceService.to_topic_brief_response(brief)
        for brief in briefs
    ]


@router.put("/briefs/{brief_uuid}/status", response_model=TopicBriefResponse)
async def update_topic_brief_status(
    brief_uuid: str,
    payload: TopicBriefStatusUpdate,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    brief = await ContentIntelligenceService.update_topic_brief_status(
        session,
        brief_uuid=brief_uuid,
        new_status=payload.status,
    )
    return ContentIntelligenceService.to_topic_brief_response(brief)


@router.get("/posts/statuses", response_model=PostStatusListResponse)
async def get_post_statuses(
    post_uuids: str = Query(..., description="Comma-separated post UUIDs"),
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    uuid_values = [value.strip() for value in post_uuids.split(",") if value.strip()]
    statuses = await ContentIntelligenceService.get_post_statuses(
        session,
        post_uuids=uuid_values,
    )
    return PostStatusListResponse(statuses=statuses)


@router.post("/posts/{post_uuid}/quality-review", response_model=QualityReviewResponse)
async def run_quality_review(
    post_uuid: str,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    review = await ContentIntelligenceService.run_quality_review(
        session,
        post_uuid=post_uuid,
        current_user=current_user,
    )
    return ContentIntelligenceService.to_quality_response(review, post_uuid=post_uuid)


@router.get("/posts/{post_uuid}/quality-review", response_model=QualityReviewResponse | None)
async def get_latest_quality_review(
    post_uuid: str,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    post = await ContentIntelligenceService._get_post(session, post_uuid)
    review = await ContentIntelligenceService.latest_quality_review(session, post.id)
    if review is None:
        return None
    return ContentIntelligenceService.to_quality_response(review, post_uuid=post_uuid)


@router.put("/posts/{post_uuid}/quality-review/override", response_model=QualityReviewResponse)
async def approve_quality_override(
    post_uuid: str,
    payload: QualityOverrideRequest,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    review = await ContentIntelligenceService.approve_quality_override(
        session,
        post_uuid=post_uuid,
        current_user=current_user,
        override_reason=payload.override_reason,
    )
    return ContentIntelligenceService.to_quality_response(review, post_uuid=post_uuid)


@router.post("/posts/{post_uuid}/distribution", response_model=list[DistributionAssetResponse])
async def generate_distribution_assets(
    post_uuid: str,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    assets = await ContentIntelligenceService.generate_distribution_assets(
        session,
        post_uuid=post_uuid,
        current_user=current_user,
    )
    return [
        ContentIntelligenceService.to_distribution_response(asset, post_uuid=post_uuid)
        for asset in assets
    ]


@router.get("/posts/{post_uuid}/distribution", response_model=list[DistributionAssetResponse])
async def list_distribution_assets(
    post_uuid: str,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    del current_user
    assets = await ContentIntelligenceService.list_distribution_assets(
        session,
        post_uuid=post_uuid,
    )
    return [
        ContentIntelligenceService.to_distribution_response(asset, post_uuid=post_uuid)
        for asset in assets
    ]


@router.put("/distribution/{asset_uuid}/status", response_model=DistributionAssetResponse)
async def update_distribution_status(
    asset_uuid: str,
    payload: DistributionStatusUpdate,
    current_user: User = Depends(get_current_admin_or_moderator),
    session: AsyncSession = Depends(get_db_session),
):
    asset = await ContentIntelligenceService.update_distribution_status(
        session,
        asset_uuid=asset_uuid,
        new_status=payload.status,
        current_user=current_user,
    )
    post_uuid = (
        await session.execute(select(Post.uuid).where(Post.id == asset.post_id))
    ).scalar_one()
    return ContentIntelligenceService.to_distribution_response(asset, post_uuid=post_uuid)
