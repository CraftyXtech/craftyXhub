import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from schemas.ai import BlogPost, BlogSection
from services.ai.blog_agent import BlogAgentService, BlogGenerationDeps


def _mk_words(count: int) -> str:
    return " ".join(["contentword"] * count)


def _build_blog(word_per_section: int) -> BlogPost:
    return BlogPost(
        title="How to Build Reliable Multi-Step AI Content Pipelines",
        slug="how-to-build-reliable-multi-step-ai-content-pipelines",
        summary=(
            "This guide explains how to design a robust content pipeline with explicit research, "
            "outline, drafting, and editorial checks so generated articles are factual, readable, "
            "and publication-ready without brittle post-processing steps."
        ),
        sections=[
            BlogSection(heading="Introduction", body_markdown=_mk_words(word_per_section)),
            BlogSection(heading="Research Workflow", body_markdown=_mk_words(word_per_section)),
            BlogSection(heading="Drafting Strategy", body_markdown=_mk_words(word_per_section)),
            BlogSection(heading="Conclusion and Next Steps", body_markdown=_mk_words(word_per_section)),
        ],
        tags=["ai-writing", "pydantic-ai", "content-strategy"],
        seo_title="Build Better AI Blog Writers with Pydantic AI",
        seo_description=(
            "Learn how to build a production-ready AI blog writer with "
            "Pydantic AI using structured outputs and deterministic quality "
            "checks for better publishing outcomes."
        ),
    )


def _deps() -> BlogGenerationDeps:
    return BlogGenerationDeps(
        current_date_utc=datetime.now(timezone.utc).isoformat(),
        current_year=datetime.now(timezone.utc).year,
        topic="Build an AI writer",
        blog_type="how-to",
        keywords_text="pydantic ai, ai writer",
        tone="professional",
        language="en-US",
        length_tier="medium",
        section_guidance="Use sections: Intro, Steps, Conclusion",
        search_context="",
        timeliness_rules="Use current year",
        markdown_rules="Use markdown lists",
    )


def test_build_outline_guidance_contains_keywords_and_sections():
    service = BlogAgentService()
    guidance = service._build_outline_guidance(
        topic="Build a reliable AI blog writer",
        blog_type="how-to",
        keywords=["pydantic ai", "blog writer"],
        sources=[{"title": "Official docs"}],
    )

    assert "STRUCTURE GUIDANCE" in guidance
    assert "pydantic ai, blog writer" in guidance
    assert "Step-by-Step Implementation" in guidance
    assert "Official docs" in guidance


def test_collect_quality_issues_flags_ai_tropes():
    service = BlogAgentService()
    blog_post = _build_blog(250)
    blog_post.sections[0].body_markdown = (
        "Let us delve into the topic. " + blog_post.sections[0].body_markdown
    )

    issues = service._collect_quality_issues(
        blog_post=blog_post,
        word_count="medium",
        keywords=["pydantic ai"],
    )

    assert any("clich" in issue.lower() or "tropes" in issue.lower() for issue in issues)


def test_collect_quality_issues_flags_missing_primary_keyword_in_seo():
    service = BlogAgentService()
    blog_post = _build_blog(250)
    blog_post.seo_title = "Build Better AI Blog Writers"
    blog_post.seo_description = (
        "A practical workflow for robust AI article generation and editorial quality checks."
    )

    issues = service._collect_quality_issues(
        blog_post=blog_post,
        word_count="medium",
        keywords=["pydantic ai"],
    )

    assert any("seo_title" in issue for issue in issues)
    assert any("seo_description" in issue for issue in issues)


def test_build_quality_report_returns_expected_shape():
    service = BlogAgentService()
    blog_post = _build_blog(250)

    report = service.build_quality_report(
        blog_post=blog_post,
        word_count="medium",
        keywords=["pydantic ai"],
        phase_metrics={"timings_ms": {"total": 123.45}},
    )

    assert report["target_length"] == "medium"
    assert report["body_word_count"] > 0
    assert isinstance(report["section_word_counts"], list)
    assert "readability" in report
    assert "issues" in report
    assert "passed" in report
    assert "phase_metrics" in report
    assert report["phase_metrics"]["timings_ms"]["total"] == 123.45


def test_normalize_inline_ordered_list_splits_items_to_new_lines():
    service = BlogAgentService()
    body = (
        "Follow these steps to launch your software sales in Kenya: "
        "1. Define your pricing model with one-off, subscription, or usage tiers. "
        "2. Integrate a local payment gateway for M-Pesa and card support. "
        "3. Set up a storefront optimized for local buyers."
    )

    normalized = service._normalize_section_markdown(body)

    assert "\n1. Define your pricing model" in normalized
    assert "\n2. Integrate a local payment gateway" in normalized
    assert "\n3. Set up a storefront" in normalized


def test_validate_and_create_blog_post_normalizes_inline_steps():
    service = BlogAgentService()
    steps_body = (
        "Follow these steps to launch your software sales in Kenya: "
        "1. Define your pricing model with one-off, subscription, or usage tiers. "
        "2. Integrate a local payment gateway for M-Pesa and card support. "
        "3. Set up a storefront optimized for local buyers."
    )
    post = service._validate_and_create_blog_post(
        {
            "title": "How to Launch Software Sales in Kenya",
            "slug": "how-to-launch-software-sales-in-kenya",
            "summary": (
                "A practical guide for launching software sales in Kenya with the right "
                "pricing, payments, localization, and support workflows."
            ),
            "sections": [
                {
                    "heading": "Step-by-Step Implementation",
                    "body_markdown": steps_body,
                },
                {
                    "heading": "Conclusion and Next Steps",
                    "body_markdown": _mk_words(80),
                },
            ],
            "tags": ["kenya", "saas", "localization"],
            "seo_title": "Launch Software Sales in Kenya",
            "seo_description": (
                "Learn how to launch software sales in Kenya using local payment methods, "
                "practical distribution channels, and customer support strategies."
            ),
        }
    )

    body = post.sections[0].body_markdown
    assert "\n1. Define your pricing model" in body
    assert "\n2. Integrate a local payment gateway" in body
    assert "\n3. Set up a storefront" in body


def test_validate_and_create_blog_post_updates_stale_title_year():
    service = BlogAgentService()
    current_year = datetime.now(timezone.utc).year
    post = service._validate_and_create_blog_post(
        {
            "title": "How to Sell Software in Kenya: A Complete 2024 Guide",
            "slug": "how-to-sell-software-in-kenya",
            "summary": (
                "A practical guide for selling software in Kenya with local payment "
                "support, channel strategy, and customer success foundations."
            ),
            "sections": [
                {
                    "heading": "Introduction",
                    "body_markdown": _mk_words(90),
                },
                {
                    "heading": "Conclusion and Next Steps",
                    "body_markdown": _mk_words(90),
                },
            ],
            "tags": ["kenya", "saas", "sales"],
            "seo_title": "Complete 2024 Guide to Selling Software in Kenya",
            "seo_description": (
                "Learn practical steps to sell software in Kenya using local payment "
                "rails and market-specific go-to-market execution."
            ),
        }
    )

    assert str(current_year) in post.title
    assert str(current_year) in post.seo_title
    assert "2024" not in post.title


def test_collect_quality_issues_flags_stale_year_mentions():
    service = BlogAgentService()
    blog_post = _build_blog(250)
    blog_post.sections[0].body_markdown = (
        "In 2024, many teams used early playbooks. " + blog_post.sections[0].body_markdown
    )

    issues = service._collect_quality_issues(
        blog_post=blog_post,
        word_count="medium",
        keywords=["pydantic ai"],
    )

    assert any("outdated year references" in issue for issue in issues)


def test_get_max_tokens_is_tuned_for_target_lengths():
    service = BlogAgentService()
    assert service._get_max_tokens("short") == 1500
    assert service._get_max_tokens("medium") == 2500
    assert service._get_max_tokens("long") == 4000
    assert service._get_max_tokens("very-long") == 6000


@pytest.mark.asyncio
async def test_run_structured_runner_strict_attempts_single_model(monkeypatch):
    service = BlogAgentService()

    class _FakeUsage:
        input_tokens = 10
        output_tokens = 20
        total_tokens = 30
        requests = 1

    class _FakeResult:
        def __init__(self, output):
            self.output = output

        def usage(self):
            return _FakeUsage()

    class _FakeAgent:
        async def run(self, *args, **kwargs):
            return _FakeResult(_build_blog(90))

    monkeypatch.setattr("services.ai.blog_agent.get_model_from_id", lambda model_id: model_id)
    monkeypatch.setattr(service, "_build_structured_blog_agent", lambda _model: _FakeAgent())

    blog_post, usage, effective_model, attempted, errors = await service._run_structured_runner(
        model_ids=["anthropic/claude-sonnet-4.6"],
        prompt="Write blog",
        deps=_deps(),
        creativity=0.7,
        max_tokens=2500,
        execution_mode="strict",
    )

    assert isinstance(blog_post, BlogPost)
    assert usage is not None
    assert usage["total_tokens"] == 30
    assert effective_model == "anthropic/claude-sonnet-4.6"
    assert attempted == ["anthropic/claude-sonnet-4.6"]
    assert errors == []


@pytest.mark.asyncio
async def test_run_structured_runner_resilient_fails_over(monkeypatch):
    service = BlogAgentService()

    class _FakeResult:
        def __init__(self, output):
            self.output = output

        def usage(self):
            return None

    class _FakeAgent:
        def __init__(self, model_id: str):
            self.model_id = model_id

        async def run(self, *args, **kwargs):
            if self.model_id.endswith("first"):
                raise RuntimeError("provider failure")
            return _FakeResult(_build_blog(90))

    monkeypatch.setattr("services.ai.blog_agent.supports_native_fallback_model", lambda: False)
    monkeypatch.setattr("services.ai.blog_agent.get_model_from_id", lambda model_id: model_id)
    monkeypatch.setattr(service, "_build_structured_blog_agent", lambda model_id: _FakeAgent(model_id))

    blog_post, usage, effective_model, attempted, errors = await service._run_structured_runner(
        model_ids=["model/first", "model/second"],
        prompt="Write blog",
        deps=_deps(),
        creativity=0.7,
        max_tokens=2500,
        execution_mode="resilient",
    )

    assert isinstance(blog_post, BlogPost)
    assert usage is None
    assert effective_model == "model/second"
    assert attempted == ["model/first", "model/second"]
    assert len(errors) == 1
    assert errors[0]["type"] in ("provider_error", "schema_validation_error")


@pytest.mark.asyncio
async def test_run_compat_json_runner_retries_transient_then_succeeds(monkeypatch):
    service = BlogAgentService()

    valid_payload = _build_blog(90).model_dump()
    valid_json = json.dumps(valid_payload)

    class _FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    post_calls = {"n": 0}

    async def _post(*args, **kwargs):
        post_calls["n"] += 1
        if post_calls["n"] == 1:
            raise httpx.TimeoutException("timed out")
        return _FakeResponse(
            {
                "choices": [{"message": {"content": valid_json}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 500,
                    "total_tokens": 600,
                },
            }
        )

    with patch("services.ai.blog_agent.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = _post
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        blog_post, usage, effective_model, attempted, errors = await service._run_compat_json_runner(
            model_ids=["openai/gpt-5.2"],
            prompt="Write blog",
            deps=_deps(),
            creativity=0.7,
            max_tokens=2500,
            execution_mode="strict",
        )

    assert isinstance(blog_post, BlogPost)
    assert usage is not None
    assert usage["total_tokens"] == 600
    assert effective_model == "openai/gpt-5.2"
    assert attempted == ["openai/gpt-5.2"]
    assert len(errors) == 1
    assert errors[0]["type"] == "timeout_error"
    assert post_calls["n"] == 2


@pytest.mark.asyncio
async def test_generate_sets_ddg_attempted_metric_by_mode(monkeypatch):
    service = BlogAgentService()

    monkeypatch.setattr(
        service,
        "_resolve_execution_path",
        lambda _model: "structured",
    )
    monkeypatch.setattr(
        "services.ai.blog_agent.build_blog_model_chain",
        lambda **kwargs: ["anthropic/claude-sonnet-4.6"],
    )

    async def _fake_structured_runner(**kwargs):
        return _build_blog(90), {"total_tokens": 123}, "anthropic/claude-sonnet-4.6", ["anthropic/claude-sonnet-4.6"], []

    monkeypatch.setattr(service, "_run_structured_runner", _fake_structured_runner)

    monkeypatch.setattr(
        BlogAgentService,
        "_research_phase",
        lambda self, topic, keywords, web_search_mode, blog_type: ("", [], False),
        raising=True,
    )

    await service.generate(
        topic="Launch SaaS in Kenya",
        blog_type="how-to",
        word_count="medium",
        web_search_mode="basic",
        execution_mode="strict",
    )
    metrics = service.get_last_phase_metrics()
    assert metrics["web_grounding"]["ddg_attempted"] is True
    assert metrics["web_grounding"]["online_used"] is False
    assert metrics["model_runtime"]["execution_mode"] == "strict"

    await service.generate(
        topic="Launch SaaS in Kenya",
        blog_type="how-to",
        word_count="medium",
        web_search_mode="enhanced",
        execution_mode="strict",
    )
    metrics = service.get_last_phase_metrics()
    assert metrics["web_grounding"]["ddg_attempted"] is False
    assert metrics["web_grounding"]["online_used"] is True


@pytest.mark.asyncio
async def test_generate_routes_to_compat_path_for_non_structured_model(monkeypatch):
    service = BlogAgentService()

    monkeypatch.setattr(service, "_resolve_execution_path", lambda _model: "compat_json")
    monkeypatch.setattr(
        "services.ai.blog_agent.build_blog_model_chain",
        lambda **kwargs: ["qwen/qwen3-235b-a22b"],
    )

    async def _fake_compat_runner(**kwargs):
        return _build_blog(90), None, "qwen/qwen3-235b-a22b", ["qwen/qwen3-235b-a22b"], []

    monkeypatch.setattr(service, "_run_compat_json_runner", _fake_compat_runner)
    monkeypatch.setattr(
        BlogAgentService,
        "_research_phase",
        lambda self, topic, keywords, web_search_mode, blog_type: ("", [], False),
        raising=True,
    )

    blog_post, generation_time, web_search_used, sources = await service.generate(
        topic="Build resilient blogging systems",
        blog_type="how-to",
        word_count="medium",
        model="qwen3-235b",
        execution_mode="strict",
        web_search_mode="off",
    )

    assert isinstance(blog_post, BlogPost)
    assert generation_time >= 0
    assert web_search_used is False
    assert sources in (None, [])
    metrics = service.get_last_phase_metrics()
    assert metrics["model_runtime"]["execution_path"] == "compat_json"
    assert metrics["model_runtime"]["model_used"] == "qwen/qwen3-235b-a22b"


@pytest.mark.asyncio
async def test_generate_defaults_to_strict_mode_when_execution_mode_missing(monkeypatch):
    service = BlogAgentService()

    captured = {"mode": None}

    monkeypatch.setattr(service, "_resolve_execution_path", lambda _model: "structured")
    monkeypatch.setattr(
        "services.ai.blog_agent.build_blog_model_chain",
        lambda **kwargs: ["anthropic/claude-sonnet-4.6", "openai/gpt-5.2"],
    )

    async def _fake_structured_runner(**kwargs):
        captured["mode"] = kwargs["execution_mode"]
        return _build_blog(90), None, "anthropic/claude-sonnet-4.6", ["anthropic/claude-sonnet-4.6"], []

    monkeypatch.setattr(service, "_run_structured_runner", _fake_structured_runner)
    monkeypatch.setattr(
        BlogAgentService,
        "_research_phase",
        lambda self, topic, keywords, web_search_mode, blog_type: ("", [], False),
        raising=True,
    )

    await service.generate(
        topic="Alias behavior",
        blog_type="how-to",
        word_count="medium",
        execution_mode=None,
        web_search_mode="off",
    )

    assert captured["mode"] == "strict"
