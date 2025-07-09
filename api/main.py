"""
Main FastAPI application for CraftyXhub.
Implements SubPRD-FastAPIAppSetup.md specifications.
"""
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
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    setup_logging()
    await init_database()
    
    yield
    
    # Shutdown
    await close_database()


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application instance.
    
    Returns:
        FastAPI: Configured application instance
    """
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
    
    # Configure middleware
    configure_middleware(app, settings)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include routers
    include_routers(app, settings)
    
    return app


def configure_middleware(app: FastAPI, settings) -> None:
    """
    Configure application middleware.
    
    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    config = settings.config
    
    # Request logging middleware (should be first)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Session middleware for session management
    app.add_middleware(
        SessionMiddleware,
        secret_key="dev-secret-key-change-in-production",  # TODO: Get from config
        max_age=86400,  # 24 hours
        same_site="lax",
        https_only=config.environment_name == "production"
    )
    
    # CORS middleware
    cors_config = config.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get("allow_origins", ["http://localhost:3000"]),
        allow_credentials=cors_config.get("allow_credentials", True),
        allow_methods=cors_config.get("allow_methods", ["*"]),
        allow_headers=cors_config.get("allow_headers", ["*"]),
        expose_headers=["X-Request-ID"],
    )
    
    # Trusted host middleware for production
    if config.environment_name == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["craftyhub.com", "*.craftyhub.com"]
        )


def include_routers(app: FastAPI, settings) -> None:
    """
    Include API routers with the application.
    
    Args:
        app: FastAPI application instance
        settings: Application settings
    """
    config = settings.config
    
    # Import authentication routers
    from routers.v1 import router as v1_router
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring."""
        from database.connection import check_database_health
        
        db_healthy = await check_database_health()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": config.environment_name,
            "database": "connected" if db_healthy else "disconnected",
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to CraftyXhub API",
            "version": "1.0.0",
            "docs_url": "/docs" if config.debug_mode else None,
            "environment": config.environment_name,
        }
    
    # API version info
    @app.get("/api", tags=["API Info"])
    async def api_info():
        """API version and information endpoint."""
        return {
            "name": "CraftyXhub API",
            "version": "1.0.0",
            "api_version": "v1",
            "description": "CraftyXhub Content Management API",
            "environment": config.environment_name,
        }
    
    # Include v1 API routers (includes all implemented endpoints)
    app.include_router(v1_router)


# Create application instance
app = create_application()


if __name__ == "__main__":
    """
    Run the application using uvicorn for development.
    In production, use a proper WSGI server like Gunicorn with uvicorn workers.
    """
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