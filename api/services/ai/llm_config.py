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
    "gpt-5.2": {
        "id": "openai/gpt-5.2",
        "label": "GPT-5.2",
        "provider": "OpenAI",
        "supports_structured": True,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "deepseek-v3.2": {
        "id": "deepseek/deepseek-chat-v3-0324",
        "label": "DeepSeek V3.2",
        "provider": "DeepSeek",
        "supports_structured": True,
        "supports_compat_json": True,
        "blog_enabled": True,
    },
    "qwen3-235b": {
        "id": "qwen/qwen3-235b-a22b",
        "label": "Qwen3 235B",
        "provider": "Alibaba Cloud",
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
}

DEFAULT_MODEL = "claude-sonnet-4.6"
BLOG_FALLBACK_ORDER = [
    "claude-sonnet-4.6",
    "gpt-5.2",
    "deepseek-v3.2",
    "qwen3-235b",
    "kimi-k2.5",
]


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


def get_model_id(model_name: str, use_online: bool = False) -> str:
    entry = get_model_entry(model_name)
    model_id = entry["id"]
    return f"{model_id}:online" if use_online else model_id


def resolve_model_name_from_id(model_id: str) -> str | None:
    model_id = model_id[:-7] if model_id.endswith(":online") else model_id
    for key, entry in AVAILABLE_MODELS.items():
        if entry["id"] == model_id:
            return key
    return None


def get_blog_model_capabilities(model_name: str) -> dict[str, bool]:
    entry = get_model_entry(model_name)
    return {
        "supports_structured": bool(entry.get("supports_structured", False)),
        "supports_compat_json": bool(entry.get("supports_compat_json", False)),
        "blog_enabled": bool(entry.get("blog_enabled", False)),
    }


def build_blog_model_chain(
    selected_model: str,
    execution_mode: str = "strict",
    *,
    path: str = "structured",
    use_online: bool = False,
) -> list[str]:
    """
    Build deterministic model id chain for blog generation.

    path:
        - "structured": requires supports_structured
        - "compat_json": requires supports_compat_json
    """
    if execution_mode not in ("strict", "resilient"):
        raise ValueError("execution_mode must be one of: strict, resilient")
    if path not in ("structured", "compat_json"):
        raise ValueError("path must be one of: structured, compat_json")

    required_capability = (
        "supports_structured" if path == "structured" else "supports_compat_json"
    )

    selected_entry = get_model_entry(selected_model)
    if not selected_entry.get("blog_enabled", False):
        raise ValueError(f"Model '{selected_model}' is not enabled for blog generation")
    if not selected_entry.get(required_capability, False):
        return []

    selected_id = get_model_id(selected_model, use_online=use_online)
    if execution_mode == "strict":
        return [selected_id]

    ordered_model_names = [selected_model] + [
        name for name in BLOG_FALLBACK_ORDER if name != selected_model
    ]
    chain: list[str] = []
    seen: set[str] = set()

    for model_name in ordered_model_names:
        entry = AVAILABLE_MODELS.get(model_name)
        if not entry:
            continue
        if not entry.get("blog_enabled", False):
            continue
        if not entry.get(required_capability, False):
            continue
        model_id = get_model_id(model_name, use_online=use_online)
        if model_id in seen:
            continue
        seen.add(model_id)
        chain.append(model_id)

    return chain


def get_model(model_name: str) -> OpenAIModel:
    """
    Return a PydanticAI-compatible model instance for the given name.
    All models go through OpenRouter's OpenAI-compatible API.
    """
    return OpenAIModel(
        get_model_id(model_name),
        provider=_get_openrouter_provider(),
    )


def get_model_with_online(model_name: str) -> OpenAIModel:
    """
    Return a model instance with OpenRouter's :online suffix for native
    web search grounding. The model will browse the web during generation.
    """
    return OpenAIModel(
        get_model_id(model_name, use_online=True),
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
        return [
            {
                "value": DEFAULT_MODEL,
                "label": f"{AVAILABLE_MODELS[DEFAULT_MODEL]['label']} (needs API key)",
                "supports_structured": True,
                "supports_compat_json": True,
                "blog_enabled": True,
                "default_path": "structured",
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
