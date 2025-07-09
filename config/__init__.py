"""Proxy package to allow `import config.*` while real implementation is in `api.config`."""
import importlib, sys
_internal = importlib.import_module("api.config")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in (
    "loader",
    "secret_manager",
    "settings",
    "services",
    "validator",
    "cache",
    "database",
    "email",
    "environments",
):
    try:
        sys.modules[f"config.{_sub}"] = importlib.import_module(f"api.config.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.config"] 