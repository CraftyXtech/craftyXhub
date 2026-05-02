"""Central LLM configuration loaded from the OpenRouter model config file."""

import json
import os
from pathlib import Path

from pydantic_ai.models import cached_async_http_client
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from core.config import settings


DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "openrouter_models.json"
)
MODEL_CONFIG_PATH = Path(os.getenv("OPENROUTER_MODELS_CONFIG", DEFAULT_CONFIG_PATH))


def _load_model_config() -> dict:
    try:
        with MODEL_CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except OSError as exc:
        raise RuntimeError(
            f"Unable to load OpenRouter model config: {MODEL_CONFIG_PATH}"
        ) from exc

    models = config.get("models")
    default_model = config.get("default_model")
    if not isinstance(models, dict) or not models:
        raise RuntimeError(
            "OpenRouter model config must define a non-empty models object"
        )
    if not default_model or default_model not in models:
        raise RuntimeError("OpenRouter model config default_model must exist in models")
    if not bool(models[default_model].get("blog_enabled", False)):
        raise RuntimeError("OpenRouter model config default_model must be blog_enabled")
    return config


_MODEL_CONFIG = _load_model_config()
AVAILABLE_MODELS = _MODEL_CONFIG["models"]
DEFAULT_MODEL = _MODEL_CONFIG["default_model"]
NVIDIA_PROVIDER_TYPE = "nvidia"
OPENROUTER_PROVIDER_TYPE = "openrouter"


def _ensure_api_key():
    if not settings.OPENROUTER_API_KEY:
        raise ValueError(
            "OpenRouter API key not configured. Add OPENROUTER_API_KEY to .env"
        )


def _ensure_nvidia_api_key():
    if not settings.NVIDIA_API_KEY:
        raise ValueError(
            "NVIDIA API key not configured. Add NVIDIA_API_KEY to .env"
        )


def _get_openrouter_provider() -> OpenRouterProvider:
    _ensure_api_key()
    request_timeout = settings.AI_MODEL_REQUEST_TIMEOUT_SECONDS
    http_client = cached_async_http_client(
        provider=f"openrouter-{request_timeout}",
        timeout=request_timeout,
        connect=5,
    )
    return OpenRouterProvider(
        api_key=settings.OPENROUTER_API_KEY,
        http_client=http_client,
    )


def _get_nvidia_provider() -> OpenAIProvider:
    _ensure_nvidia_api_key()
    request_timeout = settings.AI_MODEL_REQUEST_TIMEOUT_SECONDS
    http_client = cached_async_http_client(
        provider=f"nvidia-{request_timeout}",
        timeout=request_timeout,
        connect=5,
    )
    return OpenAIProvider(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=settings.NVIDIA_API_KEY,
        http_client=http_client,
    )


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


def get_blog_model_capabilities(model_name: str) -> dict:
    entry = get_model_entry(model_name)
    return {
        "provider_type": entry.get("provider_type", OPENROUTER_PROVIDER_TYPE),
        "supports_structured": bool(entry.get("supports_structured", False)),
        "supports_compat_json": bool(entry.get("supports_compat_json", False)),
        "blog_enabled": bool(entry.get("blog_enabled", False)),
        "output_mode": entry.get("output_mode", "prompted_json"),
        "reasoning": entry.get("reasoning"),
        "extra_body": entry.get("extra_body") or {},
        "send_temperature": bool(entry.get("send_temperature", True)),
        "json_object_fallback": bool(entry.get("json_object_fallback", True)),
        "max_tokens_by_word_count": entry.get("max_tokens_by_word_count") or {},
        "transient_retry_delay_seconds": entry.get("transient_retry_delay_seconds"),
        "openrouter_provider": entry.get("openrouter_provider") or {},
    }


def ensure_blog_model_enabled(model_name: str) -> str:
    entry = get_model_entry(model_name)
    if not bool(entry.get("blog_enabled", False)):
        visible = ", ".join(get_blog_model_keys())
        raise ValueError(
            f"Unsupported blog model: {model_name}. Supported blog models: {visible}"
        )
    return model_name


def get_blog_model_keys() -> list[str]:
    return [
        key
        for key, entry in AVAILABLE_MODELS.items()
        if bool(entry.get("blog_enabled", False))
    ]


def get_model(model_name: str):
    """
    Return a PydanticAI-compatible model instance for the given configured name.
    """
    entry = get_model_entry(model_name)
    if entry.get("provider_type") == NVIDIA_PROVIDER_TYPE:
        return OpenAIModel(
            entry["id"],
            provider=_get_nvidia_provider(),
        )

    return OpenRouterModel(
        entry["id"],
        provider=_get_openrouter_provider(),
    )


def get_model_from_id(model_id: str):
    for entry in AVAILABLE_MODELS.values():
        if entry.get("id") == model_id:
            if entry.get("provider_type") == NVIDIA_PROVIDER_TYPE:
                return OpenAIModel(
                    model_id,
                    provider=_get_nvidia_provider(),
                )
            break

    return OpenRouterModel(
        model_id,
        provider=_get_openrouter_provider(),
    )


def get_models_for_frontend() -> list[dict]:
    """Return the model list formatted for frontend dropdowns."""
    if not settings.NVIDIA_API_KEY and not settings.OPENROUTER_API_KEY:
        default_entry = AVAILABLE_MODELS[DEFAULT_MODEL]
        return [
            {
                "value": DEFAULT_MODEL,
                "label": f"{default_entry['label']} (needs API key)",
                "supports_structured": bool(default_entry.get("supports_structured", False)),
                "supports_compat_json": bool(default_entry.get("supports_compat_json", False)),
                "blog_enabled": bool(default_entry.get("blog_enabled", False)),
                "default_path": default_entry.get("output_mode", "prompted_json"),
                "provider_type": default_entry.get("provider_type", OPENROUTER_PROVIDER_TYPE),
            }
        ]

    visible_model_keys = get_blog_model_keys()
    if DEFAULT_MODEL in visible_model_keys:
        visible_model_keys = [
            DEFAULT_MODEL,
            *[key for key in visible_model_keys if key != DEFAULT_MODEL],
        ]
    visible_models = [(key, AVAILABLE_MODELS[key]) for key in visible_model_keys]

    return [
        {
            "value": key,
            "label": entry["label"],
            "supports_structured": bool(entry.get("supports_structured", False)),
            "supports_compat_json": bool(entry.get("supports_compat_json", False)),
            "blog_enabled": bool(entry.get("blog_enabled", False)),
            "default_path": entry.get("output_mode", "prompted_json"),
            "provider_type": entry.get("provider_type", OPENROUTER_PROVIDER_TYPE),
        }
        for key, entry in visible_models
    ]


def get_models_for_test() -> list[dict]:
    """Return detailed model info for the /ai/test endpoint."""
    if not settings.NVIDIA_API_KEY and not settings.OPENROUTER_API_KEY:
        return []

    models: list[dict] = []
    for key, entry in AVAILABLE_MODELS.items():
        provider_type = entry.get("provider_type", OPENROUTER_PROVIDER_TYPE)
        configured = (
            bool(settings.NVIDIA_API_KEY)
            if provider_type == NVIDIA_PROVIDER_TYPE
            else bool(settings.OPENROUTER_API_KEY)
        )
        models.append(
            {
                "model": key,
                "provider": f"{entry['provider']} (via {provider_type})",
                "model_id": entry["id"],
                "openrouter_id": entry["id"],
                "status": "configured" if configured else "missing_api_key",
                "supports_structured": bool(entry.get("supports_structured", False)),
                "supports_compat_json": bool(entry.get("supports_compat_json", False)),
                "blog_enabled": bool(entry.get("blog_enabled", False)),
                "output_mode": entry.get("output_mode", "prompted_json"),
                "provider_type": provider_type,
                "reasoning": entry.get("reasoning"),
            }
        )
    return models
