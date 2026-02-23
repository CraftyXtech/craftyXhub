import importlib

import pytest
from fastapi import HTTPException

import core.config as config_module
from routers.v1 import auth as auth_router


def test_allowed_origins_blank_env_falls_back_to_defaults(monkeypatch):
    expected_origins = [
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "https://craftyxhub.com",
        "https://www.craftyxhub.com",
        "https://admin.craftyxhub.com",
    ]

    with monkeypatch.context() as patched:
        patched.setenv("ALLOWED_ORIGINS", "")
        reloaded = importlib.reload(config_module)
        assert reloaded.settings.ALLOWED_ORIGINS == expected_origins

    # Restore module-level settings after env patch is removed.
    importlib.reload(config_module)


@pytest.mark.asyncio
async def test_google_token_login_requires_configured_client_id(monkeypatch):
    monkeypatch.setattr(auth_router.settings, "GOOGLE_CLIENT_ID", None)
    request = auth_router.GoogleTokenRequest(credential="fake-token")

    with pytest.raises(HTTPException) as exc_info:
        await auth_router.google_token_login(request=request, db=None)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Google authentication is not configured"
