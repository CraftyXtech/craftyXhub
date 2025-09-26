#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, 'api')

# Set development environment
os.environ['ENVIRONMENT'] = 'development'

from core.config import Settings

settings = Settings()
print("ALLOWED_ORIGINS:", settings.ALLOWED_ORIGINS)
print("localhost:5173 allowed:", "http://localhost:5173" in settings.ALLOWED_ORIGINS)
