from __future__ import annotations

import hashlib
import re
import secrets
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from html import unescape
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Request, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from models import Category, Post, Tag, User
from models.base import post_bookmarks, post_likes, post_tags, user_follows
from models.collection import ReadingHistory
from models.content_intelligence import (
    ContentSource,
    DistributionAsset,
    PostQualityReview,
    SiteSearchQuery,
    TopicBrief,
    TrackingClick,
    TrackingLink,
)
from schemas.content_intelligence import (
    ContentSourceCreate,
    DistributionAssetResponse,
    PostIntelligenceStatus,
    QualityReviewResponse,
    SearchConsoleImportRow,
    TopicBriefResponse,
    TrendingImportRow,
)
from services.post.post import PostService


_WORD_RE = re.compile(r"[a-z0-9]+")
_LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "but",
    "for",
    "from",
    "has",
    "have",
    "how",
    "into",
    "its",
    "more",
    "not",
    "that",
    "the",
    "their",
    "this",
    "was",
    "with",
    "you",
    "your",
}


def _plain_text(value: str | None) -> str:
    if not value:
        return ""
    text = unescape(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokens(value: str | None) -> set[str]:
    return {
        token
        for token in _WORD_RE.findall((value or "").lower())
        if len(token) > 2 and token not in _STOPWORDS
    }


def _canonical_title(value: str) -> str:
    return " ".join(_WORD_RE.findall(value.lower()))


def _clip(value: str, limit: int) -> str:
    cleaned = _plain_text(value)
    if len(cleaned) <= limit:
        return cleaned
    clipped = cleaned[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{clipped}..."


class ContentIntelligenceService:
    CRITICAL_STATUS = "blocked"
    REVIEW_STATUS = "needs_review"
    PASS_STATUS = "passed"

    @staticmethod
    async def create_source(
        session: AsyncSession,
        payload: ContentSourceCreate,
    ) -> ContentSource:
        source = ContentSource(
            name=payload.name,
            source_type=payload.source_type,
            url=str(payload.url) if payload.url else None,
            category_id=payload.category_id,
            is_active=payload.is_active,
            source_metadata=payload.source_metadata or {},
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
        return source

    @staticmethod
    async def list_sources(session: AsyncSession) -> list[ContentSource]:
        result = await session.execute(
            select(ContentSource).order_by(ContentSource.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def import_search_console_rows(
        session: AsyncSession,
        rows: list[SearchConsoleImportRow],
        current_user: User,
    ) -> int:
        for row in rows:
            ctr = row.ctr
            if ctr is None and row.impressions:
                ctr = row.clicks / row.impressions
            session.add(
                ContentSource(
                    name=row.query,
                    source_type="search_console",
                    url=row.page,
                    category_id=row.category_id,
                    is_active=True,
                    source_metadata={
                        "query": row.query,
                        "clicks": row.clicks,
                        "impressions": row.impressions,
                        "ctr": ctr,
                        "position": row.position,
                        "imported_by": current_user.uuid,
                    },
                )
            )
        await session.commit()
        return len(rows)

    @staticmethod
    async def import_trending_rows(
        session: AsyncSession,
        rows: list[TrendingImportRow],
        current_user: User,
    ) -> int:
        for row in rows:
            session.add(
                ContentSource(
                    name=row.topic,
                    source_type="trending",
                    url=str(row.url) if row.url else None,
                    category_id=row.category_id,
                    is_active=True,
                    source_metadata={
                        "topic": row.topic,
                        "source": row.source,
                        "score": row.score,
                        "imported_by": current_user.uuid,
                    },
                )
            )
        await session.commit()
        return len(rows)

    @staticmethod
    async def log_site_search(
        session: AsyncSession,
        *,
        query: str,
        result_count: int,
        request: Request | None = None,
        user_id: int | None = None,
    ) -> None:
        session_key = None
        if request is not None:
            ip = (
                request.headers.get("cf-connecting-ip")
                or (request.headers.get("x-forwarded-for", "").split(",")[0].strip() or None)
                or request.headers.get("x-real-ip")
                or (request.client.host if request.client else None)
                or "unknown"
            )
            user_agent = (request.headers.get("user-agent") or "").strip().lower()[:160]
            session_key = hashlib.sha256(f"{ip}|{user_agent}".encode()).hexdigest()[:32]

        session.add(
            SiteSearchQuery(
                query=query.strip()[:255],
                result_count=max(0, result_count),
                user_id=user_id,
                session_key=session_key,
            )
        )
        await session.commit()

    @staticmethod
    async def generate_topic_briefs(
        session: AsyncSession,
        *,
        current_user: User,
        limit: int = 10,
        include_rss: bool = True,
        include_imports: bool = True,
        include_site_search: bool = True,
        include_content_gaps: bool = True,
    ) -> list[TopicBrief]:
        signals: list[dict[str, Any]] = []
        if include_imports:
            signals.extend(await ContentIntelligenceService._import_source_signals(session))
        if include_site_search:
            signals.extend(await ContentIntelligenceService._site_search_signals(session))
        if include_content_gaps:
            signals.extend(await ContentIntelligenceService._content_gap_signals(session))
        if include_rss:
            signals.extend(await ContentIntelligenceService._rss_signals(session))

        signals = ContentIntelligenceService._dedupe_signals(signals)
        existing_result = await session.execute(select(TopicBrief.title))
        existing_titles = {_canonical_title(title) for title in existing_result.scalars().all()}

        briefs: list[TopicBrief] = []
        for signal in signals[:limit]:
            title = ContentIntelligenceService._brief_title(signal)
            canonical = _canonical_title(title)
            if not canonical or canonical in existing_titles:
                continue
            existing_titles.add(canonical)
            brief = TopicBrief(
                title=title[:255],
                angle=ContentIntelligenceService._brief_angle(signal),
                audience=signal.get("audience") or "CraftyXHub readers",
                keywords=ContentIntelligenceService._brief_keywords(signal),
                source_signals=[signal],
                category_id=signal.get("category_id"),
                status="pending",
                created_by_id=current_user.id,
            )
            session.add(brief)
            briefs.append(brief)

        await session.commit()
        for brief in briefs:
            await session.refresh(brief)
        return briefs

    @staticmethod
    async def list_topic_briefs(
        session: AsyncSession,
        *,
        status_filter: str | None = None,
        limit: int = 50,
    ) -> list[TopicBrief]:
        query = select(TopicBrief).order_by(TopicBrief.created_at.desc()).limit(limit)
        if status_filter:
            query = query.where(TopicBrief.status == status_filter)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_topic_brief_status(
        session: AsyncSession,
        *,
        brief_uuid: str,
        new_status: str,
    ) -> TopicBrief:
        brief = await ContentIntelligenceService._get_by_uuid(
            session, TopicBrief, brief_uuid, "Topic brief not found"
        )
        brief.status = new_status
        await session.commit()
        await session.refresh(brief)
        return brief

    @staticmethod
    async def run_quality_review(
        session: AsyncSession,
        *,
        post_uuid: str,
        current_user: User | None = None,
        check_external_links: bool = True,
    ) -> PostQualityReview:
        post = await ContentIntelligenceService._get_post(session, post_uuid)
        review = await ContentIntelligenceService._build_quality_review(
            session,
            post=post,
            current_user=current_user,
            check_external_links=check_external_links,
        )
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review

    @staticmethod
    async def _build_quality_review(
        session: AsyncSession,
        *,
        post: Post,
        current_user: User | None = None,
        check_external_links: bool = True,
    ) -> PostQualityReview:
        text = _plain_text(post.content)
        links = ContentIntelligenceService._extract_links(post.content)
        claims = ContentIntelligenceService._extract_claims(text)
        broken_links = await ContentIntelligenceService._check_links(
            links,
            check_external_links=check_external_links,
        )
        duplicates = await ContentIntelligenceService._internal_duplicates(session, post)
        internal_links = await ContentIntelligenceService._internal_link_suggestions(session, post)
        faqs = ContentIntelligenceService._faq_suggestions(post)
        schema = ContentIntelligenceService._schema_suggestions(post, faqs)
        source_freshness = ContentIntelligenceService._source_freshness(post, links, claims)

        critical_failures: list[str] = []
        warnings: list[str] = []

        if not post.category_id:
            critical_failures.append("Post must have a category before publishing.")
        if PostService.normalize_excerpt(post.excerpt) is None:
            critical_failures.append("Post must have a publish-ready excerpt.")
        if broken_links:
            critical_failures.append("Fix broken or unreachable links before publishing.")
        if claims and not links:
            warnings.append("Article has factual claims but no outbound sources.")
        if duplicates:
            warnings.append("Article is similar to existing CraftyXHub content.")
        if source_freshness.get("stale_source_count", 0) > 0:
            warnings.append("Some cited sources look older than 18 months.")

        score = max(
            0,
            100
            - len(critical_failures) * 30
            - len(warnings) * 12
            - min(len(claims), 8) * 2
            - min(len(duplicates), 3) * 8,
        )
        needs_human_review = bool(warnings or score < 80 or len(claims) >= 4)
        review_status = ContentIntelligenceService.PASS_STATUS
        if critical_failures:
            review_status = ContentIntelligenceService.CRITICAL_STATUS
            needs_human_review = True
        elif needs_human_review:
            review_status = ContentIntelligenceService.REVIEW_STATUS

        checks = {
            "claims": claims,
            "source_freshness": source_freshness,
            "broken_links": broken_links,
            "internal_duplicates": duplicates,
            "internal_link_suggestions": internal_links,
            "faq_suggestions": faqs,
            "schema_suggestions": schema,
            "critical_failures": critical_failures,
            "warnings": warnings,
        }

        review = PostQualityReview(
            post_id=post.id,
            checks=checks,
            needs_human_review=needs_human_review,
            score=score,
            status=review_status,
            approved_by_id=current_user.id if current_user and review_status == ContentIntelligenceService.PASS_STATUS else None,
            approved_at=datetime.utcnow() if current_user and review_status == ContentIntelligenceService.PASS_STATUS else None,
        )
        return review

    @staticmethod
    def _review_matches_current_post(review: PostQualityReview, post: Post) -> bool:
        if review is None:
            return False
        if post.updated_at is None or review.created_at is None:
            return True
        return review.created_at >= post.updated_at

    @staticmethod
    async def approve_quality_override(
        session: AsyncSession,
        *,
        post_uuid: str,
        current_user: User,
        override_reason: str,
    ) -> PostQualityReview:
        post = await ContentIntelligenceService._get_post(session, post_uuid)
        review = await ContentIntelligenceService.latest_quality_review(session, post.id)
        if review is None:
            review = await ContentIntelligenceService.run_quality_review(
                session,
                post_uuid=post_uuid,
                current_user=None,
                check_external_links=False,
            )
        if review.status == ContentIntelligenceService.CRITICAL_STATUS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Critical quality issues must be fixed before override.",
            )
        review.status = ContentIntelligenceService.PASS_STATUS
        review.needs_human_review = False
        review.override_reason = override_reason
        review.approved_by_id = current_user.id
        review.approved_at = datetime.utcnow()
        await session.commit()
        await session.refresh(review)
        return review

    @staticmethod
    async def validate_publish_gate(
        session: AsyncSession,
        *,
        post: Post,
        current_user: User,
        override_quality_gate: bool = False,
        override_reason: str | None = None,
    ) -> None:
        review = await ContentIntelligenceService.latest_quality_review(session, post.id)
        if not ContentIntelligenceService._review_matches_current_post(review, post):
            review = await ContentIntelligenceService.run_quality_review(
                session,
                post_uuid=post.uuid,
                current_user=None,
                check_external_links=False,
            )

        if review.status == ContentIntelligenceService.CRITICAL_STATUS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Quality gate blocked publishing.",
                    "quality_status": review.status,
                    "critical_failures": (review.checks or {}).get("critical_failures", []),
                },
            )

        if review.status == ContentIntelligenceService.REVIEW_STATUS:
            if not override_quality_gate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Quality review requires approval before publishing.",
                        "quality_status": review.status,
                        "warnings": (review.checks or {}).get("warnings", []),
                        "review_uuid": review.uuid,
                    },
                )
            if not current_user.is_moderator():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only moderators and admins can approve quality gate overrides",
                )
            review.status = ContentIntelligenceService.PASS_STATUS
            review.needs_human_review = False
            review.override_reason = override_reason or "Approved during publish."
            review.approved_by_id = current_user.id
            review.approved_at = datetime.utcnow()
            await session.commit()

    @staticmethod
    async def validate_uncommitted_publish_gate(
        session: AsyncSession,
        *,
        post: Post,
    ) -> None:
        review = await ContentIntelligenceService._build_quality_review(
            session,
            post=post,
            current_user=None,
            check_external_links=False,
        )

        if review.status == ContentIntelligenceService.CRITICAL_STATUS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Quality gate blocked publishing.",
                    "quality_status": review.status,
                    "critical_failures": (review.checks or {}).get("critical_failures", []),
                },
            )

        if review.status == ContentIntelligenceService.REVIEW_STATUS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Quality review requires approval before publishing.",
                    "quality_status": review.status,
                    "warnings": (review.checks or {}).get("warnings", []),
                },
            )

        session.add(review)

    @staticmethod
    def tracking_redirect_base_url() -> str:
        api_base_url = (settings.API_BASE_URL or "").rstrip("/")
        if api_base_url.endswith("/v1"):
            api_base_url = api_base_url[:-3]
        return api_base_url.rstrip("/")

    @staticmethod
    async def generate_distribution_assets(
        session: AsyncSession,
        *,
        post_uuid: str,
        current_user: User,
    ) -> list[DistributionAsset]:
        post = await ContentIntelligenceService._get_post(session, post_uuid)
        destination = f"{settings.FRONTEND_URL.rstrip('/')}/post/{post.slug}"
        summary = _clip(post.excerpt or post.meta_description or post.content, 220)
        title = post.meta_title or post.title
        platforms = ContentIntelligenceService._distribution_payloads(post, title, summary)
        tracked_platforms = set(platforms) - {"image_alt", "short_summary", "opengraph"}

        existing_result = await session.execute(
            select(DistributionAsset)
            .where(
                DistributionAsset.post_id == post.id,
                DistributionAsset.platform.in_(list(platforms)),
            )
            .order_by(DistributionAsset.created_at.desc(), DistributionAsset.id.desc())
        )
        existing_by_platform: dict[str, DistributionAsset] = {}
        for asset in existing_result.scalars().all():
            existing_by_platform.setdefault(asset.platform, asset)

        assets: list[DistributionAsset] = []
        for platform, payload in platforms.items():
            asset = existing_by_platform.get(platform)
            if asset is None:
                asset = DistributionAsset(
                    post_id=post.id,
                    platform=platform,
                    content=payload["content"],
                    asset_metadata=payload.get("metadata") or {},
                    status="pending",
                )
                session.add(asset)
                await session.flush()
            else:
                asset.content = payload["content"]
                asset.asset_metadata = payload.get("metadata") or {}

            if platform in tracked_platforms:
                link_result = await session.execute(
                    select(TrackingLink)
                    .where(
                        TrackingLink.distribution_asset_id == asset.id,
                        TrackingLink.platform == platform,
                    )
                    .order_by(TrackingLink.created_at.desc(), TrackingLink.id.desc())
                    .limit(1)
                )
                link = link_result.scalar_one_or_none()
                if link is None:
                    link = TrackingLink(
                        token=secrets.token_urlsafe(12),
                        post_id=post.id,
                        distribution_asset_id=asset.id,
                        platform=platform,
                        destination_url=destination,
                        utm_source=platform,
                        utm_medium="organic",
                        utm_campaign="content_intelligence",
                    )
                    session.add(link)
                else:
                    link.destination_url = destination
                    link.utm_source = platform
                    link.utm_medium = "organic"
                    link.utm_campaign = "content_intelligence"
                asset.tracked_url = f"{ContentIntelligenceService.tracking_redirect_base_url()}/r/{link.token}"

            assets.append(asset)

        await session.commit()
        for asset in assets:
            await session.refresh(asset)
        return assets

    @staticmethod
    async def list_distribution_assets(
        session: AsyncSession,
        *,
        post_uuid: str,
    ) -> list[DistributionAsset]:
        post = await ContentIntelligenceService._get_post(session, post_uuid)
        result = await session.execute(
            select(DistributionAsset)
            .where(DistributionAsset.post_id == post.id)
            .order_by(DistributionAsset.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_distribution_status(
        session: AsyncSession,
        *,
        asset_uuid: str,
        new_status: str,
        current_user: User,
    ) -> DistributionAsset:
        asset = await ContentIntelligenceService._get_by_uuid(
            session, DistributionAsset, asset_uuid, "Distribution asset not found"
        )
        asset.status = new_status
        if new_status == "approved":
            asset.approved_by_id = current_user.id
            asset.approved_at = datetime.utcnow()
        await session.commit()
        await session.refresh(asset)
        return asset

    @staticmethod
    async def record_tracking_click(
        session: AsyncSession,
        *,
        token: str,
        request: Request,
        user_id: int | None = None,
    ) -> str:
        result = await session.execute(
            select(TrackingLink).where(TrackingLink.token == token)
        )
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracking link not found")

        ip = (
            request.headers.get("cf-connecting-ip")
            or (request.headers.get("x-forwarded-for", "").split(",")[0].strip() or None)
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else None)
            or "unknown"
        )
        user_agent = (request.headers.get("user-agent") or "").strip()[:255]
        click = TrackingClick(
            tracking_link_id=link.id,
            user_id=user_id,
            ip_hash=hashlib.sha256(ip.encode()).hexdigest()[:64],
            user_agent=user_agent,
            referrer=request.headers.get("referer"),
        )
        link.click_count = (link.click_count or 0) + 1
        session.add(click)
        await session.commit()

        params = {
            "utm_source": link.utm_source or link.platform,
            "utm_medium": link.utm_medium or "organic",
            "utm_campaign": link.utm_campaign or "content_intelligence",
        }
        separator = "&" if "?" in link.destination_url else "?"
        return f"{link.destination_url}{separator}{urlencode(params)}"

    @staticmethod
    async def get_post_statuses(
        session: AsyncSession,
        *,
        post_uuids: list[str],
    ) -> dict[str, PostIntelligenceStatus]:
        if not post_uuids:
            return {}

        post_result = await session.execute(select(Post.id, Post.uuid).where(Post.uuid.in_(post_uuids)))
        post_rows = post_result.all()
        uuid_by_id = {post_id: uuid for post_id, uuid in post_rows}
        status_map = {
            uuid: PostIntelligenceStatus(post_uuid=uuid)
            for _, uuid in post_rows
        }

        for post_id, post_uuid in uuid_by_id.items():
            review = await ContentIntelligenceService.latest_quality_review(session, post_id)
            if review is not None:
                status_map[post_uuid].quality_status = review.status
                status_map[post_uuid].quality_score = review.score
                status_map[post_uuid].needs_human_review = bool(review.needs_human_review)

        assets_result = await session.execute(
            select(DistributionAsset.post_id, DistributionAsset.status, func.count(DistributionAsset.id))
            .where(DistributionAsset.post_id.in_(list(uuid_by_id.keys())))
            .group_by(DistributionAsset.post_id, DistributionAsset.status)
        )
        for post_id, asset_status, count in assets_result.all():
            post_uuid = uuid_by_id.get(post_id)
            if not post_uuid:
                continue
            if asset_status == "approved":
                status_map[post_uuid].distribution_approved = count
            elif asset_status == "pending":
                status_map[post_uuid].distribution_pending = count

        return status_map

    @staticmethod
    async def latest_quality_review(
        session: AsyncSession,
        post_id: int,
    ) -> PostQualityReview | None:
        result = await session.execute(
            select(PostQualityReview)
            .where(PostQualityReview.post_id == post_id)
            .order_by(PostQualityReview.created_at.desc(), PostQualityReview.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def affinity_ranked_post_ids(
        session: AsyncSession,
        *,
        user_id: int,
        limit: int,
    ) -> list[int]:
        category_weights: Counter[int] = Counter()
        tag_weights: Counter[int] = Counter()
        author_weights: Counter[int] = Counter()
        seen_post_ids: set[int] = set()

        read_result = await session.execute(
            select(Post.id, Post.category_id, ReadingHistory.read_progress)
            .join(ReadingHistory, ReadingHistory.post_id == Post.id)
            .where(ReadingHistory.user_id == user_id)
        )
        for post_id, category_id, progress in read_result.all():
            seen_post_ids.add(post_id)
            weight = 3 if (progress or 0) >= 80 else 1 if (progress or 0) >= 25 else 0
            if category_id and weight:
                category_weights[category_id] += weight

        liked_result = await session.execute(
            select(Post.id, Post.category_id)
            .join(post_likes, post_likes.c.post_id == Post.id)
            .where(post_likes.c.user_id == user_id)
        )
        for post_id, category_id in liked_result.all():
            seen_post_ids.add(post_id)
            if category_id:
                category_weights[category_id] += 4

        bookmark_result = await session.execute(
            select(Post.id, Post.category_id)
            .join(post_bookmarks, post_bookmarks.c.post_id == Post.id)
            .where(post_bookmarks.c.user_id == user_id)
        )
        for post_id, category_id in bookmark_result.all():
            seen_post_ids.add(post_id)
            if category_id:
                category_weights[category_id] += 5

        tag_result = await session.execute(
            select(post_tags.c.post_id, post_tags.c.tag_id)
            .where(post_tags.c.post_id.in_(seen_post_ids))
        )
        for _, tag_id in tag_result.all():
            tag_weights[tag_id] += 2

        click_result = await session.execute(
            select(TrackingLink.post_id)
            .join(TrackingClick, TrackingClick.tracking_link_id == TrackingLink.id)
            .where(TrackingClick.user_id == user_id)
        )
        clicked_ids = [post_id for (post_id,) in click_result.all()]
        if clicked_ids:
            clicked_posts = await session.execute(
                select(Post.id, Post.category_id).where(Post.id.in_(clicked_ids))
            )
            for post_id, category_id in clicked_posts.all():
                seen_post_ids.add(post_id)
                if category_id:
                    category_weights[category_id] += 2

        follow_result = await session.execute(
            select(user_follows.c.followed_id).where(user_follows.c.follower_id == user_id)
        )
        for followed_id in follow_result.scalars().all():
            author_weights[followed_id] += 3

        if not (category_weights or tag_weights or author_weights):
            return []

        candidate_filters = [Post.is_published.is_(True), Post.author_id != user_id]
        if seen_post_ids:
            candidate_filters.append(Post.id.notin_(seen_post_ids))

        candidate_query = (
            select(Post)
            .options(selectinload(Post.tags))
            .where(*candidate_filters)
            .limit(300)
        )
        candidates = (await session.execute(candidate_query)).scalars().all()
        scored: list[tuple[int, datetime, int, int]] = []
        for post in candidates:
            score = 0
            if post.category_id:
                score += category_weights[post.category_id]
            score += author_weights[post.author_id]
            for tag in post.tags or []:
                score += tag_weights[tag.id]
            if score <= 0:
                continue
            scored.append((
                score,
                post.published_at or post.created_at or datetime.min,
                post.view_count or 0,
                post.id,
            ))

        scored.sort(reverse=True)
        return [post_id for _, _, _, post_id in scored[:limit]]

    @staticmethod
    def to_quality_response(
        review: PostQualityReview,
        *,
        post_uuid: str | None = None,
    ) -> QualityReviewResponse:
        return QualityReviewResponse(
            uuid=review.uuid,
            post_uuid=post_uuid or review.post.uuid,
            checks=review.checks or {},
            needs_human_review=bool(review.needs_human_review),
            score=review.score,
            status=review.status,
            override_reason=review.override_reason,
            created_at=review.created_at,
            approved_at=review.approved_at,
        )

    @staticmethod
    def to_distribution_response(
        asset: DistributionAsset,
        *,
        post_uuid: str | None = None,
    ) -> DistributionAssetResponse:
        return DistributionAssetResponse(
            uuid=asset.uuid,
            post_uuid=post_uuid or asset.post.uuid,
            platform=asset.platform,
            content=asset.content,
            asset_metadata=asset.asset_metadata,
            tracked_url=asset.tracked_url,
            status=asset.status,
            created_at=asset.created_at,
            approved_at=asset.approved_at,
        )

    @staticmethod
    def to_topic_brief_response(brief: TopicBrief) -> TopicBriefResponse:
        return TopicBriefResponse(
            uuid=brief.uuid,
            title=brief.title,
            angle=brief.angle,
            audience=brief.audience,
            keywords=brief.keywords or [],
            source_signals=brief.source_signals or [],
            category_id=brief.category_id,
            status=brief.status,
            created_at=brief.created_at,
        )

    @staticmethod
    async def _get_post(session: AsyncSession, post_uuid: str) -> Post:
        result = await session.execute(
            select(Post)
            .where(Post.uuid == post_uuid)
            .options(selectinload(Post.tags), selectinload(Post.category), selectinload(Post.author))
        )
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return post

    @staticmethod
    async def _get_by_uuid(session: AsyncSession, model, value: str, missing_detail: str):
        result = await session.execute(select(model).where(model.uuid == value))
        record = result.scalar_one_or_none()
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail)
        return record

    @staticmethod
    async def _import_source_signals(session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            select(ContentSource)
            .where(
                ContentSource.is_active.is_(True),
                ContentSource.source_type.in_(["search_console", "trending", "competitor", "category"]),
            )
            .order_by(ContentSource.created_at.desc())
            .limit(80)
        )
        signals = []
        for source in result.scalars().all():
            metadata = source.source_metadata or {}
            topic = metadata.get("query") or metadata.get("topic") or source.name
            score = float(metadata.get("score") or metadata.get("impressions") or metadata.get("clicks") or 1)
            if metadata.get("ctr") is not None and metadata.get("impressions"):
                score += max(0, float(metadata["impressions"]) * (0.08 - float(metadata["ctr"])))
            signals.append({
                "type": source.source_type,
                "topic": topic,
                "score": score,
                "url": source.url,
                "category_id": source.category_id,
                "metadata": metadata,
            })
        return sorted(signals, key=lambda item: item.get("score", 0), reverse=True)

    @staticmethod
    async def _site_search_signals(session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            select(
                SiteSearchQuery.query,
                func.count(SiteSearchQuery.id).label("search_count"),
                func.avg(SiteSearchQuery.result_count).label("avg_results"),
            )
            .group_by(SiteSearchQuery.query)
            .order_by(desc("search_count"))
            .limit(30)
        )
        signals = []
        for query, search_count, avg_results in result.all():
            avg_results = float(avg_results or 0)
            score = int(search_count or 0) * (3 if avg_results < 1 else 1)
            signals.append({
                "type": "site_search",
                "topic": query,
                "score": score,
                "metadata": {
                    "search_count": int(search_count or 0),
                    "avg_results": avg_results,
                },
            })
        return signals

    @staticmethod
    async def _content_gap_signals(session: AsyncSession) -> list[dict[str, Any]]:
        stale_cutoff = datetime.utcnow() - timedelta(days=120)
        result = await session.execute(
            select(Category.id, Category.name, func.count(Post.id), func.max(Post.published_at))
            .outerjoin(Post, and_(Post.category_id == Category.id, Post.is_published.is_(True)))
            .group_by(Category.id, Category.name)
        )
        signals = []
        for category_id, name, post_count, last_published in result.all():
            if not post_count:
                score = 12
            elif last_published and last_published < stale_cutoff:
                score = 8
            else:
                continue
            signals.append({
                "type": "content_gap",
                "topic": name,
                "score": score,
                "category_id": category_id,
                "metadata": {
                    "published_posts": int(post_count or 0),
                    "last_published_at": last_published.isoformat() if last_published else None,
                },
            })
        return signals

    @staticmethod
    async def _rss_signals(session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(
            select(ContentSource)
            .where(ContentSource.is_active.is_(True), ContentSource.source_type == "rss", ContentSource.url.is_not(None))
            .limit(10)
        )
        signals = []
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            for source in result.scalars().all():
                try:
                    response = await client.get(source.url)
                    response.raise_for_status()
                    root = ET.fromstring(response.text)
                except Exception:
                    signals.append({
                        "type": "rss_error",
                        "topic": source.name,
                        "score": 0,
                        "url": source.url,
                        "category_id": source.category_id,
                        "metadata": {"error": "RSS fetch or parse failed"},
                    })
                    continue
                for item in root.findall(".//item")[:5] or root.findall(".//entry")[:5]:
                    title = item.findtext("title") or source.name
                    link = item.findtext("link") or source.url
                    signals.append({
                        "type": "rss",
                        "topic": _plain_text(title),
                        "score": 5,
                        "url": link,
                        "category_id": source.category_id,
                        "metadata": {"source": source.name},
                    })
        return signals

    @staticmethod
    def _dedupe_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for signal in signals:
            topic = _plain_text(signal.get("topic"))
            key = _canonical_title(topic)
            if not key:
                continue
            current = merged.get(key)
            if current is None:
                merged[key] = {**signal, "topic": topic}
                continue
            current["score"] = float(current.get("score", 0)) + float(signal.get("score", 0))
            current.setdefault("metadata", {})
        return sorted(merged.values(), key=lambda item: item.get("score", 0), reverse=True)

    @staticmethod
    def _brief_title(signal: dict[str, Any]) -> str:
        topic = _plain_text(signal.get("topic"))
        signal_type = signal.get("type")
        if signal_type == "site_search":
            return f"Answering Reader Questions About {topic.title()}"
        if signal_type == "content_gap":
            return f"What Readers Need To Know About {topic}"
        return topic[:255]

    @staticmethod
    def _brief_angle(signal: dict[str, Any]) -> str:
        signal_type = signal.get("type")
        topic = _plain_text(signal.get("topic"))
        if signal_type == "search_console":
            return "Refresh or create a targeted article for a query with proven search demand."
        if signal_type == "site_search":
            return "Turn repeated reader searches into a practical answer article."
        if signal_type == "content_gap":
            return "Fill a category gap with an evergreen explainer or guide."
        if signal_type == "rss":
            return "Respond to a timely external conversation with a CraftyXHub angle."
        return f"Create a focused topic brief around {topic}."

    @staticmethod
    def _brief_keywords(signal: dict[str, Any]) -> list[str]:
        topic = _plain_text(signal.get("topic"))
        keywords = [topic]
        keywords.extend(word.title() for word in _tokens(topic) if len(word) > 4)
        return list(dict.fromkeys(keywords))[:6]

    @staticmethod
    def _extract_links(content: str | None) -> list[str]:
        links = []
        for href in _LINK_RE.findall(content or ""):
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            links.append(href)
        return list(dict.fromkeys(links))

    @staticmethod
    async def _check_links(links: list[str], *, check_external_links: bool) -> list[dict[str, Any]]:
        broken = []
        for link in links[:8]:
            if not re.match(r"^https?://", link):
                broken.append({"url": link, "reason": "Unsupported or relative URL"})
                continue
            if not check_external_links:
                continue
            try:
                async with httpx.AsyncClient(timeout=6, follow_redirects=True) as client:
                    response = await client.head(link)
                    if response.status_code >= 400:
                        response = await client.get(link)
                if response.status_code >= 400:
                    broken.append({"url": link, "status_code": response.status_code})
            except Exception as exc:
                broken.append({"url": link, "reason": str(exc)[:160]})
        return broken

    @staticmethod
    def _extract_claims(text: str) -> list[dict[str, Any]]:
        claims = []
        for sentence in _SENTENCE_RE.split(text):
            normalized = sentence.strip()
            if len(normalized) < 40:
                continue
            lower = normalized.lower()
            if (
                re.search(r"\b\d{2,}(?:\.\d+)?%?\b", normalized)
                or "according to" in lower
                or "research" in lower
                or "study" in lower
                or "report" in lower
                or "survey" in lower
            ):
                claims.append({"text": normalized[:280], "type": "verifiable"})
            if len(claims) >= 10:
                break
        return claims

    @staticmethod
    async def _internal_duplicates(session: AsyncSession, post: Post) -> list[dict[str, Any]]:
        post_tokens = _tokens(post.title + " " + _plain_text(post.content))
        if not post_tokens:
            return []
        result = await session.execute(
            select(Post)
            .where(Post.id != post.id, Post.is_published.is_(True))
            .limit(200)
        )
        duplicates = []
        for candidate in result.scalars().all():
            candidate_tokens = _tokens(candidate.title + " " + _plain_text(candidate.content))
            if not candidate_tokens:
                continue
            similarity = len(post_tokens & candidate_tokens) / max(1, len(post_tokens | candidate_tokens))
            if similarity >= 0.35:
                duplicates.append({
                    "post_uuid": candidate.uuid,
                    "title": candidate.title,
                    "similarity": round(similarity, 3),
                })
        duplicates.sort(key=lambda item: item["similarity"], reverse=True)
        return duplicates[:5]

    @staticmethod
    async def _internal_link_suggestions(session: AsyncSession, post: Post) -> list[dict[str, Any]]:
        text_tokens = _tokens(post.title + " " + _plain_text(post.content))
        result = await session.execute(
            select(Post)
            .where(Post.id != post.id, Post.is_published.is_(True))
            .options(selectinload(Post.tags))
            .limit(100)
        )
        suggestions = []
        for candidate in result.scalars().all():
            candidate_tokens = _tokens(candidate.title + " " + (candidate.excerpt or ""))
            overlap = len(text_tokens & candidate_tokens)
            if post.category_id and candidate.category_id == post.category_id:
                overlap += 3
            if overlap >= 4:
                suggestions.append({
                    "post_uuid": candidate.uuid,
                    "title": candidate.title,
                    "slug": candidate.slug,
                    "anchor": candidate.title[:80],
                    "relevance_score": overlap,
                })
        suggestions.sort(key=lambda item: item["relevance_score"], reverse=True)
        return suggestions[:6]

    @staticmethod
    def _faq_suggestions(post: Post) -> list[dict[str, str]]:
        headings = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", post.content or "", flags=re.IGNORECASE)
        questions = []
        for heading in headings[:3]:
            plain = _plain_text(heading)
            if not plain:
                continue
            question = plain if plain.endswith("?") else f"What should readers know about {plain.lower()}?"
            questions.append({"question": question, "answer_hint": f"Summarize the section: {plain}"})
        if not questions:
            questions.append({
                "question": f"What is the main takeaway from {post.title}?",
                "answer_hint": _clip(post.excerpt or post.content, 180),
            })
        return questions[:3]

    @staticmethod
    def _schema_suggestions(post: Post, faqs: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "article": {
                "@type": "Article",
                "headline": post.meta_title or post.title,
                "description": post.meta_description or post.excerpt,
            },
            "faq": {
                "@type": "FAQPage",
                "mainEntity_count": len(faqs),
            } if faqs else None,
        }

    @staticmethod
    def _source_freshness(post: Post, links: list[str], claims: list[dict[str, Any]]) -> dict[str, Any]:
        text = post.content or ""
        current_year = datetime.utcnow().year
        years = [int(year) for year in re.findall(r"\b(20\d{2})\b", text)]
        stale_years = [year for year in years if current_year - year > 1]
        return {
            "outbound_source_count": len([link for link in links if link.startswith("http")]),
            "claim_count": len(claims),
            "dated_references": sorted(set(years), reverse=True)[:8],
            "stale_source_count": len(set(stale_years)),
        }

    @staticmethod
    def _distribution_payloads(post: Post, title: str, summary: str) -> dict[str, dict[str, Any]]:
        clean_title = _clip(title, 120)
        clean_summary = _clip(summary, 220)
        return {
            "linkedin": {
                "content": f"{clean_title}\n\n{clean_summary}\n\nRead the full piece:",
            },
            "x": {
                "content": _clip(f"{clean_title}: {clean_summary}", 240),
            },
            "facebook": {
                "content": f"{clean_title}\n\n{clean_summary}",
            },
            "newsletter": {
                "content": f"This week on CraftyXHub: {clean_title}. {clean_summary}",
            },
            "short_summary": {
                "content": clean_summary,
            },
            "image_alt": {
                "content": _clip(post.featured_image and f"Featured image for {post.title}" or post.title, 125),
            },
            "opengraph": {
                "content": clean_title,
                "metadata": {
                    "title": clean_title[:68],
                    "description": _clip(post.meta_description or post.excerpt or clean_summary, 155),
                    "image": post.featured_image,
                },
            },
        }
