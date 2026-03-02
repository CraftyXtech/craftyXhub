from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from core.settings import get_settings
from fastapi.responses import RedirectResponse
from routers.v1 import router as v1_router
from database.connection import db_health_check, get_db_session
from fastapi.responses import FileResponse
from sqlalchemy import select, or_
from models import Post, User, Category
from pathlib import Path
import logging

# Initialize cached settings
settings = get_settings()
logger = logging.getLogger(__name__)


def include_routers(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")

    @app.get("/health", tags=["Health"])
    async def health_check():
        db_healthy = await db_health_check()

        return {
            "status": "Healthy" if db_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": "development",
            "database": "connected" if db_healthy else "disconnected",
        }

    @app.get("/search", tags=["Global Search"], summary="Global Search")
    async def global_search(
        q: str = Query(..., min_length=1),
        db=Depends(get_db_session),
    ):
        query = f"%{q}%"

        posts_stmt = select(Post).filter(
            or_(
                Post.title.ilike(query),
                Post.content.ilike(query),
                Post.excerpt.ilike(query)
            )
        )
        users_stmt = select(User).filter(
            or_(
                User.username.ilike(query),
                User.full_name.ilike(query)
            )
        )
        categories_stmt = select(Category).filter(
            or_(
                Category.name.ilike(query),
                Category.description.ilike(query)
            )
        )

        posts_result = await db.execute(posts_stmt)
        users_result = await db.execute(users_stmt)
        categories_result = await db.execute(categories_stmt)

        return {
            "posts": posts_result.scalars().all(),
            "users": users_result.scalars().all(),
            "categories": categories_result.scalars().all(),
        }

    @app.get(
        "/v1/uploads/images/{filename}",
        tags=["Get Images"],
        summary="Get Image",
    )
    async def get_image(
        filename: str,
        folder: str = Query(
            ..., description="Folder category (e.g., 'posts', 'avatars')"
        ),
    ):
        if folder not in ["posts", "avatars", "media", "images"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder category"
            )
        
        # Backward compat: old DB records store "uploads/images/" but files
        # physically live in "uploads/posts/"
        folder_aliases = {"images": "posts"}
        actual_folder = folder_aliases.get(folder, folder)
        
        directory = Path(f"uploads/{actual_folder}")
        file_path = directory / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        return FileResponse(file_path)

    app.include_router(v1_router)


def create_application() -> FastAPI:
    app = FastAPI(
        title="CraftyXhub API",
        description="CraftyXhub Content Management API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={
            "name": "CraftyXhub Support",
            "email": "support@craftyhub.com",
        }
    )
    allow_origins = settings.ALLOWED_ORIGINS

    if settings.ALLOW_CREDENTIALS and (
        allow_origins == ["*"] or "*" in allow_origins
    ):
        # Fallback to explicit origins (e.g., FRONTEND_URL)
        # to avoid wildcard with credentials
        allow_origins = list(
            {settings.FRONTEND_URL, *[o for o in allow_origins if o != "*"]}
        )

    # Prepare CORS middleware kwargs
    cors_kwargs = {
        "allow_origins": allow_origins,
        "allow_credentials": settings.ALLOW_CREDENTIALS,
        "allow_methods": settings.ALLOW_METHODS,
        "allow_headers": settings.ALLOW_HEADERS,
        "expose_headers": settings.EXPOSE_HEADERS,
        "max_age": settings.CORS_MAX_AGE,
    }
    # Only add regex if it's provided and not None
    if settings.ALLOW_ORIGIN_REGEX:
        cors_kwargs["allow_origin_regex"] = settings.ALLOW_ORIGIN_REGEX
    
    app.add_middleware(
        CORSMiddleware,
        **cors_kwargs
    )

    # Optional AI observability setup and runtime capability checks.
    try:
        from services.ai.observability import configure_observability
        from services.ai.pydantic_compat import get_pydantic_ai_capabilities

        configure_observability()
        caps = get_pydantic_ai_capabilities()
        if settings.BLOG_AGENT_V2_REQUIRE_NATIVE:
            missing: list[str] = []
            if not caps.get("output_api", False):
                missing.append("output_type/output_retries")
            if not caps.get("fallback_model", False):
                missing.append("FallbackModel")
            if missing:
                raise RuntimeError(
                    "BLOG_AGENT_V2_REQUIRE_NATIVE=true but missing pydantic-ai features: "
                    + ", ".join(missing)
                )
    except Exception as exc:
        logger.warning("AI startup checks: %s", exc)

    include_routers(app)
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
