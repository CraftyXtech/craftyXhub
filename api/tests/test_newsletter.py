import pytest
from sqlalchemy import select

from models.newsletter import NewsletterSubscriber


@pytest.mark.asyncio
async def test_public_newsletter_subscription_is_saved(client_public, test_session):
    response = await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "Reader@Example.com", "source": "homepage"},
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["subscriber"]["email"] == "reader@example.com"
    assert data["subscriber"]["source"] == "homepage"
    assert data["already_subscribed"] is False

    result = await test_session.execute(select(NewsletterSubscriber))
    subscriber = result.scalar_one()
    assert subscriber.email == "reader@example.com"


@pytest.mark.asyncio
async def test_duplicate_newsletter_subscription_is_idempotent(client_public, test_session):
    await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "reader@example.com", "source": "homepage"},
    )

    response = await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "READER@example.com", "source": "footer"},
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["already_subscribed"] is True
    assert data["subscriber"]["source"] == "footer"

    count = len((await test_session.execute(select(NewsletterSubscriber))).scalars().all())
    assert count == 1


@pytest.mark.asyncio
async def test_admin_dashboard_includes_newsletter_subscribers(
    client_public,
    client_admin,
):
    await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "first@example.com", "source": "homepage"},
    )
    await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "second@example.com", "source": "footer"},
    )

    response = await client_admin.get("/v1/dashboard/admin")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["newsletter_subscribers"] == 2
    assert [item["email"] for item in data["recent_subscribers"]] == [
        "second@example.com",
        "first@example.com",
    ]


@pytest.mark.asyncio
async def test_only_admins_can_list_newsletter_subscribers(client_public, client_author, client_admin):
    await client_public.post(
        "/v1/newsletter/subscribe",
        json={"email": "reader@example.com", "source": "homepage"},
    )

    denied = await client_author.get("/v1/newsletter/subscribers")
    assert denied.status_code == 403

    allowed = await client_admin.get("/v1/newsletter/subscribers")
    assert allowed.status_code == 200
    assert allowed.json()[0]["email"] == "reader@example.com"
