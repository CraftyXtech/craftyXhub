from functools import lru_cache

# Reuse the Settings definition from config.py
from .config import Settings


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.

    This ensures environment variables are read once and the Settings
    object is reused across the application lifetime.
    """
    return Settings()
