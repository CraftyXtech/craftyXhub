# routes/post.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from services.post.post_service import PostService
from services.user.auth import get_current_active_user
from database.connection import get_db_session
from schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    CategoryCreate,
    CategoryResponse,
    TagCreate,
    TagResponse,
    PostStatsResponse
)
from models import User, Post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=PostListResponse)
async def get_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        published_only: bool = Query(True),
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_posts(
        session,
        skip=skip,
        limit=limit,
        published_only=published_only,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id
    )
    total = await PostService.get_posts_count(
        session,
        published_only=published_only,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id
    )
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
        post_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    post = await PostService.get_post_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    await PostService.increment_view_count(session, post_id)
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        post_data: PostCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.create_post(session, post_data, current_user.id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.update_post(session, post_id, post_data, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    await PostService.delete_post(session, post_id, current_user.id)
    return None


@router.post("/{post_id}/like", response_model=bool)
async def toggle_post_like(
        post_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.toggle_post_like(session, post_id, current_user.id)


# Categories endpoints
@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(
        session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(Category))
    return result.scalars().all()


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: CategoryCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.create_category(session, category_data)


# Tags endpoints
@router.get("/tags/", response_model=List[TagResponse])
async def get_tags(
        session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(Tag))
    return result.scalars().all()


@router.post("/tags/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
        tag_data: TagCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.create_tag(session, tag_data)


@router.get("/stats/", response_model=PostStatsResponse)
async def get_post_stats(
        session: AsyncSession = Depends(get_db_session)
):
    stats = await PostService.get_post_stats(session)
    return stats