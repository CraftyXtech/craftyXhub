"""
Web schemas for public-facing API endpoints.

This module contains Pydantic models for public web API endpoints
including posts, comments, interactions, and user profiles.
"""

from .posts import *
from .comments import *
from .interactions import *
from .profile import *

__all__ = [
    # Post schemas
    "PostListFilters",
    "PostSummaryResponse",
    "PostListResponse", 
    "PostDetailResponse",
    "CategoryWithCountResponse",
    "SEODataResponse",
    "RelatedPostResponse",
    
    # Comment schemas
    "CommentCreateRequest",
    "CommentResponse",
    "CommentThreadResponse",
    "CommentSubmissionResponse",
    
    # Interaction schemas
    "InteractionResponse",
    "InteractionCountsResponse",
    "InteractionStatusResponse",
    "BulkInteractionRequest",
    "BulkInteractionResponse",
    
    # Profile schemas
    "UserProfileResponse",
    "UserDetailResponse",
    "UserActivityStatsResponse",
    "PaginatedPostsResponse",
    "PostWithInteractionResponse",
    "UserPreferencesRequest",
    "UserPreferencesResponse",
    "UserActivityResponse",
] 