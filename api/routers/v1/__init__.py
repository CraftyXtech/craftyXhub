
from fastapi import APIRouter

from .admin_users import router as admin_users_router
from .ai import router as ai_router
from .auth import router as auth_router
from .comment import router as comment_router
from .dashboard import router as dashboard_router
from .media import router as media_router
from .notification import router as notification_router
from .post import router as post_router
from .profile import router as profile_router
from .user import router as user_router


router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(user_router)
router.include_router(post_router)
router.include_router(comment_router)
router.include_router(media_router)
router.include_router(ai_router)
router.include_router(notification_router)
router.include_router(admin_users_router)
router.include_router(dashboard_router)
