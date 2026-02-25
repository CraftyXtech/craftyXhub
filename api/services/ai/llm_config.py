"""
Central LLM configuration — single source of truth for all AI models.

All models are routed through OpenRouter. Add new models here and they
become available everywhere: blog agent, content generator, test endpoints,
and the frontend options dropdown.
"""

from pydantic_ai.models.openai import OpenAIModel
from core.config import settings


# ── Model registry ──────────────────────────────────────────────────
# Key   = value used in API requests and stored in DB
# label = human-readable name shown in the frontend dropdown
# id    = OpenRouter model identifier
AVAILABLE_MODELS = {
    "kimi-k2.5": {
        "id": "moonshotai/kimi-k2.5",
        "label": "Kimi K2.5 (Moonshot AI)",
        "provider": "Moonshot AI",
    },
    "grok-4.1-fast": {
        "id": "x-ai/grok-4.1-fast",
        "label": "Grok 4.1 Fast (xAI)",
        "provider": "xAI",
    },
    "gemini-3-flash": {
        "id": "google/gemini-3-flash-preview",
        "label": "Gemini 3 Flash Preview (Google)",
        "provider": "Google",
    },
}

DEFAULT_MODEL = "kimi-k2.5"


def get_model(model_name: str) -> OpenAIModel:
    """
    Return a PydanticAI-compatible model instance for the given name.
    All models go through OpenRouter's OpenAI-compatible API.
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError(
            "OpenRouter API key not configured. Add OPENROUTER_API_KEY to .env"
        )

    entry = AVAILABLE_MODELS.get(model_name)
    if not entry:
        supported = ", ".join(AVAILABLE_MODELS.keys())
        raise ValueError(
            f"Unsupported model: {model_name}. Supported: {supported}"
        )

    return OpenAIModel(
        entry["id"],
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )


def get_models_for_frontend() -> list[dict]:
    """Return the model list formatted for frontend dropdowns."""
    if not settings.OPENROUTER_API_KEY:
        return [{"value": DEFAULT_MODEL, "label": f"{AVAILABLE_MODELS[DEFAULT_MODEL]['label']} (needs API key)"}]

    return [
        {"value": key, "label": entry["label"]}
        for key, entry in AVAILABLE_MODELS.items()
    ]


def get_models_for_test() -> list[dict]:
    """Return detailed model info for the /ai/test endpoint."""
    if not settings.OPENROUTER_API_KEY:
        return []

    return [
        {
            "model": key,
            "provider": f"{entry['provider']} (via OpenRouter)",
            "openrouter_id": entry["id"],
            "status": "configured",
        }
        for key, entry in AVAILABLE_MODELS.items()
    ]
