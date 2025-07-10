
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.config import get_settings
from core.logging import setup_logging, RequestLoggingMiddleware
from core.exceptions import register_exception_handlers
from database.connection import init_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
   
    setup_logging()
    await init_database()
    
    yield
    
    # Shutdown
    await close_database()


def create_application() -> FastAPI:
  
    settings = get_settings()
    config = settings.config
    
    # Create FastAPI application with metadata
    app = FastAPI(
        title="CraftyXhub API",
        description="CraftyXhub Content Management API",
        version="1.0.0",
        docs_url="/docs" if config.debug_mode else None,
        redoc_url="/redoc" if config.debug_mode else None,
        openapi_url="/openapi.json" if config.debug_mode else None,
        lifespan=lifespan,
        # Additional metadata for OpenAPI documentation
        contact={
            "name": "CraftyXhub Support",
            "email": "support@craftyhub.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        terms_of_service="https://craftyhub.com/terms",
    )
    
    
    configure_middleware(app, settings)
    
    register_exception_handlers(app)
       
    include_routers(app, settings)
    
    return app


def configure_middleware(app: FastAPI, settings) -> None:
   
    config = settings.config
    
   
   
   
    app.add_middleware(
        SessionMiddleware,
        secret_key="dev-secret-key-change-in-production",  # TODO: Get from config
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


def include_routers(app: FastAPI, settings) -> None:
   
    config = settings.config
    
   
    from routers.v1 import router as v1_router
    
   
    @app.get("/health", tags=["Health"])
    async def health_check():
       
        from database.connection import check_database_health
        
        db_healthy = await check_database_health()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": config.environment_name,
            "database": "connected" if db_healthy else "disconnected",
        }
    
   
    @app.get("/", tags=["Root"])
    async def root():
       
        return {
            "message": "Welcome to CraftyXhub API",
            "version": "1.0.0",
            "docs_url": "/docs" if config.debug_mode else None,
            "environment": config.environment_name,
        }
    
   
    @app.get("/api", tags=["API Info"])
    async def api_info():
       
        return {
            "name": "CraftyXhub API",
            "version": "1.0.0",
            "api_version": "v1",
            "description": "CraftyXhub Backend Blog API",
            "environment": config.environment_name,
        }
    
   
    app.include_router(v1_router)



app = create_application()


if __name__ == "__main__":
   
    import uvicorn
    
    settings = get_settings()
    config = settings.config
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=config.hot_reload and config.environment_name == "development",
        workers=config.worker_count if config.environment_name != "development" else 1,
        log_level=config.log_level.lower(),
        access_log=config.debug_mode,
    ) 