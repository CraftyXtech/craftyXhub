import io

import pytest
from sqlalchemy import select

from models import Profile, User


@pytest.mark.asyncio
async def test_profile_update_saves_user_name_bio_and_avatar(client_author, test_session, author_user):
    files = {
        "avatar": ("avatar.png", io.BytesIO(b"fake image bytes"), "image/png"),
    }
    data = {
        "full_name": "Updated Author",
        "username": "updatedauthor",
        "bio": "This is my new profile bio.",
        "twitter_handle": "@updated",
    }

    response = await client_author.put(
        f"/v1/profiles/{author_user.uuid}",
        data=data,
        files=files,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["bio"] == "This is my new profile bio."
    assert body["twitter_handle"] == "@updated"
    assert body["avatar"].startswith("uploads/avatars/")

    user = (
        await test_session.execute(select(User).where(User.id == author_user.id))
    ).scalar_one()
    profile = (
        await test_session.execute(select(Profile).where(Profile.user_id == author_user.id))
    ).scalar_one()
    assert user.full_name == "Updated Author"
    assert user.username == "updatedauthor"
    assert profile.bio == "This is my new profile bio."
    assert profile.avatar == body["avatar"]


@pytest.mark.asyncio
async def test_profile_update_creates_missing_profile(client_author, test_session, author_user):
    existing = (
        await test_session.execute(select(Profile).where(Profile.user_id == author_user.id))
    ).scalar_one_or_none()
    if existing:
        await test_session.delete(existing)
        await test_session.commit()

    response = await client_author.put(
        f"/v1/profiles/{author_user.uuid}",
        data={"bio": "Created during update."},
    )

    assert response.status_code == 200, response.text
    assert response.json()["bio"] == "Created during update."

    profile = (
        await test_session.execute(select(Profile).where(Profile.user_id == author_user.id))
    ).scalar_one()
    assert profile.bio == "Created during update."


@pytest.mark.asyncio
async def test_profile_update_rejects_duplicate_username(
    client_author,
    test_session,
    author_user,
):
    other = User(
        email="other-profile@example.com",
        username="takenname",
        full_name="Other User",
        password="hashed",
        is_active=True,
    )
    test_session.add(other)
    await test_session.commit()

    response = await client_author.put(
        f"/v1/profiles/{author_user.uuid}",
        data={"username": "takenname"},
    )

    assert response.status_code == 400
    assert "Username may already be taken" in response.json()["detail"]
