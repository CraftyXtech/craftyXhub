
from fastapi import APIRouter
from .auth import router as auth_router
from .profile import router as profile_router
from .post import router as post_router
from .user import router as user_router
from .comment import router as comment_router
from .media import router as media_router
from .ai import router as ai_router


router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(user_router)
router.include_router(post_router)
router.include_router(comment_router)
router.include_router(media_router)
router.include_router(ai_router)
