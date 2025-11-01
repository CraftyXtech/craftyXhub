import pytest

from services.ai.generator import AIGeneratorService


@pytest.mark.asyncio
async def test_all_16_tools_builds_prompts(monkeypatch):
    """Smoke-test that all tool_ids build prompts or accept freeform generation.
    We mock the agent run to avoid external API usage.
    """
    service = AIGeneratorService()

    class FakeResult:
        def __init__(self, text="<p>ok</p>"):
            self.data = text

        def usage(self):
            class U:
                total_tokens = 42
            return U()

    class FakeAgent:
        async def run(self, *_args, **_kwargs):
            return FakeResult()

    def fake_get_agent(self, model_name, system_prompt=None):
        return FakeAgent()

    monkeypatch.setattr(AIGeneratorService, "_get_agent_for_model", fake_get_agent)

    tools_to_test = [
        ("blog-ideas", {"category": "AI", "keywords": "machine learning"}),
        ("outline-generator", {"title": "AI Guide", "keywords": "ML"}),
        ("section-draft", {"outline": "I. Intro\nII. Body"}),
        ("title-variants", {"topic": "AI Tools", "keywords": "gpt"}),
        ("intro-conclusion-cta", {"title": "AI", "summary": "..", "cta_goal": "signup"}),
        ("seo-pack", {"content": "...", "focus_keyword": "ai tools"}),
        ("image-alt-text", {"image_context": "Team meeting"}),
        ("internal-link-suggester", {"content": "...", "available_slugs": "/blog/a,/blog/b"}),
        ("content-refiner", {"content": "Draft text"}),
        ("summarizer-brief", {"content": "Long text..."}),
        ("fact-checklist", {"content": "Claims here"}),
        ("style-adapter", {"content": "Text", "reading_level": "High School"}),
        # New tools
        ("social-media-post", {"platform": "linkedin", "topic": "AI trends", "cta_goal": "engagement"}),
        ("email-campaign", {"campaign_type": "promotional", "audience": "developers", "offer": "50% off"}),
        ("product-description", {"product_name": "Smart Watch", "features": "GPS", "benefits": "Track fitness", "target_audience": "Athletes"}),
        ("ad-copy-generator", {"platform": "google_rsa", "objective": "conversion", "audience": "SMBs", "offer": "Free trial"}),
    ]

    for tool_id, params in tools_to_test:
        res = await service.generate(
            tool_id=tool_id,
            model="gpt-5-mini",
            params=params,
            tone="professional",
            length="medium",
            language="en-US",
            variant_count=2,
            creativity=0.3,
        )
        assert res["tool_id"] == tool_id
        assert len(res["variants"]) >= 1
