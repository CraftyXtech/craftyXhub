
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from core.config import get_settings
from core.exceptions import register_exception_handlers
from routers.v1 import router as v1_router
from database.connection import db_health_check

settings = get_settings()
config = settings.config


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
            "environment": config.environment_name,
            "database": "connected" if db_healthy else "disconnected",
        }
    app.include_router(v1_router)


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key="dev-secret-key-change-in-production",
        max_age=86400,  # 24 hours
        same_site="lax",
        https_only=config.environment_name == "production"
    )

    cors_config = config.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get("allow_origins", ["http://localhost:3000"]),
        allow_credentials=cors_config.get("allow_credentials", True),
        allow_methods=cors_config.get("allow_methods", ["*"]),
        allow_headers=cors_config.get("allow_headers", ["*"]),
        expose_headers=["X-Request-ID"],
    )

    if config.environment_name == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["craftyhub.com", "*.craftyhub.com"]
        )


def create_application() -> FastAPI:
    app = FastAPI(
        title="CraftyXhub API",
        description="CraftyXhub Content Management API",
        version="1.0.0",
        docs_url="/docs" if config.debug_mode else None,
        redoc_url="/redoc" if config.debug_mode else None,
        openapi_url="/openapi.json" if config.debug_mode else None,
        contact={
            "name": "CraftyXhub Support",
            "email": "support@craftyhub.com",
        }
    )
    
    
    configure_middleware(app)
    register_exception_handlers(app)
    include_routers(app)
    
    return app
app = create_application()


if __name__ == "__main__":
   
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=config.hot_reload and config.environment_name == "development",
        workers=config.worker_count if config.environment_name != "development" else 1,
        log_level=config.log_level.lower(),
        access_log=config.debug_mode,
    ) 