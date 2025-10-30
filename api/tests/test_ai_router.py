import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from routers.v1.ai import router as ai_router
from services.ai.generator import AIGeneratorService
from services.user.auth import get_current_active_user
from database.connection import get_db_session


class DummyUser:
    def __init__(self, user_id: int = 1):
        self.id = user_id


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(ai_router, prefix="/v1")

    # Dependency overrides
    async def _fake_user():
        return DummyUser(1)

    async def _fake_db():
        yield None

    app.dependency_overrides[get_current_active_user] = _fake_user
    app.dependency_overrides[get_db_session] = _fake_db
    return app


@pytest.mark.asyncio
async def test_generate_ok(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        return {
            "variants": [
                {"content": "<p>ok</p>", "metadata": {"words": 1, "model": "openai"}}
            ],
            "template_id": kwargs.get("template_id"),
            "model_used": kwargs.get("model"),
            "generation_time": 0.01,
        }

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "template_id": "blog-ideas",
            "model": "openai",
            "params": {"category": "Tech", "keywords": "ai"},
            "tone": "professional",
            "length": "short",
            "language": "en-US",
            "creativity": 0.3,
            "variant_count": 1,
        }
        resp = await ac.post("/v1/ai/generate", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["model_used"] == "openai"
        assert data["template_id"] == "blog-ideas"
        assert len(data["variants"]) == 1


@pytest.mark.asyncio
async def test_generate_bad_request_from_service(app, monkeypatch):
    async def fake_generate(self, **kwargs):
        raise ValueError("bad input")

    monkeypatch.setattr(AIGeneratorService, "generate", fake_generate, raising=True)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "template_id": "blog-ideas",
            "model": "openai",
            "params": {},
        }
        resp = await ac.post("/v1/ai/generate", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
