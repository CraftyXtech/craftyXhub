#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, 'api')

# Set development environment
os.environ['ENVIRONMENT'] = 'development'

from core.settings import get_settings

# Clear cache and reload
import importlib
if 'core.settings' in sys.modules:
    importlib.reload(sys.modules['core.settings'])
if 'core.config' in sys.modules:
    importlib.reload(sys.modules['core.config'])

settings = get_settings()
print("Settings ALLOWED_ORIGINS:", settings.ALLOWED_ORIGINS)

# Test main.py CORS logic
allow_origins = settings.ALLOWED_ORIGINS

# Development convenience: Add localhost origins for development
dev_origins = []
if os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "local"]:
    dev_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server alternative
    ]
    # Only add dev origins that aren't already in the list
    allow_origins = list(set(allow_origins + dev_origins))

print("Final CORS origins:", allow_origins)
print("localhost:5173 allowed:", "http://localhost:5173" in allow_origins)
