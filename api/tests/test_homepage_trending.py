import pytest
from uuid import uuid4

from models import Category


STORY_FIXTURES = [
    {
        "title": "Makers Build Better Analytics Dashboards",
        "content": (
            "<p>Independent makers are redesigning analytics dashboards around calmer weekly routines, "
            "clearer customer signals, and practical operating metrics.</p>"
            '<p>Reference: <a href="https://example.com/maker-analytics">maker analytics notes</a>.</p>'
        ),
        "excerpt": (
            "A practical look at how independent makers are rebuilding analytics dashboards around "
            "clearer signals, calmer weekly review habits, and decisions that improve product work."
        ),
    },
    {
        "title": "Design Teams Rethink Accessible Navigation",
        "content": (
            "<p>Design teams are testing navigation patterns that improve keyboard movement, screen "
            "reader clarity, and faster route discovery across complex publishing products.</p>"
            '<p>Reference: <a href="https://example.com/accessible-navigation">accessible navigation notes</a>.</p>'
        ),
        "excerpt": (
            "Design teams are revisiting navigation patterns to improve keyboard movement, screen "
            "reader clarity, and faster route discovery across complex editorial products."
        ),
    },
    {
        "title": "Security Researchers Explain Safer API Tokens",
        "content": (
            "<p>Security researchers are publishing new guidance for API token rotation, scoped access, "
            "audit trails, and safer defaults in developer-facing platforms.</p>"
            '<p>Reference: <a href="https://example.com/api-token-safety">API token safety notes</a>.</p>'
        ),
        "excerpt": (
            "Security researchers explain practical API token rotation, scoped access, audit trails, "
            "and safer defaults for teams building developer-facing platforms."
        ),
    },
    {
        "title": "Community Writers Turn Notes Into Essays",
        "content": (
            "<p>Community writers are transforming rough research notes into polished essays using "
            "editorial calendars, peer review loops, and structured publishing rituals.</p>"
            '<p>Reference: <a href="https://example.com/editorial-workflows">editorial workflow notes</a>.</p>'
        ),
        "excerpt": (
            "Community writers are turning rough research notes into polished essays with editorial "
            "calendars, peer review loops, and structured publishing rituals."
        ),
    },
]


async def create_category(test_session):
    suffix = uuid4().hex[:8]
    category = Category(name=f"Homepage {suffix}", slug=f"homepage-{suffix}")
    test_session.add(category)
    await test_session.commit()
    await test_session.refresh(category)
    return category


async def create_published_post(client_author, category, index):
    story = STORY_FIXTURES[index - 1]
    response = await client_author.post(
        "/v1/posts/",
        data={
            "title": story["title"],
            "content": story["content"],
            "excerpt": story["excerpt"],
            "category_id": str(category.id),
            "is_published": "true",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_admin_picks_up_to_three_homepage_trending_posts(client_author, client_admin, client_public, test_session):
    category = await create_category(test_session)
    posts = [
        await create_published_post(client_author, category, index)
        for index in range(1, 5)
    ]

    for index, post in enumerate(posts[:3], start=1):
        response = await client_admin.put(
            f"/v1/posts/{post['uuid']}/homepage-trending",
            params={"trending": "true"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["is_homepage_trending"] is True
        assert body["homepage_trending_order"] == index

    full_response = await client_admin.put(
        f"/v1/posts/{posts[3]['uuid']}/homepage-trending",
        params={"trending": "true"},
    )
    assert full_response.status_code == 400, full_response.text
    assert "already has 3 picked posts" in full_response.json()["detail"]

    listing = await client_public.get("/v1/posts/homepage-trending")
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert [post["uuid"] for post in body["posts"]] == [post["uuid"] for post in posts[:3]]
    assert [post["homepage_trending_order"] for post in body["posts"]] == [1, 2, 3]


@pytest.mark.asyncio
async def test_admin_can_remove_homepage_trending_post(client_author, client_admin, client_public, test_session):
    category = await create_category(test_session)
    post = await create_published_post(client_author, category, 1)

    add_response = await client_admin.put(
        f"/v1/posts/{post['uuid']}/homepage-trending",
        params={"trending": "true"},
    )
    assert add_response.status_code == 200, add_response.text

    remove_response = await client_admin.put(
        f"/v1/posts/{post['uuid']}/homepage-trending",
        params={"trending": "false"},
    )
    assert remove_response.status_code == 200, remove_response.text
    body = remove_response.json()
    assert body["is_homepage_trending"] is False
    assert body["homepage_trending_order"] is None

    listing = await client_public.get("/v1/posts/homepage-trending")
    assert listing.status_code == 200, listing.text
    assert listing.json()["posts"] == []


@pytest.mark.asyncio
async def test_unpublish_clears_homepage_trending_slot(client_author, client_admin, client_public, test_session):
    category = await create_category(test_session)
    post = await create_published_post(client_author, category, 1)

    add_response = await client_admin.put(
        f"/v1/posts/{post['uuid']}/homepage-trending",
        params={"trending": "true"},
    )
    assert add_response.status_code == 200, add_response.text

    unpublish_response = await client_admin.put(f"/v1/posts/{post['uuid']}/unpublish")
    assert unpublish_response.status_code == 200, unpublish_response.text
    body = unpublish_response.json()
    assert body["is_published"] is False
    assert body["is_homepage_trending"] is False
    assert body["homepage_trending_order"] is None

    listing = await client_public.get("/v1/posts/homepage-trending")
    assert listing.status_code == 200, listing.text
    assert listing.json()["posts"] == []
