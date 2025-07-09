"""Proxy package to allow `import schemas.*` while real implementation is in `api.schemas`."""
import importlib, sys
_internal = importlib.import_module("api.schemas")
for attr in dir(_internal):
    if not attr.startswith("__"):
        globals()[attr] = getattr(_internal, attr)
# register submodules
for _sub in ("auth", "comment", "interaction", "password", "post", "registration", "user", "admin", "editor", "web"):
    try:
        sys.modules[f"schemas.{_sub}"] = importlib.import_module(f"api.schemas.{_sub}")
    except ModuleNotFoundError:
        pass
sys.modules[__name__] = sys.modules["api.schemas"] 