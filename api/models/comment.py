from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .post import Post

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    
    # Primary key and basic fields
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    post_id: UUID = Field(foreign_key="posts.id", index=True)
    user_id: Optional[UUID] = Field(foreign_key="users.id", index=True, default=None)
    parent_id: Optional[UUID] = Field(foreign_key="comments.id", index=True, default=None)
    
    # Content fields
    content: str  # TEXT field for comment content
    status: str = Field(default="pending", max_length=50, index=True)  # 'pending', 'approved', 'rejected', 'spam'
    
    # Guest user fields (nullable for registered users)
    guest_name: Optional[str] = Field(default=None, max_length=255)
    guest_email: Optional[str] = Field(default=None, max_length=255)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    post: Optional["Post"] = Relationship(back_populates="comments")
    author: Optional["User"] = Relationship(back_populates="comments")
    
    # Self-referential relationships for threading
    parent: Optional["Comment"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Comment.id",
            "back_populates": "replies"
        }
    )
    replies: List["Comment"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Comment.parent_id",
            "back_populates": "parent"
        }
    )
    
    # Social interactions (polymorphic likes)
    liked_by_users: List["User"] = Relationship(
        back_populates="liked_comments",
        sa_relationship_kwargs={"secondary": "comment_likes"}
    )
    
    def __init__(self, **data):
        """Initialize comment with validation."""
        super().__init__(**data)
        self._validate_author_info()
    
    def _validate_author_info(self) -> None:
        """Validate that either user_id or guest info is provided."""
        if not self.user_id and not (self.guest_name and self.guest_email):
            raise ValueError("Either user_id or both guest_name and guest_email must be provided")
    
    # Moderation methods
    def approve(self) -> None:
        """Approve the comment."""
        self.status = "approved"
        self.updated_at = datetime.utcnow()
    
    def reject(self) -> None:
        """Reject the comment."""
        self.status = "rejected"
        self.updated_at = datetime.utcnow()
    
    def mark_as_spam(self) -> None:
        """Mark comment as spam."""
        self.status = "spam"
        self.updated_at = datetime.utcnow()
    
    def is_approved(self) -> bool:
        """Check if comment is approved."""
        return self.status == "approved"
    
    def is_pending(self) -> bool:
        """Check if comment is pending moderation."""
        return self.status == "pending"
    
    # Threading methods
    def get_replies(self, approved_only: bool = True) -> List["Comment"]:
        """Get all replies to this comment."""
        if approved_only:
            return [reply for reply in self.replies if reply.is_approved()]
        return self.replies
    
    def get_thread_depth(self) -> int:
        """Get the depth of this comment in the thread."""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth
    
    def is_top_level(self) -> bool:
        """Check if this is a top-level comment (no parent)."""
        return self.parent_id is None
    
    # Social interaction methods
    def is_liked_by(self, user: "User") -> bool:
        """Check if comment is liked by user."""
        return user in self.liked_by_users
    
    def get_likes_count(self) -> int:
        """Get count of likes for this comment."""
        return len(self.liked_by_users)
    
    # Author methods
    def get_author_name(self) -> str:
        """Get the author name (either from User or guest)."""
        if self.author:
            return self.author.name
        return self.guest_name or "Anonymous"
    
    def get_author_email(self) -> Optional[str]:
        """Get the author email (either from User or guest)."""
        if self.author:
            return self.author.email
        return self.guest_email
    
    def is_guest_comment(self) -> bool:
        """Check if this is a guest comment."""
        return self.user_id is None
    
    def can_edit(self, user: Optional["User"]) -> bool:
        """Check if user can edit this comment."""
        if not user:
            return False
        # Only author or admin can edit
        return self.user_id == user.id or user.is_admin()
    
    def can_delete(self, user: Optional["User"]) -> bool:
        """Check if user can delete this comment."""
        if not user:
            return False
        # Author, admin, or post author can delete
        return (self.user_id == user.id or 
                user.is_admin() or 
                (self.post and self.post.user_id == user.id))


# Link table for comment likes
class CommentLike(SQLModel, table=True):
    __tablename__ = "comment_likes"
    
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    comment_id: UUID = Field(foreign_key="comments.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow) 