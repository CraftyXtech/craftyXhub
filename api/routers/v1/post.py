import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from sqlmodel import select
from typing import Optional, List
from pydantic import ValidationError

from services.post.post import PostService, UPLOAD_DIR
from services.user.auth import get_current_active_user
from database.connection import get_db_session
from schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryCreateResponse,
    CategoryResponse,
    CategoryListResponse,
    TagCreate,
    TagResponse,
    TagListResponse,
    PostStatsResponse,
    ReportCreate,
    ReportResponse
)
from models import User, Category, Tag, Post
from fastapi import Form, File, UploadFile
from models.base import post_bookmarks

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/trending/", response_model=PostListResponse)
async def get_trending_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_trending_posts(session, skip=skip, limit=limit)
    total = await PostService.get_posts_count(session, published_only=True)
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/featured", response_model=PostListResponse)
async def get_featured_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_featured_posts(session, skip=skip, limit=limit)
    total = await PostService.get_posts_count(session, published_only=True, is_featured=True)
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/recent", response_model=PostListResponse)
async def get_recent_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_recent_posts(session, skip=skip, limit=limit)
    total = await PostService.get_posts_count(session, published_only=True)
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/popular", response_model=PostListResponse)
async def get_popular_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_popular_posts(session, skip=skip, limit=limit)
    total = await PostService.get_posts_count(session, published_only=True)
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/{post_uuid}/related", response_model=PostListResponse)
async def get_related_posts(
        post_uuid: str,
        limit: int = Query(5, ge=1, le=10),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_related_posts(session, post_uuid, limit=limit)
    return {
        "posts": posts,
        "total": len(posts),
        "page": 1,
        "size": limit
    }


@router.get("/drafts", response_model=PostListResponse)
async def get_draft_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_draft_posts(session, current_user.id, skip=skip, limit=limit)
    total = await PostService.get_posts_count(session, published_only=False, author_id=current_user.id)
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(get_db_session)
):
    reports = await PostService.get_reports(session, skip=skip, limit=limit)
    return reports


@router.get("/", response_model=PostListResponse)
async def get_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        published: bool = Query(True),
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_posts(
        session,
        skip=skip,
        limit=limit,
        published_only=published,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id
    )
    total = await PostService.get_posts_count(
        session,
        published_only=published,
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


@router.get("/{post_uuid}", response_model=PostResponse)
async def get_post(
        post_uuid: str,
        session: AsyncSession = Depends(get_db_session)
):
    post = await PostService.get_post_by_uuid(session, post_uuid)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    await PostService.increment_view_count(session, post_uuid)
    return await PostService.get_post_with_relationships(session, post.id)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        title: str = Form(...),
        slug: Optional[str] = Form(None),
        content: str = Form(...),
        content_blocks: Optional[str] = Form(None),
        excerpt: Optional[str] = Form(None),
        meta_title: Optional[str] = Form(None),
        meta_description: Optional[str] = Form(None),
        category_id: Optional[int] = Form(None),
        tag_ids: Optional[str] = Form(None),
        reading_time: Optional[int] = Form(None),
        is_published: Optional[bool] = Form(False),
        featured_image: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    featured_image_path = None
    if featured_image and featured_image.filename:
        featured_image_path = await PostService.save_uploaded_file(featured_image, UPLOAD_DIR)

    parsed_tag_ids = []
    if tag_ids:
        try:
            parsed_tag_ids = [int(tag_id.strip()) for tag_id in tag_ids.split(",") if tag_id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Must be comma-separated integers."
            )

    if not slug:
        generated_slug = await PostService.generate_unique_slug(session, title, Post)
    else:
        generated_slug = slug.strip()

    # Parse content_blocks JSON if provided
    parsed_blocks = None
    if content_blocks:
        try:
            parsed_blocks = json.loads(content_blocks)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content_blocks format. Must be valid JSON."
            )

    # Validate input via schema; return 422 on validation errors instead of 500
    try:
        post_data = PostCreate(
            title=title,
            slug=generated_slug,
            content=content,
            content_blocks=parsed_blocks,
            excerpt=excerpt,
            meta_title=meta_title,
            meta_description=meta_description,
            category_id=category_id,
            tag_ids=parsed_tag_ids,
            reading_time=reading_time,
            featured_image=featured_image_path,
            is_published=is_published or False
        )
    except ValidationError as e:
        if featured_image_path and os.path.exists(featured_image_path):
            os.remove(featured_image_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "errors": [
                    {
                        "field": ".".join(str(loc) for loc in error["loc"]),
                        "message": error["msg"],
                        "type": error["type"]
                    }
                    for error in e.errors()
                ]
            }
        )

    try:
        post = await PostService.create_post(session, post_data, current_user.id)
        return post
    except Exception as e:
        if featured_image_path and os.path.exists(featured_image_path):
            os.remove(featured_image_path)
        raise e


@router.put("/{post_uuid}", response_model=PostResponse)
async def update_post(
        post_uuid: str,
        title: Optional[str] = Form(None),
        slug: Optional[str] = Form(None),
        content: Optional[str] = Form(None),
        content_blocks: Optional[str] = Form(None),
        excerpt: Optional[str] = Form(None),
        meta_title: Optional[str] = Form(None),
        meta_description: Optional[str] = Form(None),
        category_id: Optional[int] = Form(None),
        tag_ids: Optional[str] = Form(None),
        reading_time: Optional[int] = Form(None),
        is_published: Optional[bool] = Form(None),
        featured_image: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    existing_post = await PostService.get_post_by_uuid(session, post_uuid)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    old_image_path = existing_post.featured_image

    if featured_image and featured_image.filename:
        featured_image_path = await PostService.save_uploaded_file(featured_image, UPLOAD_DIR)
    else:
        featured_image_path = existing_post.featured_image

    parsed_tag_ids = None
    if tag_ids:
        try:
            parsed_tag_ids = [int(tag_id.strip()) for tag_id in tag_ids.split(",") if tag_id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Must be comma-separated integers."
            )

    # Parse content_blocks JSON if provided
    parsed_blocks = None
    if content_blocks is not None:
        if content_blocks == "":
            parsed_blocks = None
        else:
            try:
                parsed_blocks = json.loads(content_blocks)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid content_blocks format. Must be valid JSON."
                )

    form_data = {
        'title': title,
        'slug': slug,
        'content': content,
        'content_blocks': parsed_blocks,
        'excerpt': excerpt,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'category_id': category_id,
        'tag_ids': parsed_tag_ids,
        'reading_time': reading_time,
        'is_published': is_published,
    }

    if featured_image and featured_image.filename:
        form_data['featured_image'] = featured_image_path

    update_data = {k: v for k, v in form_data.items() if v is not None}

    try:
        post_data = PostUpdate(**update_data)
    except ValidationError as e:
        if featured_image_path and featured_image_path != existing_post.featured_image:
            PostService.delete_image_file(featured_image_path, UPLOAD_DIR)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "errors": [
                    {
                        "field": ".".join(str(loc) for loc in error["loc"]),
                        "message": error["msg"],
                        "type": error["type"]
                    }
                    for error in e.errors()
                ]
            }
        )

    try:
        updated_post = await PostService.update_post(session, post_uuid, post_data, current_user.id)
        PostService.cleanup_old_image(old_image_path, featured_image_path, UPLOAD_DIR)

        return updated_post
    except Exception as e:
        if featured_image_path and featured_image_path != existing_post.featured_image:
            PostService.delete_image_file(featured_image_path, UPLOAD_DIR)
        raise e


@router.delete("/{post_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    await PostService.soft_delete_post(session, post_uuid, current_user)
    return None


@router.post("/{post_uuid}/like", response_model=bool)
async def toggle_post_like(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.toggle_post_like(session, post_uuid, current_user.id)


# Categories endpoints
@router.get("/categories/", response_model=CategoryListResponse)
async def get_categories(
        session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(
        select(Category)
        .options(selectinload(Category.subcategories))
        .where(Category.parent_id.is_(None))
    )
    categories = result.scalars().all()

    return {"categories": categories}


@router.post("/categories/", response_model=CategoryCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: CategoryCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.create_category(session, category_data)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
        category_id: int,
        category_data: CategoryUpdate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.update_category(session, category_id, category_data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    await PostService.delete_category(session, category_id)


# Tags endpoints
@router.get("/tags/", response_model=TagListResponse)
async def get_tags(
        session: AsyncSession = Depends(get_db_session)
):
    result = await session.execute(select(Tag))
    tags = result.scalars().all()
    return {"tags": tags}


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


@router.put("/{post_uuid}/publish", response_model=PostResponse)
async def publish_post(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.publish_post(session, post_uuid, current_user)


@router.put("/{post_uuid}/unpublish", response_model=PostResponse)
async def unpublish_post(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.unpublish_post(session, post_uuid, current_user)


@router.put("/{post_uuid}/feature", response_model=PostResponse)
async def feature_post(
        post_uuid: str,
        feature: bool = True,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.feature_post(session, post_uuid, current_user, feature=feature)


@router.post("/{post_uuid}/report", response_model=ReportResponse)
async def report_post(
        post_uuid: str,
        report_data: ReportCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.report_post(session, post_uuid, report_data, current_user.id)


@router.post("/{post_uuid}/bookmark", response_model=bool)
async def bookmark_post(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.toggle_bookmark_post(session, post_uuid, current_user.id)


@router.get("/users/me/bookmarks", response_model=PostListResponse)
async def get_user_bookmarks(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    posts = await PostService.get_user_bookmarks(session, current_user.id, skip=skip, limit=limit)
    result = await session.execute(
        select(func.count()).select_from(post_bookmarks).where(post_bookmarks.c.user_id == current_user.id)
    )
    total = result.scalar_one()
    return {
        "posts": posts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.put("/{post_uuid}/flag", response_model=PostResponse)
async def flag_post(
        post_uuid: str,
        flag: bool = True,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.flag_post(session, post_uuid, current_user, flag)
