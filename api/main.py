import os
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

# Initialize cached settings
settings = get_settings()


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
        if folder not in ["posts", "avatars", "media"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder category"
            )
        
        directory = Path(f"uploads/{folder}")
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

    # Add localhost origins for development
    if os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "local"]:
        dev_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        allow_origins = list(set(allow_origins + dev_origins))

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
