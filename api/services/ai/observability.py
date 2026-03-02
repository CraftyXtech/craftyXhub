"""
Optional observability hooks for AI workflows.

Uses Logfire when available and enabled, with safe no-op fallbacks.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from core.config import settings

logger = logging.getLogger(__name__)

_configured = False
_logfire_mod: Any | None = None


def configure_observability() -> dict[str, Any]:
    """
    Configure optional Logfire instrumentation.
    Safe to call multiple times.
    """
    global _configured, _logfire_mod

    if _configured:
        return {
            "configured": True,
            "provider": "logfire" if _logfire_mod else "none",
        }

    _configured = True

    if not settings.LOGFIRE_ENABLED:
        logger.info("AI observability: disabled (LOGFIRE_ENABLED=false)")
        return {"configured": True, "provider": "none"}

    try:
        import logfire

        # Support explicit token configuration where available.
        if settings.LOGFIRE_TOKEN:
            try:
                logfire.configure(token=settings.LOGFIRE_TOKEN)
            except TypeError:
                # Older/newer logfire may not accept token kwarg.
                logfire.configure()
        else:
            logfire.configure()

        try:
            logfire.instrument_pydantic_ai()
        except Exception as exc:
            logger.warning("AI observability: failed to instrument pydantic-ai: %s", exc)

        _logfire_mod = logfire
        logger.info("AI observability: Logfire enabled")
        return {"configured": True, "provider": "logfire"}
    except Exception as exc:
        logger.warning("AI observability: Logfire unavailable, continuing without it: %s", exc)
        _logfire_mod = None
        return {"configured": True, "provider": "none", "error": str(exc)}


@contextmanager
def ai_span(name: str, **attrs: Any) -> Iterator[None]:
    """
    Start an observability span when supported; otherwise no-op.
    """
    if _logfire_mod is None:
        yield
        return

    try:
        with _logfire_mod.span(name, **attrs):
            yield
    except Exception:
        # Never fail generation due to telemetry.
        yield


def ai_event(message: str, **attrs: Any) -> None:
    """
    Emit an event into the active observability backend when supported.
    """
    if _logfire_mod is None:
        return

    try:
        _logfire_mod.info(message, **attrs)
    except Exception:
        return
