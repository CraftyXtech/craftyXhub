import pytest
import types

from services.ai.generator import AIGeneratorService


class FakeUsage:
    def __init__(self, total_tokens=123):
        self.total_tokens = total_tokens


class FakeRunResult:
    def __init__(self, text="<p>Generated content</p>", tokens=123):
        self.data = text
        self._tokens = tokens

    def usage(self):
        return FakeUsage(self._tokens)


class FakeAgent:
    async def run(self, prompt, model_settings=None):  # signature similar to pydantic-ai Agent
        assert isinstance(prompt, str)
        return FakeRunResult()


@pytest.mark.asyncio
async def test_generate_success_variants_count():
    service = AIGeneratorService()
    # Override agents with fakes regardless of env keys
    service.agents = {"openai": FakeAgent()}

    res = await service.generate(
        template_id="blog-ideas",
        model="openai",
        params={"category": "Tech", "keywords": "ai, ml", "audience": "devs"},
        tone="friendly",
        length="medium",
        language="en-US",
        creativity=0.4,
        variant_count=2,
    )

    assert res["model_used"] == "openai"
    assert res["template_id"] == "blog-ideas"
    assert isinstance(res["generation_time"], float)
    assert len(res["variants"]) == 2
    for v in res["variants"]:
        assert "content" in v and isinstance(v["content"], str)
        assert "metadata" in v and "words" in v["metadata"]


@pytest.mark.asyncio
async def test_generate_unknown_model_raises():
    service = AIGeneratorService()
    service.agents = {}  # ensure no agents configured
    with pytest.raises(ValueError) as ex:
        await service.generate(
            template_id="blog-ideas",
            model="openai",
            params={"category": "Tech", "keywords": "ai"},
        )
    assert "No AI models configured" in str(ex.value) or "not configured" in str(ex.value)


@pytest.mark.asyncio
async def test_generate_missing_template_params_raises():
    service = AIGeneratorService()
    service.agents = {"openai": FakeAgent()}
    with pytest.raises(ValueError):
        await service.generate(
            template_id="blog-ideas",
            model="openai",
            params={"keywords": "ai"},  # missing 'category'
        )
