"""Minimal runtime capability checks for pydantic-ai native features."""

from __future__ import annotations

import inspect
from pydantic_ai import Agent


_AGENT_INIT_PARAMS = set(inspect.signature(Agent.__init__).parameters.keys())


def agent_supports_output_api() -> bool:
    return "output_type" in _AGENT_INIT_PARAMS


def supports_native_fallback_model() -> bool:
    try:
        from pydantic_ai.models.fallback import FallbackModel  # noqa: F401

        return True
    except Exception:
        return False


def get_pydantic_ai_capabilities() -> dict[str, bool]:
    return {
        "output_api": agent_supports_output_api(),
        "fallback_model": supports_native_fallback_model(),
    }
