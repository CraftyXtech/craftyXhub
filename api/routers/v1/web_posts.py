
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.pagination import get_pagination_params, get_search_params
from dependencies.web_auth import get_optional_current_user, check_post_access
from models.user import User
from services.web.post_service import WebPostService
from schemas.web.posts import (
    PostListFilters, PostListResponse, PostDetailResponse,
    PostSearchResponse, SearchSuggestionResponse
)

router = APIRouter(prefix="/posts", tags=["Web Posts"])


@router.get("/", response_model=PostListResponse)
async def list_posts(
    request: Request,
    pagination: "PaginationParams" = Depends(get_pagination_params),
    search: "SearchParams" = Depends(get_search_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Convert search params to filters
    filters = PostListFilters(
        q=search.q,
        category=search.category,
        tag=search.tag,
        sort_by=search.sort_by,
        sort_direction=search.sort_direction
    )
    
    # Get posts list
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.get("/{slug}", response_model=PostDetailResponse)
async def get_post_by_slug(
    slug: str,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Get post by slug
    post_response = await service.get_post_by_slug(slug, current_user)
    
    if not post_response:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post_response


@router.get("/search/advanced", response_model=PostSearchResponse)
async def search_posts(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    pagination: "PaginationParams" = Depends(get_pagination_params),
    category: Optional[str] = Query(None, description="Category filter"),
    tag: Optional[str] = Query(None, description="Tag filter"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Prepare filters
    filters = {
        "category": category,
        "tag": tag
    }
    
    # Perform search
    search_response = await service.search_posts(q, filters, pagination, current_user)
    
    return search_response


@router.get("/search/suggestions", response_model=SearchSuggestionResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Get search suggestions
    suggestions_response = await service.get_search_suggestions(q, limit)
    
    return suggestions_response


@router.get("/category/{category_slug}", response_model=PostListResponse)
async def get_posts_by_category(
    category_slug: str,
    pagination: "PaginationParams" = Depends(get_pagination_params),
    sort_by: str = Query("published_at", description="Sort field"),
    sort_direction: str = Query("desc", description="Sort direction"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Create filters for category
    filters = PostListFilters(
        category=category_slug,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    # Get posts list
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.get("/tag/{tag_slug}", response_model=PostListResponse)
async def get_posts_by_tag(
    tag_slug: str,
    pagination: "PaginationParams" = Depends(get_pagination_params),
    sort_by: str = Query("published_at", description="Sort field"),
    sort_direction: str = Query("desc", description="Sort direction"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Create filters for tag
    filters = PostListFilters(
        tag=tag_slug,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    # Get posts list
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.get("/featured", response_model=PostListResponse)
async def get_featured_posts(
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Create filters for featured posts
    filters = PostListFilters(
        sort_by="published_at",
        sort_direction="desc"
    )
    
    # TODO: Add featured filter to service
    # For now, return regular posts
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.get("/trending", response_model=PostListResponse)
async def get_trending_posts(
    pagination: "PaginationParams" = Depends(get_pagination_params),
    timeframe: str = Query("week", description="Trending timeframe (day, week, month)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    # Validate timeframe
    if timeframe not in ["day", "week", "month"]:
        raise HTTPException(status_code=422, detail="Invalid timeframe")
    
    service = WebPostService(db)
    
    # Create filters for trending posts
    filters = PostListFilters(
        sort_by="view_count",  # TODO: Implement proper trending algorithm
        sort_direction="desc"
    )
    
    # Get posts list
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.get("/recent", response_model=PostListResponse)
async def get_recent_posts(
    pagination: "PaginationParams" = Depends(get_pagination_params),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):

    service = WebPostService(db)
    
    # Create filters for recent posts
    filters = PostListFilters(
        sort_by="published_at",
        sort_direction="desc"
    )
    
    # Get posts list
    posts_response = await service.get_posts_list(filters, pagination, current_user)
    
    return posts_response


@router.post("/{post_id}/view")
async def record_post_view(
    post_id: UUID,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    from services.web.interaction_service import WebInteractionService
    
    service = WebInteractionService(db)
    
    # Get client IP and user agent
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Record view
    response = await service.record_view(
        post_id=post_id,
        user=current_user,
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return {
        "success": response.success,
        "message": response.message
    } 