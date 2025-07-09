"""Proxy package to allow `import dependencies.*` while real implementation is in `api.dependencies`."""
import importlib, sys
_internal = importlib.import_module("api.dependencies")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("auth", "database", "editor_permissions", "pagination", "web_auth"):
    try:
        sys.modules[f"dependencies.{_sub}"] = importlib.import_module(f"api.dependencies.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.dependencies"] 