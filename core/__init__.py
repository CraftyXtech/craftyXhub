"""Proxy package to maintain compatibility with imports expecting `core.*` when the actual implementation resides in `api.core`.
This avoids the need to rewrite all existing import statements.
"""
import importlib, sys

# Import the real internal package
_internal = importlib.import_module("api.core")
# Expose its public attributes at this top-level namespace
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)

# Ensure submodules (core.config, core.logging, etc.) resolve correctly
for _sub_name in ("config", "logging", "security", "exceptions"):
    full_internal = f"api.core.{_sub_name}"
    try:
        sys.modules[f"core.{_sub_name}"] = importlib.import_module(full_internal)
    except ModuleNotFoundError:
        # Some submodules might not exist yet; skip them gracefully
        pass

# Finally, register this proxy module itself
sys.modules[__name__] = sys.modules["api.core"] 