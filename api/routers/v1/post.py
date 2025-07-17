import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional, List

from services.post.post_service import PostService, UPLOAD_DIR
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
from models import User, Category, Tag
from fastapi import Form, File, UploadFile
from fastapi.responses import FileResponse


router = APIRouter(prefix="/posts", tags=["Posts"])


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
    return  await PostService.get_post_with_relationships(session, post.id)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        title: str = Form(...),
        slug: str = Form(...),
        content: str = Form(...),
        excerpt: Optional[str] = Form(None),
        meta_title: Optional[str] = Form(None),
        meta_description: Optional[str] = Form(None),
        category_id: Optional[int] = Form(None),
        tag_ids: Optional[str] = Form(None),  
        reading_time: Optional[int] = Form(None),
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
            parsed_tag_ids = json.loads(tag_ids)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Must be valid JSON array."
            )
    
    post_data = PostCreate(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        meta_title=meta_title,
        meta_description=meta_description,
        category_id=category_id,
        tag_ids=parsed_tag_ids,
        reading_time=reading_time,
        featured_image=featured_image_path
    )
    
    try:
        post = await PostService.create_post(session, post_data, current_user.id)
        return post
    except Exception as e:
        if featured_image_path and os.path.exists(featured_image_path):
            os.remove(featured_image_path)
        raise e
    
@router.get("/images/{filename}")
async def get_image(filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(file_path)


@router.put("/{post_uuid}", response_model=PostResponse)
async def update_post(
    post_uuid: str,
    title: Optional[str] = Form(None),
    slug: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    tag_ids: Optional[str] = Form(None),
    reading_time: Optional[int] = Form(None),
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
    
    featured_image_path = None
    old_image_path = existing_post.featured_image
    
    if featured_image and featured_image.filename:
        featured_image_path = await PostService.save_uploaded_file(featured_image, UPLOAD_DIR)
    else:
        featured_image_path = existing_post.featured_image
    
    parsed_tag_ids = None
    if tag_ids:
        try:
            parsed_tag_ids = json.loads(tag_ids)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag_ids format. Must be valid JSON array."
            )
    
    update_data = {}
    
    if title is not None:
        update_data['title'] = title
    if slug is not None:
        update_data['slug'] = slug
    if content is not None:
        update_data['content'] = content
    if excerpt is not None:
        update_data['excerpt'] = excerpt
    if meta_title is not None:
        update_data['meta_title'] = meta_title
    if meta_description is not None:
        update_data['meta_description'] = meta_description
    if category_id is not None:
        update_data['category_id'] = category_id
    if parsed_tag_ids is not None:
        update_data['tag_ids'] = parsed_tag_ids
    if reading_time is not None:
        update_data['reading_time'] = reading_time
   
    
    if (featured_image and featured_image.filename):
        update_data['featured_image'] = featured_image_path
    
    post_data = PostUpdate(**update_data)
    
    try:
        updated_post = await PostService.update_post(session, post_uuid, post_data, current_user.id)
        
        if old_image_path and old_image_path != featured_image_path:
            old_file_path = UPLOAD_DIR / os.path.basename(old_image_path)
            if old_file_path.exists():
                os.remove(old_file_path)
        
        return updated_post
    except Exception as e:
        if featured_image_path and featured_image_path != existing_post.featured_image:
            new_file_path = UPLOAD_DIR / os.path.basename(featured_image_path)
            if new_file_path.exists():
                os.remove(new_file_path)
        raise e


@router.delete("/{post_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    await PostService.delete_post(session, post_uuid, current_user.id)
    return None


@router.post("/{post_uuid}/like", response_model=bool)
async def toggle_post_like(
        post_uuid: str,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session)
):
    return await PostService.toggle_post_like(session, post_uuid, current_user.id)


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