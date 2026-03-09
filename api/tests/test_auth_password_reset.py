from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import PasswordResetToken, User, UserRole
from services.user.auth import AuthService


@pytest.mark.asyncio
async def test_authenticated_password_change_invalidates_existing_reset_tokens(
    client_author,
    author_user: User,
    test_session: AsyncSession,
):
    author_user.password = AuthService.get_password_hash("currentpass123")
    reset_token = PasswordResetToken(
        user_id=author_user.id,
        token="legacy-token",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
        used=False,
    )
    test_session.add(reset_token)
    await test_session.commit()

    response = await client_author.put(
        "/v1/auth/reset-password",
        json={
            "current_password": "currentpass123",
            "new_password": "newpass123",
            "confirm_new_password": "newpass123",
        },
    )

    assert response.status_code == 200
    await test_session.refresh(author_user)
    await test_session.refresh(reset_token)
    assert AuthService.verify_password("newpass123", author_user.password)
    assert reset_token.used is True


@pytest.mark.asyncio
async def test_authenticated_password_change_rejects_short_password(
    client_author,
    author_user: User,
    test_session: AsyncSession,
):
    author_user.password = AuthService.get_password_hash("currentpass123")
    await test_session.commit()

    response = await client_author.put(
        "/v1/auth/reset-password",
        json={
            "current_password": "currentpass123",
            "new_password": "short",
            "confirm_new_password": "short",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_password_reset_request_stores_hashed_token_and_confirms_with_raw_token(
    client_public,
    test_session: AsyncSession,
    monkeypatch,
):
    user = User(
        email="forgot@example.com",
        username="forgotuser",
        full_name="Forgot User",
        password=AuthService.get_password_hash("oldpassword123"),
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    legacy_token = PasswordResetToken(
        user_id=user.id,
        token="legacy-plaintext-token",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
        used=False,
    )
    test_session.add(legacy_token)
    await test_session.commit()

    raw_token = "reset-token-123456"
    monkeypatch.setattr(
        AuthService,
        "generate_password_reset_token",
        staticmethod(lambda: raw_token),
    )

    request_response = await client_public.post(
        "/v1/auth/password-reset/request",
        json={"email": user.email},
    )

    assert request_response.status_code == 200
    assert request_response.json()["debug_reset_token"] is None

    stored_tokens = (
        await test_session.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .order_by(PasswordResetToken.id.asc())
        )
    ).scalars().all()
    assert len(stored_tokens) == 2
    assert stored_tokens[0].used is True
    assert stored_tokens[1].used is False
    assert stored_tokens[1].token == AuthService.hash_opaque_token(raw_token)
    assert stored_tokens[1].token != raw_token

    confirm_response = await client_public.post(
        "/v1/auth/password-reset/confirm",
        json={
            "token": raw_token,
            "new_password": "resetnew123",
            "confirm_password": "resetnew123",
        },
    )

    assert confirm_response.status_code == 200
    await test_session.refresh(user)
    assert AuthService.verify_password("resetnew123", user.password)

    stored_tokens = (
        await test_session.execute(
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user.id)
            .order_by(PasswordResetToken.id.asc())
        )
    ).scalars().all()
    assert all(token.used for token in stored_tokens)
