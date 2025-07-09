"""
Pagination dependencies for web endpoints.

Provides reusable pagination logic for public-facing API endpoints
with proper validation and metadata generation.
"""

from typing import Optional, Tuple, Dict, Any
from math import ceil
from fastapi import Query, HTTPException
from pydantic import BaseModel

from schemas.web.posts import PaginationResponse


class PaginationParams(BaseModel):
    """Pagination parameters for web endpoints."""
    
    page: int = 1
    per_page: int = 9
    
    def __init__(self, page: int = 1, per_page: int = 9):
        super().__init__(page=page, per_page=per_page)
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.per_page


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(9, ge=1, le=50, description="Items per page")
) -> PaginationParams:
    """
    Get pagination parameters from query string.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page (max 50)
        
    Returns:
        PaginationParams: Validated pagination parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be greater than 0")
    
    if per_page < 1 or per_page > 50:
        raise HTTPException(status_code=422, detail="Per page must be between 1 and 50")
    
    return PaginationParams(page=page, per_page=per_page)


def create_pagination_response(
    page: int,
    per_page: int,
    total_count: int
) -> PaginationResponse:
    """
    Create pagination response metadata.
    
    Args:
        page: Current page number
        per_page: Items per page
        total_count: Total number of items
        
    Returns:
        PaginationResponse: Pagination metadata
    """
    total_pages = ceil(total_count / per_page) if total_count > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginationResponse(
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )


def paginate_query_results(
    results: list,
    page: int,
    per_page: int,
    total_count: int
) -> Tuple[list, PaginationResponse]:
    """
    Paginate query results and create pagination metadata.
    
    Args:
        results: List of query results
        page: Current page number
        per_page: Items per page
        total_count: Total number of items
        
    Returns:
        Tuple of (paginated_results, pagination_metadata)
    """
    pagination = create_pagination_response(page, per_page, total_count)
    return results, pagination


class SearchParams(BaseModel):
    """Search parameters for web endpoints."""
    
    q: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    sort_by: str = "published_at"
    sort_direction: str = "desc"
    
    def __init__(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        sort_by: str = "published_at",
        sort_direction: str = "desc"
    ):
        super().__init__(
            q=q,
            category=category,
            tag=tag,
            sort_by=sort_by,
            sort_direction=sort_direction
        )
    
    @property
    def has_search(self) -> bool:
        """Check if search query is provided."""
        return self.q is not None and len(self.q.strip()) > 0
    
    @property
    def has_category_filter(self) -> bool:
        """Check if category filter is provided."""
        return self.category is not None and len(self.category.strip()) > 0
    
    @property
    def has_tag_filter(self) -> bool:
        """Check if tag filter is provided."""
        return self.tag is not None and len(self.tag.strip()) > 0
    
    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return self.has_search or self.has_category_filter or self.has_tag_filter
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for response."""
        return {
            "q": self.q,
            "category": self.category,
            "tag": self.tag,
            "sort_by": self.sort_by,
            "sort_direction": self.sort_direction
        }


def get_search_params(
    q: Optional[str] = Query(None, max_length=200, description="Search query"),
    category: Optional[str] = Query(None, description="Category slug"),
    tag: Optional[str] = Query(None, description="Tag slug"),
    sort_by: str = Query("published_at", description="Sort field"),
    sort_direction: str = Query("desc", description="Sort direction")
) -> SearchParams:
    """
    Get search parameters from query string.
    
    Args:
        q: Search query
        category: Category slug
        tag: Tag slug
        sort_by: Sort field
        sort_direction: Sort direction
        
    Returns:
        SearchParams: Validated search parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    # Validate sort_by
    allowed_sorts = ['published_at', 'title', 'view_count', 'like_count', 'created_at']
    if sort_by not in allowed_sorts:
        raise HTTPException(
            status_code=422,
            detail=f"sort_by must be one of {allowed_sorts}"
        )
    
    # Validate sort_direction
    if sort_direction not in ['asc', 'desc']:
        raise HTTPException(
            status_code=422,
            detail="sort_direction must be 'asc' or 'desc'"
        )
    
    # Validate search query length
    if q and len(q.strip()) < 2:
        raise HTTPException(
            status_code=422,
            detail="Search query must be at least 2 characters"
        )
    
    return SearchParams(
        q=q.strip() if q else None,
        category=category.strip() if category else None,
        tag=tag.strip() if tag else None,
        sort_by=sort_by,
        sort_direction=sort_direction
    )


def get_comment_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Comments per page")
) -> PaginationParams:
    """
    Get pagination parameters for comments.
    
    Args:
        page: Page number (1-based)
        per_page: Comments per page (max 100)
        
    Returns:
        PaginationParams: Validated pagination parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be greater than 0")
    
    if per_page < 1 or per_page > 100:
        raise HTTPException(status_code=422, detail="Per page must be between 1 and 100")
    
    return PaginationParams(page=page, per_page=per_page)


def get_profile_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=50, description="Posts per page")
) -> PaginationParams:
    """
    Get pagination parameters for profile collections.
    
    Args:
        page: Page number (1-based)
        per_page: Posts per page (max 50)
        
    Returns:
        PaginationParams: Validated pagination parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be greater than 0")
    
    if per_page < 1 or per_page > 50:
        raise HTTPException(status_code=422, detail="Per page must be between 1 and 50")
    
    return PaginationParams(page=page, per_page=per_page) 