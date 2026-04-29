import pytest
from uuid import uuid4

from models import Category


STORY_FIXTURES = [
    {
        "title": "Markets Reprice AI Infrastructure Bets",
        "content": "<p>Investors are reassessing how capital will flow into AI infrastructure as cloud demand rises.</p>",
        "excerpt": "Markets are repricing AI infrastructure bets as cloud demand, energy costs, and chip roadmaps shift.",
    },
    {
        "title": "Crypto Firms Brace For Policy Jolt",
        "content": "<p>Crypto operators are preparing for the next round of policy shifts across licensing and market structure.</p>",
        "excerpt": "Crypto firms are bracing for policy jolts that could affect liquidity, licensing, and cross-border growth.",
    },
    {
        "title": "Geotech Risk Hits Global Supply Chains",
        "content": "<p>Supply-chain planners are watching how regional conflict affects chips, shipping routes, and cloud resilience.</p>",
        "excerpt": "Geotech risk is hitting global supply chains through chips, shipping routes, and infrastructure exposure.",
    },
]


async def create_category(test_session):
    suffix = uuid4().hex[:8]
    category = Category(name=f"Breaking {suffix}", slug=f"breaking-{suffix}")
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
async def test_admin_can_order_breaking_posts(client_author, client_admin, client_public, test_session):
    category = await create_category(test_session)
    posts = [
        await create_published_post(client_author, category, index)
        for index in range(1, 4)
    ]

    response_one = await client_admin.put(
        f"/v1/posts/{posts[0]['uuid']}/breaking",
        params={"breaking": "true", "order": 2},
    )
    assert response_one.status_code == 200, response_one.text

    response_two = await client_admin.put(
        f"/v1/posts/{posts[1]['uuid']}/breaking",
        params={"breaking": "true", "order": 1},
    )
    assert response_two.status_code == 200, response_two.text

    response_three = await client_admin.put(
        f"/v1/posts/{posts[2]['uuid']}/breaking",
        params={"breaking": "true"},
    )
    assert response_three.status_code == 200, response_three.text

    listing = await client_public.get("/v1/posts/breaking")
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert [post["uuid"] for post in body["posts"]] == [
        posts[1]["uuid"],
        posts[0]["uuid"],
        posts[2]["uuid"],
    ]
    assert [post["breaking_news_order"] for post in body["posts"]] == [1, 2, 3]


@pytest.mark.asyncio
async def test_unpublish_clears_breaking_news_slot(client_author, client_admin, client_public, test_session):
    category = await create_category(test_session)
    first_post = await create_published_post(client_author, category, 1)
    second_post = await create_published_post(client_author, category, 2)

    for post in (first_post, second_post):
        response = await client_admin.put(
            f"/v1/posts/{post['uuid']}/breaking",
            params={"breaking": "true"},
        )
        assert response.status_code == 200, response.text

    unpublish_response = await client_admin.put(f"/v1/posts/{first_post['uuid']}/unpublish")
    assert unpublish_response.status_code == 200, unpublish_response.text
    body = unpublish_response.json()
    assert body["is_published"] is False
    assert body["is_breaking_news"] is False
    assert body["breaking_news_order"] is None

    listing = await client_public.get("/v1/posts/breaking")
    assert listing.status_code == 200, listing.text
    listing_body = listing.json()
    assert len(listing_body["posts"]) == 1
    assert listing_body["posts"][0]["uuid"] == second_post["uuid"]
    assert listing_body["posts"][0]["breaking_news_order"] == 1
