import pytest
from sqlalchemy import func, select

from models import Category, Post, Tag, User
from models.base import post_bookmarks, post_likes, post_tags
from models.collection import ReadingHistory
from models.content_intelligence import (
    DistributionAsset,
    PostQualityReview,
    SiteSearchQuery,
    TrackingLink,
)
from core.config import settings
from services.content_intelligence import ContentIntelligenceService
from services.post.post import PostService


@pytest.mark.asyncio
async def test_source_import_and_topic_brief_generation(client_admin):
    source_response = await client_admin.post(
        "/v1/content-intelligence/sources",
        json={
            "name": "Automation Feed",
            "source_type": "rss",
            "url": "https://example.com/feed.xml",
        },
    )
    assert source_response.status_code == 201

    import_response = await client_admin.post(
        "/v1/content-intelligence/imports/search-console",
        json=[
            {
                "query": "ai automation tools",
                "impressions": 1200,
                "clicks": 24,
                "ctr": 0.02,
            }
        ],
    )
    assert import_response.status_code == 200
    assert import_response.json()["imported"] == 1

    brief_response = await client_admin.post(
        "/v1/content-intelligence/briefs/generate",
        json={
            "limit": 5,
            "include_rss": False,
            "include_imports": True,
            "include_site_search": False,
            "include_content_gaps": False,
        },
    )
    assert brief_response.status_code == 200
    briefs = brief_response.json()
    assert briefs
    assert "ai automation tools" in briefs[0]["title"].lower()
    assert briefs[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_site_search_logging(client_public, test_session):
    response = await client_public.get("/search", params={"q": "no results here"})
    assert response.status_code == 200

    result = await test_session.execute(select(SiteSearchQuery))
    query = result.scalar_one()
    assert query.query == "no results here"
    assert query.result_count == 0


@pytest.mark.asyncio
async def test_quality_review_blocks_missing_publish_basics(client_admin, test_session, admin_user):
    post = Post(
        title="AI Claims Without Basics",
        slug="ai-claims-without-basics",
        content="<p>Research shows 75% of teams want better automation tooling.</p>",
        author_id=admin_user.id,
        is_published=False,
    )
    test_session.add(post)
    await test_session.commit()
    await test_session.refresh(post)

    response = await client_admin.post(
        f"/v1/content-intelligence/posts/{post.uuid}/quality-review"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"
    assert data["needs_human_review"] is True
    assert data["checks"]["critical_failures"]


@pytest.mark.asyncio
async def test_distribution_assets_and_tracking_redirect(client_admin, client_public, test_session, admin_user, monkeypatch):
    monkeypatch.setattr(settings, "API_BASE_URL", "http://test/v1")
    category = Category(name="Automation", slug="automation")
    post = Post(
        title="Useful Automation Systems",
        slug="useful-automation-systems",
        content="<p>Useful automation systems reduce manual work.</p>",
        excerpt="Useful automation systems reduce manual work without hiding editorial control.",
        meta_title="Useful Automation Systems",
        meta_description="Useful automation systems reduce manual work while keeping editors in control.",
        author_id=admin_user.id,
        category=category,
        is_published=True,
    )
    test_session.add_all([category, post])
    await test_session.commit()
    await test_session.refresh(post)

    response = await client_admin.post(
        f"/v1/content-intelligence/posts/{post.uuid}/distribution"
    )
    assert response.status_code == 200
    assets = response.json()
    platforms = {asset["platform"] for asset in assets}
    assert {"linkedin", "x", "facebook", "newsletter", "short_summary", "image_alt", "opengraph"} <= platforms

    repeat_response = await client_admin.post(
        f"/v1/content-intelligence/posts/{post.uuid}/distribution"
    )
    assert repeat_response.status_code == 200
    assert len(repeat_response.json()) == len(assets)

    asset_count = await test_session.scalar(
        select(func.count()).select_from(DistributionAsset)
    )
    link_count = await test_session.scalar(
        select(func.count()).select_from(TrackingLink)
    )
    assert asset_count == len(assets)
    assert link_count == 4

    link = (await test_session.execute(select(TrackingLink))).scalars().first()
    tracked_asset = next(asset for asset in assets if asset["tracked_url"])
    assert tracked_asset["tracked_url"].startswith("http://test/r/")
    redirect_response = await client_public.get(f"/r/{link.token}", follow_redirects=False)
    assert redirect_response.status_code == 302
    assert "utm_source=" in redirect_response.headers["location"]


@pytest.mark.asyncio
async def test_regular_user_cannot_override_quality_gate(client_author, test_session, author_user):
    category = Category(name="Editorial", slug="editorial")
    post = Post(
        title="Editorial Automation",
        slug="editorial-automation",
        content="<p>Editorial automation needs human review.</p>",
        excerpt="Editorial automation needs human review before a post is published.",
        author_id=author_user.id,
        category=category,
        is_published=False,
    )
    test_session.add_all([category, post])
    await test_session.commit()
    await test_session.refresh(post)

    test_session.add(
        PostQualityReview(
            post_id=post.id,
            checks={"warnings": ["Needs source review"], "critical_failures": []},
            needs_human_review=True,
            score=70,
            status="needs_review",
        )
    )
    await test_session.commit()

    response = await client_author.put(
        f"/v1/posts/{post.uuid}/publish",
        json={"override_quality_gate": True, "override_reason": "Ship it"},
    )

    assert response.status_code == 403
    await test_session.refresh(post)
    assert post.is_published is False


@pytest.mark.asyncio
async def test_for_you_affinity_prefers_bookmarked_tagged_posts(test_session, author_user):
    user = User(
        email="reader@example.com",
        username="reader",
        full_name="Reader",
        password="hashed",
        is_active=True,
    )
    category = Category(name="Productivity", slug="productivity")
    tag = Tag(name="Automation", slug="automation", category=category)
    seed_post = Post(
        title="Seed Automation Post",
        slug="seed-automation-post",
        content="<p>Seed content</p>",
        excerpt="Seed content excerpt for reader affinity.",
        author_id=author_user.id,
        category=category,
        is_published=True,
    )
    target_post = Post(
        title="Advanced Automation Guide",
        slug="advanced-automation-guide",
        content="<p>Advanced content</p>",
        excerpt="Advanced automation guide for focused readers.",
        author_id=author_user.id,
        category=category,
        is_published=True,
        view_count=10,
    )
    target_post_two = Post(
        title="Automation Review Checklist",
        slug="automation-review-checklist",
        content="<p>Checklist content</p>",
        excerpt="Automation review checklist for focused readers.",
        author_id=author_user.id,
        category=category,
        is_published=True,
        view_count=1,
    )
    fallback_post = Post(
        title="Generic Popular Post",
        slug="generic-popular-post",
        content="<p>Generic content</p>",
        excerpt="Generic popular post for fallback.",
        author_id=author_user.id,
        is_published=True,
        view_count=999,
    )
    test_session.add_all([user, category, tag, seed_post, target_post, target_post_two, fallback_post])
    await test_session.commit()
    await test_session.execute(post_tags.insert().values(post_id=seed_post.id, tag_id=tag.id))
    await test_session.execute(post_tags.insert().values(post_id=target_post.id, tag_id=tag.id))
    await test_session.execute(post_tags.insert().values(post_id=target_post_two.id, tag_id=tag.id))
    await test_session.execute(post_bookmarks.insert().values(user_id=user.id, post_id=seed_post.id))
    test_session.add(ReadingHistory(user_id=user.id, post_id=seed_post.id, read_progress=90))
    await test_session.commit()

    posts = await PostService.get_for_you_posts(test_session, user_id=user.id, limit=3)
    assert posts[0].uuid == target_post.uuid
    page_one = await PostService.get_for_you_posts(test_session, user_id=user.id, limit=1, skip=0)
    page_two = await PostService.get_for_you_posts(test_session, user_id=user.id, limit=1, skip=1)
    assert page_one[0].uuid != page_two[0].uuid
