import pytest

from schemas.ai import BlogPost, BlogSection
from services.ai.blog_agent import BlogAgentService


class _FakeResult:
    def __init__(self, data):
        self.data = data
        self.output = data


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

    def __init__(self, *args, output_type=None, **kwargs):
        assert "result_type" not in kwargs
        self.output_type = output_type

    async def run(self, prompt, model_settings=None):
        if self.output_type is BlogPost:
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
            "hero_image_prompt": (
                "Editorial illustration of a content team reviewing AI drafts on large screens. "
                "Use a 1200x630 landscape composition for social sharing, no logos, no watermarks, "
                "no text overlay, strong focal subject."
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
        seo_title="Pydantic AI Workflow for Better Blog Writing Teams",
        seo_description=(
            "Learn how to build a production-ready AI blog writer with "
            "Pydantic AI using structured outputs and deterministic quality "
            "checks for better publishing outcomes."
        ),
        hero_image_prompt=(
            "Editorial desk scene with a writer reviewing an AI draft. "
            "Use a 1200x630 landscape composition for social sharing, no logos, "
            "no watermarks, no text overlay, strong focal subject."
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
        use_web_search=False,
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
        use_web_search=False,
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


def test_research_phase_skips_ddg_when_disabled(monkeypatch):
    service = BlogAgentService()
    state = {"called": False}

    class _SearchShouldNotRun:
        def __init__(self, *args, **kwargs):
            state["called"] = True

    monkeypatch.setattr("services.ai.blog_agent.WebSearchService", _SearchShouldNotRun)

    context, sources, used, attempted = service._research_phase(
        topic="AI search mode cleanup",
        keywords=["duckduckgo"],
        use_web_search=False,
    )

    assert state["called"] is False
    assert context == ""
    assert sources is None
    assert used is False
    assert attempted is False


def test_research_phase_uses_ddg_when_enabled(monkeypatch):
    service = BlogAgentService()
    state = {"called": False}

    class _FakeSearchService:
        def __init__(self, *args, **kwargs):
            pass

        def search_for_topic(self, topic, keywords):
            state["called"] = True
            assert topic == "AI search mode cleanup"
            assert keywords == ["duckduckgo"]
            return {
                "text_results": [],
                "news_results": [],
                "sources": [
                    {
                        "title": "DDG source",
                        "url": "https://example.com/ddg",
                        "snippet": "DuckDuckGo search result",
                    }
                ],
            }

        def format_as_context(self, search_results):
            assert search_results["sources"]
            return "formatted ddg context"

    monkeypatch.setattr("services.ai.blog_agent.WebSearchService", _FakeSearchService)

    context, sources, used, attempted = service._research_phase(
        topic="AI search mode cleanup",
        keywords=["duckduckgo"],
        use_web_search=True,
    )

    assert state["called"] is True
    assert context == "formatted ddg context"
    assert sources and sources[0]["title"] == "DDG source"
    assert used is True
    assert attempted is True


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


def test_collect_quality_issues_flags_social_metadata_even_without_keywords():
    service = BlogAgentService()
    blog_post = _build_blog(250)
    blog_post.seo_title = "Short title"
    blog_post.seo_description = "Too short."
    blog_post.hero_image_prompt = "Editorial AI writing scene."

    issues = service._collect_quality_issues(
        blog_post=blog_post,
        word_count="medium",
        keywords=None,
    )

    assert any("seo_title should be between" in issue for issue in issues)
    assert any("seo_description should be between" in issue for issue in issues)
    assert any("hero_image_prompt should specify a 1200x630" in issue for issue in issues)
    assert any("avoid logos" in issue.lower() for issue in issues)
    assert any("avoid watermarks" in issue.lower() for issue in issues)


def test_validate_and_create_blog_post_normalizes_dash_aside_punctuation():
    service = BlogAgentService()

    blog_post = service._validate_and_create_blog_post(
        {
            "title": "Quit Smoking Facts — What Your Body Does First",
            "slug": "quit-smoking-facts",
            "summary": (
                "Your body starts recovering faster than most people expect — and the first "
                "changes are measurable within hours."
            ),
            "sections": [
                {
                    "heading": "Introduction",
                    "body_markdown": "This is a grounded guide — not a scare tactic.",
                },
                {
                    "heading": "What changes first",
                    "body_markdown": (
                        "These changes are confirmed by the [CDC](https://www.cdc.gov/tobacco/about/how-to-quit.html) "
                        "— not marketing copy."
                    ),
                },
                {
                    "heading": "Conclusion and Next Steps",
                    "body_markdown": "Use support early — it improves your odds.",
                },
            ],
            "tags": ["quit-smoking", "health"],
            "seo_title": "Quit Smoking Facts — What Changes First",
            "seo_description": (
                "The first recovery milestones happen fast — and knowing them gives people a "
                "better reason to stick with the process."
            ),
        }
    )

    assert "—" not in blog_post.summary
    assert "—" not in blog_post.seo_description
    assert all("—" not in section.body_markdown for section in blog_post.sections)
    assert "[CDC](https://www.cdc.gov/tobacco/about/how-to-quit.html)" in blog_post.sections[1].body_markdown


def test_validate_and_create_blog_post_normalizes_social_metadata_and_hero_prompt():
    service = BlogAgentService()

    blog_post = service._validate_and_create_blog_post(
        {
            "title": "Prompt Engineering Tricks to Stop AI Hallucinations in Production Systems",
            "slug": "prompt-engineering-tricks-stop-ai-hallucinations",
            "summary": (
                "A practical breakdown of the prompt design habits, guardrails, and evaluation loops "
                "that reduce hallucinations before they reach production users."
            ),
            "sections": [
                {
                    "heading": "Introduction",
                    "body_markdown": _mk_words(120),
                },
                {
                    "heading": "What actually reduces hallucinations",
                    "body_markdown": _mk_words(120),
                },
                {
                    "heading": "Conclusion and Next Steps",
                    "body_markdown": _mk_words(120),
                },
            ],
            "tags": ["prompt-engineering", "ai-reliability"],
            "seo_title": "Prompt Engineering Tricks to Stop AI Hallucinations in Production Systems | CraftyXHub",
            "seo_description": (
                "Prompt engineering tactics that reduce hallucinations across model evaluation, "
                "retrieval, and production guardrails without slowing your team down."
            ),
            "hero_image_prompt": "Editorial illustration of an AI system under review.",
        }
    )

    assert len(blog_post.seo_title) <= 65
    assert "CraftyXHub" not in blog_post.seo_title
    assert len(blog_post.seo_description) <= 155
    assert "1200x630" in blog_post.hero_image_prompt
    assert "no logos" in blog_post.hero_image_prompt.lower()
    assert "no watermarks" in blog_post.hero_image_prompt.lower()
    assert "no text overlay" in blog_post.hero_image_prompt.lower()


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
