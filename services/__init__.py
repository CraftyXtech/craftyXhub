"""Proxy package to allow `import services.*` while real implementation is in `api.services`."""
import importlib, sys
_internal = importlib.import_module("api.services")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("admin", "comments", "editor", "interactions", "posts", "web"):
    try:
        sys.modules[f"services.{_sub}"] = importlib.import_module(f"api.services.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.services"] 