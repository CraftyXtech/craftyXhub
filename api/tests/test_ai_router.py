import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from routers.v1.ai import router as ai_router
from schemas.ai import BlogGenerateRequest
from core.config import settings
from services.ai.generator import AIGeneratorService
from services.ai.blog_agent import BlogAgentService
from services.ai.llm_config import DEFAULT_MODEL, AVAILABLE_MODELS
from services.ai.taxonomy import BlogTaxonomyService
from services.post import PostService
from services.user.auth import get_current_active_user
from database.connection import get_db_session


class DummyUser:
    def __init__(self, user_id: int = 1):
        self.id = user_id


def test_blog_generate_request_does_not_save_draft_by_default():
    request = BlogGenerateRequest(topic="Fast AI blog generation")

    assert request.save_draft is False


def test_glm_51_is_the_only_enabled_blog_model():
    assert "gpt-5.4" in AVAILABLE_MODELS
    assert AVAILABLE_MODELS["gpt-5.4"]["blog_enabled"] is False
    assert DEFAULT_MODEL == "glm-5.1"
    assert AVAILABLE_MODELS["glm-5.1"]["blog_enabled"] is True
    assert AVAILABLE_MODELS["glm-5.1"]["provider_type"] == "nvidia"
    assert [
        key for key, entry in AVAILABLE_MODELS.items() if entry.get("blog_enabled")
    ] == ["glm-5.1"]


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(ai_router, prefix="/v1")

    # Dependency overrides
    async def _fake_user():
        return DummyUser(1)

    async def _fake_db():
        yield None

    app.dependency_overrides[get_current_active_user] = _fake_user
    app.dependency_overrides[get_db_session] = _fake_db
    return app


@pytest.mark.asyncio
async def test_generate_ok(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        return {
            "variants": [
                {"content": "<p>ok</p>", "metadata": {"words": 1, "model": kwargs.get("model")}}
            ],
            "tool_id": kwargs.get("tool_id"),
            "model_used": kwargs.get("model", DEFAULT_MODEL),
            "generation_time": 0.01,
        }

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "tool_id": "blog-ideas",
            "params": {"category": "Tech", "keywords": "ai"},
            "tone": "professional",
            "length": "short",
            "language": "en-US",
            "creativity": 0.3,
            "variant_count": 1,
        }
        resp = await ac.post("/v1/ai/generate", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["model_used"] == DEFAULT_MODEL
        assert data["tool_id"] == "blog-ideas"
        assert len(data["variants"]) == 1


@pytest.mark.asyncio
async def test_generate_bad_request_from_service(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        raise ValueError("bad input")

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "tool_id": "blog-ideas",
            "params": {},
        }
        resp = await ac.post("/v1/ai/generate", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_timeout_returns_504(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        raise TimeoutError("request timed out")

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "tool_id": "blog-ideas",
            "params": {"category": "Tech", "keywords": "ai"},
        }
        resp = await ac.post("/v1/ai/generate", json=payload)

    assert resp.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert DEFAULT_MODEL in resp.json()["detail"]
    assert "timed out" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_provider_error_returns_502(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        raise RuntimeError("OpenRouter upstream 502")

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "tool_id": "blog-ideas",
            "params": {"category": "Tech", "keywords": "ai"},
        }
        resp = await ac.post("/v1/ai/generate", json=payload)

    assert resp.status_code == status.HTTP_502_BAD_GATEWAY
    assert "failed at the ai provider" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_excerpt_ok(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        assert kwargs["tool_id"] == "post-excerpt"
        return {
            "variants": [
                {
                    "content": 'Excerpt: A sharp summary that captures the full article and gives readers a strong reason to continue reading.',
                    "metadata": {"words": 18, "model": kwargs.get("model")},
                }
            ],
            "tool_id": "post-excerpt",
            "model_used": kwargs.get("model", DEFAULT_MODEL),
            "generation_time": 0.08,
        }

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "title": "Why editorial summaries matter",
            "content": (
                "A long-form article about why publish-quality excerpts need to "
                "summarize the full piece instead of copying the opening paragraph."
            ),
        }
        resp = await ac.post("/v1/ai/generate/excerpt", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["excerpt"].startswith("A sharp summary")
    assert data["model_used"] == DEFAULT_MODEL


@pytest.mark.asyncio
async def test_generate_blog_ok_without_save_or_publish(app, monkeypatch):
    from schemas.ai import (
        BlogPost,
        BlogSection,
        BlogTaxonomyCategory,
        BlogTaxonomySuggestion,
        BlogTaxonomyTag,
    )

    async def fake_blog_generate(self, **kwargs):
        post = BlogPost(
            title="How to Build Production-Ready AI Content Pipelines",
            slug="how-to-build-production-ready-ai-content-pipelines",
            summary=(
                "This guide shows how to structure an AI content workflow "
                "with clear research, outlining, drafting, and editorial "
                "controls so outputs are consistent, factual, and ready to "
                "publish."
            ),
            sections=[
                BlogSection(
                    heading="Introduction",
                    body_markdown=" ".join(["word"] * 200),
                ),
                BlogSection(
                    heading="Research Method",
                    body_markdown=" ".join(["word"] * 220),
                ),
                BlogSection(
                    heading="Drafting Approach",
                    body_markdown=" ".join(["word"] * 230),
                ),
                BlogSection(
                    heading="Conclusion and Next Steps",
                    body_markdown=" ".join(["word"] * 210),
                ),
            ],
            tags=["ai-writing", "pydantic-ai", "content-ops"],
            seo_title="Build a Better AI Blog Writer with Pydantic AI",
            seo_description=(
                "Learn a practical, production-ready workflow for building "
                "an AI blog writer with structured outputs, quality checks, "
                "and reliable multi-step orchestration."
            ),
        )
        return post, 0.12, False, None

    async def fake_taxonomy_suggestion(*args, **kwargs):
        return BlogTaxonomySuggestion(
            category=BlogTaxonomyCategory(
                id=45,
                name="Artificial Intelligence",
                slug="artificial-intelligence",
                parent_id=44,
            ),
            tags=[
                BlogTaxonomyTag(id=101, name="AI", slug="ai", category_id=45),
                BlogTaxonomyTag(id=104, name="LLMs", slug="llms", category_id=45),
            ],
        )

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)
    monkeypatch.setattr(
        BlogTaxonomyService,
        "suggest_for_generated_post",
        fake_taxonomy_suggestion,
        raising=True,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Build an AI article writer",
            "blog_type": "how-to",
            "keywords": ["ai writer", "pydantic ai"],
            "word_count": "medium",
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["blog_post"]["title"].startswith("How to Build")
        assert data["draft_id"] is None
        assert data["post_id"] is None
        assert data["quality_report"] is not None
        assert "passed" in data["quality_report"]
        assert "readability" in data["quality_report"]
        assert "phase_metrics" in data["quality_report"]
        assert data["resolved_keywords"][:2] == ["AI Writer", "Pydantic AI"]
        assert data["taxonomy_suggestion"]["category"]["id"] == 45
        assert [tag["id"] for tag in data["taxonomy_suggestion"]["tags"]] == [101, 104]


@pytest.mark.asyncio
async def test_generate_blog_auto_generates_keywords_when_blank(app, monkeypatch):
    from schemas.ai import (
        BlogPost,
        BlogSection,
        BlogTaxonomyCategory,
        BlogTaxonomySuggestion,
        BlogTaxonomyTag,
    )

    async def fake_blog_generate(self, **kwargs):
        post = BlogPost(
            title="OpenAI and Anthropic IPO Rumors and AI Valuation Signals",
            slug="openai-and-anthropic-ipo-rumors-and-ai-valuation-signals",
            summary=(
                "A grounded news analysis of what IPO rumors can signal for "
                "venture sentiment, startup multiples, and public-market "
                "expectations around artificial intelligence companies."
            ),
            sections=[
                BlogSection(heading="Headline Context", body_markdown=" ".join(["word"] * 200)),
                BlogSection(heading="Market Signals", body_markdown=" ".join(["word"] * 210)),
                BlogSection(heading="Investor Readthrough", body_markdown=" ".join(["word"] * 220)),
            ],
            tags=["startup-valuations", "ai-investing", "ipo-rumors"],
            seo_title="What OpenAI and Anthropic IPO Rumors Signal for AI Valuations",
            seo_description=(
                "Understand how OpenAI and Anthropic IPO rumors can affect "
                "investor confidence, startup valuation narratives, and "
                "artificial intelligence market sentiment."
            ),
        )
        return post, 0.2, True, [{"title": "Source", "url": "https://example.com"}]

    async def fake_taxonomy_suggestion(*args, **kwargs):
        return BlogTaxonomySuggestion(
            category=BlogTaxonomyCategory(
                id=53,
                name="Creator Business",
                slug="creator-economy-and-monetization",
                parent_id=50,
            ),
            tags=[
                BlogTaxonomyTag(id=150, name="Artificial Intelligence", slug="artificial-intelligence", category_id=45),
                BlogTaxonomyTag(id=151, name="Startup Valuations", slug="startup-valuations", category_id=51),
            ],
        )

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)
    monkeypatch.setattr(
        BlogTaxonomyService,
        "suggest_for_generated_post",
        fake_taxonomy_suggestion,
        raising=True,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "What OpenAI and Anthropic IPO rumors mean for investor confidence in artificial intelligence startup valuations today.",
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["resolved_keywords"]
    assert "Artificial Intelligence" in data["resolved_keywords"]


@pytest.mark.asyncio
async def test_get_blog_options_exposes_web_search_default(app, monkeypatch):
    monkeypatch.setattr(settings, "NVIDIA_API_KEY", "test-key")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/v1/ai/blog/options")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["use_web_search_default"] is True
    assert data["blog_types"][0]["value"] == "news"
    model_values = [model["value"] for model in data["models"]]
    assert model_values == ["glm-5.1"]
    assert data["models"][0]["provider_type"] == "nvidia"
    assert "gpt-5.4" not in model_values


@pytest.mark.asyncio
async def test_generate_blog_rejects_paused_gpt_model_before_generation(app, monkeypatch):
    called = False

    async def fake_blog_generate(self, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("Paused model should be rejected before generation")

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/v1/ai/generate/blog",
            json={
                "topic": "Build an AI article writer",
                "model": "gpt-5.4",
                "save_draft": False,
                "publish_post": False,
            },
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported blog model" in resp.json()["detail"]
    assert called is False


@pytest.mark.asyncio
async def test_generate_blog_quality_error_returns_400(app, monkeypatch):
    async def fake_blog_generate(self, **kwargs):
        raise ValueError("Quality validation failed after retry")

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Build an AI article writer",
            "blog_type": "how-to",
            "word_count": "medium",
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_blog_timeout_returns_504(app, monkeypatch):
    async def fake_blog_generate(self, **kwargs):
        raise TimeoutError("blog generation timed out")

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Build an AI article writer",
            "blog_type": "how-to",
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)

    assert resp.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert DEFAULT_MODEL in resp.json()["detail"]
    assert "timed out" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_blog_publish_persists_quality_metadata(app, monkeypatch):
    from schemas.ai import (
        BlogPost,
        BlogSection,
        BlogTaxonomyCategory,
        BlogTaxonomySuggestion,
        BlogTaxonomyTag,
    )

    async def fake_blog_generate(self, **kwargs):
        post = BlogPost(
            title="How to Ship Reliable AI Content Pipelines in Production",
            slug="how-to-ship-reliable-ai-content-pipelines-in-production",
            summary=(
                "A practical guide to designing phased AI content workflows with "
                "deterministic checks, metrics capture, and publish-ready outputs "
                "that are easier to monitor and improve over time."
            ),
            sections=[
                BlogSection(heading="Introduction", body_markdown=" ".join(["word"] * 210)),
                BlogSection(heading="Research and Grounding", body_markdown=" ".join(["word"] * 220)),
                BlogSection(heading="Drafting and Revision", body_markdown=" ".join(["word"] * 230)),
                BlogSection(heading="Conclusion and Next Steps", body_markdown=" ".join(["word"] * 210)),
            ],
            tags=["ai-writing", "quality-metrics", "content-ops"],
            seo_title="How to Ship Reliable AI Content Pipelines",
            seo_description=(
                "Learn how to persist quality checks and phase metrics in an AI "
                "content pipeline so publishing workflows stay observable and "
                "auditable in production."
            ),
        )
        return post, 0.33, True, [{"title": "Source", "url": "https://example.com"}]

    async def fake_taxonomy_suggestion(*args, **kwargs):
        return BlogTaxonomySuggestion(
            category=BlogTaxonomyCategory(
                id=45,
                name="Artificial Intelligence",
                slug="artificial-intelligence",
                parent_id=44,
            ),
            tags=[
                BlogTaxonomyTag(id=101, name="AI", slug="ai", category_id=45),
                BlogTaxonomyTag(id=104, name="LLMs", slug="llms", category_id=45),
            ],
        )

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)
    monkeypatch.setattr(
        BlogAgentService,
        "blog_post_to_html",
        lambda self, blog_post: "<p>stub html</p>",
        raising=True,
    )
    monkeypatch.setattr(
        BlogTaxonomyService,
        "suggest_for_generated_post",
        fake_taxonomy_suggestion,
        raising=True,
    )

    captured = {}

    async def fake_create_post(session, post_data, author_id):
        captured["post_data"] = post_data

        class _CreatedPost:
            uuid = "post-uuid-123"

        return _CreatedPost()

    async def fake_get_post_by_slug(session, slug, include_deleted=False):
        return None

    async def fake_publish_post(session, post_uuid, current_user, **kwargs):
        class _PublishedPost:
            uuid = post_uuid

        return _PublishedPost()

    monkeypatch.setattr(PostService, "create_post", fake_create_post, raising=True)
    monkeypatch.setattr(PostService, "get_post_by_slug", fake_get_post_by_slug, raising=True)
    monkeypatch.setattr(PostService, "publish_post", fake_publish_post, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Ship a production AI article pipeline",
            "blog_type": "how-to",
            "keywords": ["ai pipeline", "quality metrics"],
            "word_count": "medium",
            "save_draft": False,
            "publish_post": True,
            "is_published": True,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["post_id"] == "post-uuid-123"

    persisted = captured["post_data"].content_blocks
    assert "ai_generation" in persisted
    assert persisted["ai_generation"]["generator"] == "blog-agent"
    assert persisted["ai_generation"]["resolved_keywords"][:2] == ["AI Pipeline", "Quality Metrics"]
    assert "quality_report" in persisted["ai_generation"]
    assert "phase_metrics" in persisted["ai_generation"]
    assert persisted["ai_generation"]["taxonomy_suggestion"]["category"]["id"] == 45
    assert captured["post_data"].category_id == 45
    assert captured["post_data"].tag_ids == [101, 104]


@pytest.mark.asyncio
async def test_generate_blog_publish_uses_unique_slug_on_collision(app, monkeypatch):
    from schemas.ai import BlogPost, BlogSection, BlogTaxonomySuggestion

    async def fake_blog_generate(self, **kwargs):
        post = BlogPost(
            title="AI in Journalism: The Transparency and Trust Crisis",
            slug="ai-in-journalism-the-transparency-and-trust-crisis",
            summary=(
                "A practical article about AI journalism transparency, trust, "
                "editorial labeling, and reader expectations for generated content."
            ),
            sections=[
                BlogSection(heading="Why This Matters", body_markdown=" ".join(["word"] * 120)),
                BlogSection(heading="What Changes Now", body_markdown=" ".join(["word"] * 120)),
                BlogSection(heading="What To Do Next", body_markdown=" ".join(["word"] * 120)),
            ],
            tags=["artificial-intelligence", "journalism"],
            seo_title="AI Journalism Transparency and Reader Trust",
            seo_description=(
                "Learn how AI journalism transparency, labeling, and editorial review "
                "can help publishers build reader trust in generated content."
            ),
        )
        return post, 0.12, False, None

    async def fake_taxonomy_suggestion(*args, **kwargs):
        return BlogTaxonomySuggestion()

    class _ExistingPost:
        slug = "ai-in-journalism-the-transparency-and-trust-crisis"

    captured = {}

    async def fake_get_post_by_slug(session, slug, include_deleted=False):
        return _ExistingPost()

    async def fake_generate_unique_slug(session, title, model):
        return "ai-in-journalism-the-transparency-and-trust-crisis-2"

    async def fake_create_post(session, post_data, author_id):
        captured["post_data"] = post_data

        class _CreatedPost:
            uuid = "post-uuid-unique"

        return _CreatedPost()

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)
    monkeypatch.setattr(BlogAgentService, "blog_post_to_html", lambda self, post: "<p>html</p>", raising=True)
    monkeypatch.setattr(BlogTaxonomyService, "suggest_for_generated_post", fake_taxonomy_suggestion, raising=True)
    monkeypatch.setattr(PostService, "get_post_by_slug", fake_get_post_by_slug, raising=True)
    monkeypatch.setattr(PostService, "generate_unique_slug", fake_generate_unique_slug, raising=True)
    monkeypatch.setattr(PostService, "create_post", fake_create_post, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/v1/ai/generate/blog",
            json={
                "topic": "AI in journalism transparency",
                "publish_post": True,
                "save_draft": False,
            },
        )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["blog_post"]["slug"] == "ai-in-journalism-the-transparency-and-trust-crisis-2"
    assert captured["post_data"].slug == "ai-in-journalism-the-transparency-and-trust-crisis-2"
