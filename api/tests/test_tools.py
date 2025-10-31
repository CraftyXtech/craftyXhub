import pytest

from services.ai.tools import ToolHandler


def test_validate_params_success():
    params = {"category": "Tech", "keywords": "ai, ml", "audience": "devs"}
    # Should not raise
    ToolHandler.validate_params("blog-ideas", params)


def test_validate_params_missing_required():
    with pytest.raises(ValueError) as ex:
        ToolHandler.validate_params("blog-ideas", {"keywords": "ai"})
    assert "Missing required fields" in str(ex.value)


def test_build_prompt_includes_controls():
    params = {"category": "Tech", "keywords": "ai, ml", "audience": "devs"}
    prompt = ToolHandler.build_prompt(
        tool_id="blog-ideas",
        params=params,
        tone="professional",
        length="long",
        language="fr",
    )
    assert "Generate blog post ideas about Tech" in prompt
    assert "Keywords: ai, ml" in prompt
    assert "Tone: professional" in prompt
    assert "Length: 300-500 words" in prompt
    assert "Write in fr" in prompt


@pytest.mark.parametrize(
    "length,expected",
    [
        ("short", 200),
        ("medium", 600),
        ("long", 1000),
        ("very-long", 2000),
    ],
)
def test_get_max_tokens_mapping(length, expected):
    assert ToolHandler.get_max_tokens(length) == expected
