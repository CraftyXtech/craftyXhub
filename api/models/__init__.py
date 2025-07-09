"""
CraftyXhub Data Models

This module contains all SQLModel data models for the CraftyXhub blog platform,
implementing the specifications from PRDs/02-Data-Models/.

Models:
- User: User authentication and profile management
- Category: Content organization with hierarchical structure  
- Tag: Flexible content labeling and topic following
- Post: Core content model with publishing workflow and AI features
- Comment: Hierarchical commenting with moderation and guest support
- Social Interactions: Like, Bookmark, Follow, View for user engagement
- User Engagement: UserRead, UserTopic, UserPreference, Media for personalization
- Audit: Admin operation logging and system audit trails
"""

# Core models
from .user import (
    User, 
    Like, 
    Bookmark, 
    Follow, 
    UserTopic, 
    UserRead, 
    UserPreference, 
    Media
)
from .category import Category
from .tag import Tag, PostTag
from .post import Post
from .comment import Comment, CommentLike

# Social interaction models
from .interactions import (
    Like,
    Bookmark, 
    Follow,
    View,
    AnalyticsHelper
)

# Audit models for admin operations
from .audit import (
    UserManagementLog,
    ContentApproval,
    Setting,
    SystemOperation,
    AccessAuditLog
)

# Export all models for easy importing
__all__ = [
    # Core models
    "User",
    "Category", 
    "Tag",
    "Post",
    "Comment",
    
    # Social interaction models
    "Like",
    "Bookmark",
    "Follow", 
    "View",
    
    # Link/Junction tables
    "Like",
    "Bookmark", 
    "Follow",
    "UserTopic",
    "UserRead",
    "PostTag",
    "CommentLike",
    
    # Engagement models
    "UserPreference",
    "Media",
    
    # Audit models
    "UserManagementLog",
    "ContentApproval",
    "Setting",
    "SystemOperation",
    "AccessAuditLog",
    
    # Helper classes
    "AnalyticsHelper"
] 