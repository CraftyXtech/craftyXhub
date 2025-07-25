from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, JSONResponse
from routers.v1 import router as v1_router
from database.connection import db_health_check, init_db, get_db_session
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from database.connection import get_db_session
from models import Post, User, Category



def include_routers(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        return RedirectResponse(url="/docs")

    @app.get("/health", tags=["Health"])
    async def health_check():
        db_healthy = await db_health_check()
        await  init_db()

        return {
            "status": "Healthy" if db_healthy else "unhealthy",
            "version": "1.0.0",
            "environment": "development",
            "database": "connected" if db_healthy else "disconnected",
        }


    @app.get("/search", tags=["Global Search"], summary="Global Search",)
    async def global_search(q: str = Query(..., min_length=1), db = Depends(get_db_session)):
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
            "categories": categories_result.scalars().all()
        }
            
    app.include_router(v1_router)

def create_application() -> FastAPI:
    app = FastAPI(
        title="CraftyXhub API",
        description="CraftyXhub Content Management API",
        version="1.0.0",
        docs_url="/docs" ,
        redoc_url="/redoc" ,
        openapi_url="/openapi.json",
        contact={
            "name": "CraftyXhub Support",
            "email": "support@craftyhub.com",
        }
    )
    # Enable CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

       
    include_routers(app)
    return app

app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    ) 