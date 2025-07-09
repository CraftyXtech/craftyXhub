"""
API v1 Router Configuration

Includes all API routers for version 1 endpoints.
Organized by functional areas: authentication, editor modules, admin functions, and public web.
"""

from fastapi import APIRouter

# Authentication routers
from .auth import router as auth_router

# Editor module routers
from .editor_categories import router as editor_categories_router
from .editor_tags import router as editor_tags_router
from .editor_posts import router as editor_posts_router
from .editor_dashboard import router as editor_dashboard_router

# Public web routers
from .web_posts import router as web_posts_router
from .web_comments import router as web_comments_router, comment_router
from .web_interactions import router as web_interactions_router
from .web_profile import router as web_profile_router

# Admin routers (if they exist)
try:
    from .admin import router as admin_router
except ImportError:
    admin_router = None

try:
    from .public import router as public_router
except ImportError:
    public_router = None

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include authentication routes
router.include_router(auth_router)

# Include editor module routes (requires editor/admin permissions)
router.include_router(
    editor_categories_router,
    prefix="/editor",
    tags=["Editor - Categories"]
)
router.include_router(
    editor_tags_router,
    prefix="/editor",
    tags=["Editor - Tags"]
)
router.include_router(
    editor_posts_router,
    prefix="/editor",
    tags=["Editor - Posts"]
)
router.include_router(
    editor_dashboard_router,
    prefix="/editor",
    tags=["Editor - Dashboard"]
)

# Include public web routes (accessible to all users)
router.include_router(web_posts_router, tags=["Web - Posts"])
router.include_router(web_comments_router, tags=["Web - Comments"])
router.include_router(comment_router, tags=["Web - Comments"])  # Comment management without post_id
router.include_router(web_interactions_router, tags=["Web - Interactions"])
router.include_router(web_profile_router, tags=["Web - Profile"])

# Include admin routes if available
if admin_router:
    router.include_router(
        admin_router,
        prefix="/admin",
        tags=["Admin"]
    )

# Include public API routes if available
if public_router:
    router.include_router(public_router, tags=["Public API"])

# Available endpoints summary:
# Authentication:
#   - POST /v1/auth/login
#   - POST /v1/auth/refresh
#   - POST /v1/auth/logout
#   - GET  /v1/auth/me

# Editor Modules:
#   - /v1/editor/categories/* (Category management)
#   - /v1/editor/tags/* (Tag management)
#   - /v1/editor/posts/* (Post management)
#   - /v1/editor/dashboard/* (Dashboard analytics)

# Public Web:
#   - /v1/posts/* (Public post viewing)
#   - /v1/posts/{post_id}/comments/* (Comment threads)
#   - /v1/comments/* (Comment management)
#   - /v1/interactions/* (User interactions)
#   - /v1/profile/* (User profiles and preferences)

# Admin (if available):
#   - /v1/admin/* (Admin functions)

# Public API (if available):
#   - /v1/* (Public API endpoints) 