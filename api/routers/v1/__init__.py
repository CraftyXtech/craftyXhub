
from fastapi import APIRouter

# Authentication routers
from .auth import router as auth_router
from .registration import router as registration_router
from .password import router as password_router

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

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include authentication routes - let routers use their own tags
router.include_router(auth_router)
router.include_router(registration_router)
router.include_router(password_router)

# Include editor module routes (requires editor/admin permissions)
router.include_router(editor_categories_router)
router.include_router(editor_tags_router)
router.include_router(editor_posts_router)
router.include_router(editor_dashboard_router)

# Include public web routes (accessible to all users)
router.include_router(web_posts_router)
router.include_router(web_comments_router)
router.include_router(comment_router)  # Has its own "Comment Management" tag
router.include_router(web_interactions_router)
router.include_router(web_profile_router)


if admin_router:
    router.include_router(admin_router, prefix="/admin")

