#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Clear any cached modules
import importlib
if 'core.config' in sys.modules:
    del sys.modules['core.config']
if 'core.settings' in sys.modules:
    del sys.modules['core.settings']

from core.config import Settings

settings = Settings()
print("ALLOWED_ORIGINS:", settings.ALLOWED_ORIGINS)
print("Found localhost:5173:", "http://localhost:5173" in settings.ALLOWED_ORIGINS)
