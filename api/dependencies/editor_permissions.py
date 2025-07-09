"""Editor permissions and access control dependencies."""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .auth import get_current_user
from .database import get_db
from models.user import User
from models.post import Post
from models.category import Category
from models.tag import Tag
from services.admin.audit_service import AuditService


async def require_editor_or_admin(
    current_user: User = Depends(get_current_user),
    request: Request = None
) -> User:
    """Ensure user has editor or admin role."""
    if not (current_user.is_editor() or current_user.is_admin()):
        # Log access attempt
        if request:
            audit_service = AuditService()
            await audit_service.log_access_attempt(
                user_id=current_user.id,
                route=request.url.path,
                required_permission="editor",
                granted=False,
                denial_reason="Insufficient role permissions"
            )
        raise HTTPException(
            status_code=403, 
            detail="Editor or Admin access required"
        )
    return current_user


async def verify_post_ownership(
    post_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
) -> Post:
    """Verify that the current user owns the post or is an admin."""
    result = await db.execute(
        select(Post).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Admins can edit any post, editors can only edit their own posts
    if not current_user.is_admin() and post.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only edit your own posts"
        )
    
    return post


async def verify_category_permissions(
    category_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
) -> Category:
    """Verify that the current user can edit the category."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Only admins or the creator can edit categories
    if not current_user.is_admin() and category.created_by != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only edit categories you created"
        )
    
    return category


async def verify_tag_permissions(
    tag_id: UUID,
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
) -> Tag:
    """Verify that the current user can edit the tag."""
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Only admins or the creator can edit tags
    if not current_user.is_admin() and tag.created_by != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only edit tags you created"
        )
    
    return tag


async def verify_post_edit_permissions(
    post: Post,
    current_user: User = Depends(require_editor_or_admin)
) -> Post:
    """Verify that the post can be edited by the current user."""
    # Published posts can only be edited by admins
    if post.status == "published" and not current_user.is_admin():
        raise HTTPException(
            status_code=403, 
            detail="Published posts can only be edited by admins"
        )
    
    # Editors can only edit their own posts
    if not current_user.is_admin() and post.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="You can only edit your own posts"
        )
    
    return post


async def verify_post_publish_permissions(
    post: Post,
    current_user: User = Depends(require_editor_or_admin)
) -> Post:
    """Verify that the post can be published by the current user."""
    # Only admins can publish posts
    if not current_user.is_admin():
        raise HTTPException(
            status_code=403, 
            detail="Only admins can publish posts"
        )
    
    return post


async def verify_bulk_operation_permissions(
    post_ids: list[UUID],
    current_user: User = Depends(require_editor_or_admin),
    db: AsyncSession = Depends(get_db)
) -> list[Post]:
    """Verify that the current user can perform bulk operations on the posts."""
    result = await db.execute(
        select(Post).where(Post.id.in_(post_ids))
    )
    posts = result.scalars().all()
    
    if len(posts) != len(post_ids):
        raise HTTPException(
            status_code=404, 
            detail="One or more posts not found"
        )
    
    # Verify permissions for each post
    for post in posts:
        if not current_user.is_admin() and post.user_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail=f"You don't have permission to modify post: {post.title}"
            )
    
    return posts


def check_post_permissions(post: Post, current_user: User) -> dict:
    """Check what permissions the current user has for a post."""
    is_owner = post.user_id == current_user.id
    is_admin = current_user.is_admin()
    
    return {
        "can_edit": is_owner or is_admin,
        "can_delete": is_owner or is_admin,
        "can_publish": is_admin,
        "can_submit_review": is_owner and post.status == "draft",
        "can_resubmit": is_owner and post.status == "rejected"
    }


def check_category_permissions(category: Category, current_user: User) -> dict:
    """Check what permissions the current user has for a category."""
    is_creator = category.created_by == current_user.id
    is_admin = current_user.is_admin()
    
    return {
        "can_edit": is_creator or is_admin,
        "can_delete": is_creator or is_admin
    }


def check_tag_permissions(tag: Tag, current_user: User) -> dict:
    """Check what permissions the current user has for a tag."""
    is_creator = tag.created_by == current_user.id
    is_admin = current_user.is_admin()
    
    return {
        "can_edit": is_creator or is_admin,
        "can_delete": is_creator or is_admin
    } 