import json
from pathlib import Path

from models import Category, Tag
from schemas.ai import BlogPost, BlogSection
from services.ai.taxonomy import BlogTaxonomyService, _TaxonomyResolver

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "production_taxonomy_snapshot.json"


def _build_post(*, title: str, summary: str, tags: list[str]) -> BlogPost:
    return BlogPost(
        title=title,
        slug="test-post-slug",
        summary=summary,
        sections=[
            BlogSection(
                heading="Section One",
                body_markdown=" ".join(["word"] * 80),
            ),
            BlogSection(
                heading="Section Two",
                body_markdown=" ".join(["word"] * 80),
            ),
            BlogSection(
                heading="Section Three",
                body_markdown=" ".join(["word"] * 80),
            ),
        ],
        tags=tags,
        seo_title="Test SEO Title That Fits The Length",
        seo_description=(
            "A suitable SEO description that is long enough to satisfy the "
            "schema without affecting taxonomy scoring."
        ),
    )


def _production_resolver() -> _TaxonomyResolver:
    snapshot = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    categories = [
        Category(
            id=item["id"],
            name=item["name"],
            slug=item["slug"],
            parent_id=item["parent_id"],
        )
        for item in snapshot["categories"]
    ]
    tags = [
        Tag(
            id=item["id"],
            name=item["name"],
            slug=item["slug"],
            category_id=item["category_id"],
            is_active=item["is_active"],
            canonical_tag_id=item["canonical_tag_id"],
        )
        for item in snapshot["tags"]
        if item["is_active"] and item["canonical_tag_id"] is None
    ]
    return _TaxonomyResolver(categories=categories, tags=tags)


def test_taxonomy_resolver_returns_confident_match_for_clear_signals():
    tech = Category(id=1, name="Tech & Innovation", slug="tech-and-innovation", parent_id=None)
    automation = Category(id=2, name="Automation", slug="automation", parent_id=1)
    business = Category(id=3, name="Business & Finance", slug="business-and-finance", parent_id=None)

    automation_tag = Tag(id=10, name="Automation", slug="automation", category_id=2, is_active=True)
    workflow_tag = Tag(
        id=11,
        name="Workflow Automation",
        slug="workflow-automation",
        category_id=2,
        is_active=True,
    )
    finance_tag = Tag(id=12, name="Investing", slug="investing", category_id=3, is_active=True)

    resolver = _TaxonomyResolver(
        categories=[tech, automation, business],
        tags=[automation_tag, workflow_tag, finance_tag],
    )

    result = resolver.resolve(
        topic="Workflow automation for enterprise operations teams",
        blog_post=_build_post(
            title="Workflow Automation Playbook for Fast-Moving Teams",
            summary="A practical guide to automation systems, workflow design, and process automation.",
            tags=["automation", "workflow automation"],
        ),
        keywords=["workflow automation", "process automation"],
        preferred_category_id=None,
    )

    assert result.category is not None
    assert result.category.id == 2
    assert result.review_required is False
    assert result.confidence_score >= BlogTaxonomyService.LOW_CONFIDENCE_THRESHOLD
    assert [tag.name for tag in result.tags] == ["Workflow Automation", "Automation"]


def test_taxonomy_resolver_returns_review_required_when_signals_are_weak():
    tech = Category(id=1, name="Tech & Innovation", slug="tech-and-innovation", parent_id=None)
    automation = Category(id=2, name="Automation", slug="automation", parent_id=1)
    business = Category(id=3, name="Business & Finance", slug="business-and-finance", parent_id=None)
    marketing = Category(id=4, name="Online Business & Marketing", slug="online-business-and-marketing", parent_id=3)

    automation_tag = Tag(id=10, name="Automation", slug="automation", category_id=2, is_active=True)
    marketing_tag = Tag(id=11, name="Affiliate Marketing", slug="affiliate-marketing", category_id=4, is_active=True)

    resolver = _TaxonomyResolver(
        categories=[tech, automation, business, marketing],
        tags=[automation_tag, marketing_tag],
    )

    result = resolver.resolve(
        topic="Fresh perspectives for modern teams",
        blog_post=_build_post(
            title="Fresh perspectives for modern teams",
            summary="A broad reflection on change, decision making, and current ideas.",
            tags=["insights", "trends"],
        ),
        keywords=["ideas"],
        preferred_category_id=None,
    )

    assert result.category is None
    assert result.tags == []
    assert result.review_required is True
    assert result.confidence_score < BlogTaxonomyService.LOW_CONFIDENCE_THRESHOLD


def test_taxonomy_resolver_keeps_preferred_category_even_when_review_is_required():
    tech = Category(id=1, name="Tech & Innovation", slug="tech-and-innovation", parent_id=None)
    products = Category(id=2, name="Products & Platforms", slug="products-and-platforms", parent_id=1)
    products_tag = Tag(id=10, name="Creator Platforms", slug="creator-platforms", category_id=2, is_active=True)

    resolver = _TaxonomyResolver(
        categories=[tech, products],
        tags=[products_tag],
    )

    result = resolver.resolve(
        topic="A broad update",
        blog_post=_build_post(
            title="A broad update",
            summary="A short general piece with weak taxonomy signals and very little specific taxonomy evidence.",
            tags=["update", "general"],
        ),
        keywords=[],
        preferred_category_id=2,
    )

    assert result.category is not None
    assert result.category.id == 2
    assert result.review_required is True


def test_production_taxonomy_prefers_ai_when_security_word_is_context_only():
    resolver = _production_resolver()

    result = resolver.resolve(
        topic="AI model safety dashboards for product teams tracking jailbreak and security risks",
        blog_post=_build_post(
            title="AI Safety Dashboards Help Product Teams Monitor Model Risk",
            summary=(
                "A practical article about artificial intelligence observability, "
                "model evaluation, jailbreak monitoring, and safer AI release workflows."
            ),
            tags=["artificial intelligence", "security", "ai assistants"],
        ),
        keywords=["artificial intelligence", "AI safety", "model evaluation"],
        preferred_category_id=None,
    )

    assert result.category is not None
    assert result.category.slug == "artificial-intelligence"
    assert result.review_required is False
    assert all(tag.category_id != 71 for tag in result.tags)


def test_production_taxonomy_does_not_let_crime_tag_hijack_ai_article():
    resolver = _production_resolver()

    result = resolver.resolve(
        topic="OpenAI, xAI, and new defense red lines for artificial intelligence systems",
        blog_post=_build_post(
            title="AI Policy Red Lines Are Changing Product Governance",
            summary=(
                "This news analysis focuses on artificial intelligence policy, "
                "governance reviews, model deployment rules, and product safety controls."
            ),
            tags=["artificial intelligence", "war crimes", "national security"],
        ),
        keywords=["AI policy", "artificial intelligence", "AI governance"],
        preferred_category_id=None,
    )

    assert result.category is not None
    assert result.category.slug == "artificial-intelligence"
    assert result.review_required is False


def test_production_taxonomy_returns_review_when_signals_are_conflicted():
    resolver = _production_resolver()

    result = resolver.resolve(
        topic="Teams, tools, risk, and platform changes",
        blog_post=_build_post(
            title="Platform Risk Update for Modern Teams",
            summary=(
                "A mixed article with scattered references to crime, safety, "
                "platform tools, AI, teams, and business risk without a dominant angle."
            ),
            tags=["artificial intelligence", "national security", "productivity tools"],
        ),
        keywords=["risk", "platforms", "teams"],
        preferred_category_id=None,
    )

    assert result.review_required is True
    assert result.category is None
