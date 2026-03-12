import pytest

from schemas.ai import BlogPost, BlogSection
from services.ai.blog_agent import BlogAgentService


class _FakeResult:
    def __init__(self, data):
        self.data = data


class _FakeAgent:
    responses = []
    call_count = 0

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, prompt, model_settings=None):
        idx = _FakeAgent.call_count
        _FakeAgent.call_count += 1
        data = _FakeAgent.responses[min(idx, len(_FakeAgent.responses) - 1)]
        return _FakeResult(data)


class _FallbackRetryAgent:
    text_attempt_count = 0

    def __init__(self, *args, result_type=None, **kwargs):
        self.result_type = result_type

    async def run(self, prompt, model_settings=None):
        if self.result_type is BlogPost:
            raise Exception("Exceeded maximum retries (1) for result validation")

        _FallbackRetryAgent.text_attempt_count += 1
        if _FallbackRetryAgent.text_attempt_count == 1:
            raise Exception("Received empty model response")

        payload = {
            "title": "How to Build Reliable AI Writing Pipelines",
            "slug": "how-to-build-reliable-ai-writing-pipelines",
            "summary": (
                "This practical guide explains how to design resilient multi-step AI content workflows "
                "with validation, retries, and quality checks for consistently publishable output."
            ),
            "sections": [
                {
                    "heading": "Introduction",
                    "body_markdown": " ".join(["word"] * 120),
                },
                {
                    "heading": "Research Strategy",
                    "body_markdown": " ".join(["word"] * 120),
                },
                {
                    "heading": "Drafting Workflow",
                    "body_markdown": " ".join(["word"] * 120),
                },
                {
                    "heading": "Conclusion and Next Steps",
                    "body_markdown": " ".join(["word"] * 120),
                },
            ],
            "tags": ["ai-writing", "reliability", "content-ops"],
            "seo_title": "Reliable AI Writing Pipelines for Production Teams",
            "seo_description": (
                "Learn to build robust AI writing workflows with retries, structured validation, "
                "and quality checks that keep production content pipelines dependable over time."
            ),
        }
        return _FakeResult(str(payload).replace("'", '"'))


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


@pytest.mark.asyncio
async def test_generate_retries_on_quality_issues(monkeypatch):
    service = BlogAgentService()

    monkeypatch.setattr(BlogAgentService, "_get_model_for_name", lambda self, model_name: object())
    monkeypatch.setattr("services.ai.blog_agent.Agent", _FakeAgent)

    _FakeAgent.call_count = 0
    _FakeAgent.responses = [
        _build_blog(80),   # too short overall for medium
        _build_blog(150),  # valid on retry
    ]

    blog_post, generation_time, web_search_used, sources = await service.generate(
        topic="Building a reliable AI blog writer",
        blog_type="how-to",
        keywords=["pydantic ai", "ai blog writer"],
        word_count="medium",
        web_search_mode="off",
    )

    assert isinstance(blog_post, BlogPost)
    assert sum(len(s.body_markdown.split()) for s in blog_post.sections) >= 420
    assert _FakeAgent.call_count >= 2
    assert generation_time >= 0
    assert web_search_used is False
    assert sources is None


@pytest.mark.asyncio
async def test_generate_returns_best_effort_when_quality_persists(monkeypatch):
    """
    When quality issues remain after the editorial revision, the pipeline now
    returns the best-effort revised post rather than raising. This prevents
    a perfectly readable post from being discarded due to minor metric misses.
    """
    service = BlogAgentService()

    monkeypatch.setattr(BlogAgentService, "_get_model_for_name", lambda self, model_name: object())
    monkeypatch.setattr("services.ai.blog_agent.Agent", _FakeAgent)

    _FakeAgent.call_count = 0
    _FakeAgent.responses = [
        _build_blog(80),
        _build_blog(90),
    ]

    # Should NOT raise — returns a result even if quality checks still fire
    blog_post, gen_time, web_search_used, sources = await service.generate(
        topic="Building a reliable AI blog writer",
        blog_type="how-to",
        keywords=["pydantic ai", "ai blog writer"],
        word_count="medium",
        web_search_mode="off",
    )
    assert blog_post is not None
    assert blog_post.title


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


def test_select_model_phase_falls_back_when_online_unavailable(monkeypatch):
    service = BlogAgentService()

    def _fail_online(_model_name):
        raise ValueError("online unavailable")

    monkeypatch.setattr("services.ai.blog_agent.get_model_with_online", _fail_online)
    monkeypatch.setattr(BlogAgentService, "_get_model_for_name", lambda self, model_name: object())

    model_obj, used_online = service._select_model_phase(
        model="claude-sonnet-4.6",
        web_search_mode="enhanced",
    )

    assert model_obj is not None
    assert used_online is False


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


@pytest.mark.asyncio
async def test_run_generation_once_retries_text_fallback_on_empty_response(monkeypatch):
    service = BlogAgentService()
    monkeypatch.setattr("services.ai.blog_agent.Agent", _FallbackRetryAgent)

    _FallbackRetryAgent.text_attempt_count = 0

    blog_post, usage = await service._run_generation_once(
        pydantic_model=object(),
        prompt="Write a blog post about resilient AI writing pipelines.",
        creativity=0.6,
        word_count="short",
    )

    assert isinstance(blog_post, BlogPost)
    assert blog_post.title == "How to Build Reliable AI Writing Pipelines"
    assert _FallbackRetryAgent.text_attempt_count == 2
    assert usage is None
