"""
Central LLM configuration — single source of truth for all AI models.

All models are routed through OpenRouter. Add new models here and they
become available everywhere: blog agent, content generator, test endpoints,
and the frontend options dropdown.
"""

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from core.config import settings


# ── Model registry ──────────────────────────────────────────────────
# Key   = value used in API requests and stored in DB
# label = human-readable name shown in the frontend dropdown
# id    = OpenRouter model identifier
AVAILABLE_MODELS = {
    "claude-sonnet-4.6": {
        "id": "anthropic/claude-sonnet-4.6",
        "label": "Sonnet 4.6",
        "provider": "Anthropic",
        "supports_structured": True,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "gpt-5.4": {
        "id": "openai/gpt-5.4",
        "label": "GPT-5.4",
        "provider": "OpenAI",
        "supports_structured": True,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "glm-5-turbo": {
        "id": "z-ai/glm-5-turbo",
        "label": "GLM 5 Turbo",
        "provider": "Z.AI",
        "supports_structured": False,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "kimi-k2.5": {
        "id": "moonshotai/kimi-k2.5",
        "label": "Kimi K2.5",
        "provider": "Moonshot AI",
        "supports_structured": True,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "qwen-3.6-plus": {
        "id": "qwen/qwen3.6-plus",
        "label": "Qwen 3.6 Plus",
        "provider": "Qwen",
        "supports_structured": False,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
}

DEFAULT_MODEL = "glm-5-turbo"


def _ensure_api_key():
    if not settings.OPENROUTER_API_KEY:
        raise ValueError(
            "OpenRouter API key not configured. Add OPENROUTER_API_KEY to .env"
        )


def _get_openrouter_provider() -> OpenRouterProvider:
    _ensure_api_key()
    return OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)


def get_model_entry(model_name: str) -> dict:
    entry = AVAILABLE_MODELS.get(model_name)
    if not entry:
        supported = ", ".join(AVAILABLE_MODELS.keys())
        raise ValueError(
            f"Unsupported model: {model_name}. Supported: {supported}"
        )
    return entry


def get_model_id(model_name: str) -> str:
    entry = get_model_entry(model_name)
    return entry["id"]


def get_blog_model_capabilities(model_name: str) -> dict[str, bool]:
    entry = get_model_entry(model_name)
    return {
        "supports_structured": bool(entry.get("supports_structured", False)),
        "supports_compat_json": bool(entry.get("supports_compat_json", False)),
        "blog_enabled": bool(entry.get("blog_enabled", False)),
    }


def get_model(model_name: str) -> OpenAIModel:
    """
    Return a PydanticAI-compatible model instance for the given name.
    All models go through OpenRouter's OpenAI-compatible API.
    """
    return OpenAIModel(
        get_model_id(model_name),
        provider=_get_openrouter_provider(),
    )


def get_model_from_id(model_id: str) -> OpenAIModel:
    return OpenAIModel(
        model_id,
        provider=_get_openrouter_provider(),
    )


def get_models_for_frontend() -> list[dict]:
    """Return the model list formatted for frontend dropdowns."""
    if not settings.OPENROUTER_API_KEY:
        default_entry = AVAILABLE_MODELS[DEFAULT_MODEL]
        return [
            {
                "value": DEFAULT_MODEL,
                "label": f"{default_entry['label']} (needs API key)",
                "supports_structured": bool(default_entry.get("supports_structured", False)),
                "supports_compat_json": bool(default_entry.get("supports_compat_json", False)),
                "blog_enabled": bool(default_entry.get("blog_enabled", False)),
                "default_path": (
                    "structured"
                    if default_entry.get("supports_structured", False)
                    else "compat_json"
                ),
            }
        ]

    return [
        {
            "value": key,
            "label": entry["label"],
            "supports_structured": bool(entry.get("supports_structured", False)),
            "supports_compat_json": bool(entry.get("supports_compat_json", False)),
            "blog_enabled": bool(entry.get("blog_enabled", False)),
            "default_path": (
                "structured"
                if entry.get("supports_structured", False)
                else "compat_json"
            ),
        }
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
            "supports_structured": bool(entry.get("supports_structured", False)),
            "supports_compat_json": bool(entry.get("supports_compat_json", False)),
            "blog_enabled": bool(entry.get("blog_enabled", False)),
        }
        for key, entry in AVAILABLE_MODELS.items()
    ]
