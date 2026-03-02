import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from routers.v1.ai import router as ai_router
from services.ai.generator import AIGeneratorService
from services.ai.blog_agent import BlogAgentService
from services.post import PostService
from services.user.auth import get_current_active_user
from database.connection import get_db_session


class DummyUser:
    def __init__(self, user_id: int = 1):
        self.id = user_id


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
                {"content": "<p>ok</p>", "metadata": {"words": 1, "model": "openai"}}
            ],
            "tool_id": kwargs.get("tool_id"),
            "model_used": kwargs.get("model", "gpt-3.5-turbo"),
            "generation_time": 0.01,
        }

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "tool_id": "blog-ideas",
            "model": "gpt-3.5-turbo",
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
        assert data["model_used"] == "gpt-3.5-turbo"
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
            "model": "gpt-3.5-turbo",
            "params": {},
        }
        resp = await ac.post("/v1/ai/generate", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_blog_ok_without_save_or_publish(app, monkeypatch):
    from schemas.ai import BlogPost, BlogSection

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

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)

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
async def test_get_blog_options_excludes_full_web_search_mode(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/v1/ai/blog/options")

    assert resp.status_code == status.HTTP_200_OK
    modes = resp.json().get("web_search_modes", [])
    mode_values = {mode["value"] for mode in modes}
    assert "full" not in mode_values
    assert mode_values == {"off", "basic"}


@pytest.mark.asyncio
async def test_generate_blog_rejects_full_web_search_mode(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Build an AI article writer",
            "blog_type": "how-to",
            "word_count": "medium",
            "web_search_mode": "full",
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_generate_blog_maps_web_search_toggle_to_mode(app, monkeypatch):
    from schemas.ai import BlogPost, BlogSection

    captured = {}

    async def fake_blog_generate(self, **kwargs):
        captured["web_search_mode"] = kwargs.get("web_search_mode")
        post = BlogPost(
            title="How to Build Reliable AI Writing Pipelines",
            slug="how-to-build-reliable-ai-writing-pipelines",
            summary=(
                "This practical guide explains how to design resilient multi-step AI content workflows "
                "with validation, retries, and quality checks for consistently publishable output."
            ),
            sections=[
                BlogSection(heading="Introduction", body_markdown=" ".join(["word"] * 200)),
                BlogSection(heading="Research", body_markdown=" ".join(["word"] * 220)),
                BlogSection(heading="Implementation", body_markdown=" ".join(["word"] * 230)),
                BlogSection(heading="Conclusion and Next Steps", body_markdown=" ".join(["word"] * 210)),
            ],
            tags=["ai-writing", "reliability", "content-ops"],
            seo_title="Reliable AI Writing Pipelines",
            seo_description=(
                "Learn to build robust AI writing workflows with retries, structured validation, "
                "and quality checks that keep production content pipelines dependable over time."
            ),
        )
        return post, 0.2, False, None

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "topic": "Build an AI article writer",
            "blog_type": "how-to",
            "word_count": "medium",
            "web_search": False,
            "save_draft": False,
            "publish_post": False,
        }
        resp = await ac.post("/v1/ai/generate/blog", json=payload)

    assert resp.status_code == status.HTTP_200_OK
    assert captured["web_search_mode"] == "off"


@pytest.mark.asyncio
async def test_generate_blog_publish_persists_quality_metadata(app, monkeypatch):
    from schemas.ai import BlogPost, BlogSection

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

    monkeypatch.setattr(BlogAgentService, "generate", fake_blog_generate, raising=True)
    monkeypatch.setattr(
        BlogAgentService,
        "blog_post_to_html",
        lambda self, blog_post: "<p>stub html</p>",
        raising=True,
    )

    captured = {}

    async def fake_create_post(session, post_data, author_id):
        captured["post_data"] = post_data

        class _CreatedPost:
            uuid = "post-uuid-123"

        return _CreatedPost()

    monkeypatch.setattr(PostService, "create_post", fake_create_post, raising=True)

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
    assert "quality_report" in persisted["ai_generation"]
    assert "phase_metrics" in persisted["ai_generation"]
