"""Proxy package to allow `import routers.*` while real implementation is in `api.routers`."""
import importlib, sys
_internal = importlib.import_module("api.routers")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("v1",):
    try:
        sys.modules[f"routers.{_sub}"] = importlib.import_module(f"api.routers.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.routers"] 