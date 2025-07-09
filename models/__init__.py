"""Proxy package to allow `import models.*` while real implementation is in `api.models`."""
import importlib, sys
_internal = importlib.import_module("api.models")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("user", "post", "category", "tag", "comment", "interactions", "audit"):
    try:
        sys.modules[f"models.{_sub}"] = importlib.import_module(f"api.models.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.models"] 