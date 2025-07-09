"""Proxy package to allow `import database.*` while real implementation is in `api.database`."""
import importlib, sys
_internal = importlib.import_module("api.database")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("connection",):
    try:
        sys.modules[f"database.{_sub}"] = importlib.import_module(f"api.database.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.database"] 