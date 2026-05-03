import pytest

from services.post import PostService
from models import Post


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _FakeSession:
    def __init__(self, existing_slugs):
        self.existing_slugs = set(existing_slugs)
        self.checked_slugs = []

    async def execute(self, query):
        slug = query.whereclause.right.value
        self.checked_slugs.append(slug)
        return _ScalarResult(slug if slug in self.existing_slugs else None)


@pytest.mark.asyncio
async def test_generate_unique_slug_adds_numeric_suffix_before_random_fallback():
    session = _FakeSession({"what_is_artificial_intelligence_a_complete"})

    slug = await PostService.generate_unique_slug(
        session,
        "What Is Artificial Intelligence? A Complete Beginner Guide",
        Post,
    )

    assert slug == "what_is_artificial_intelligence_a_complete-2"
    assert session.checked_slugs == [
        "what_is_artificial_intelligence_a_complete",
        "what_is_artificial_intelligence_a_complete-2",
    ]
