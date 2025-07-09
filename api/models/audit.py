from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User

class UserManagementLog(SQLModel, table=True):
    """Audit log for user management operations by admins."""
    __tablename__ = "user_management_logs"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    admin_id: UUID = Field(foreign_key="users.id", index=True)
    target_user_id: Optional[UUID] = Field(default=None, index=True)  # May be null for bulk operations
    action: str = Field(max_length=50, index=True)  # 'role_update', 'delete', 'create', 'activate', 'deactivate'
    old_values: Optional[str] = None  # JSON string
    new_values: Optional[str] = None  # JSON string
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 support
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ContentApproval(SQLModel, table=True):
    """Audit log for content approval operations."""
    __tablename__ = "content_approvals"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    content_type: str = Field(max_length=20, index=True)  # 'post' or 'comment'
    content_id: UUID = Field(index=True)
    admin_id: UUID = Field(foreign_key="users.id", index=True)
    action: str = Field(max_length=20, index=True)  # 'approved', 'rejected', 'pending'
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Setting(SQLModel, table=True):
    """Site configuration settings."""
    __tablename__ = "settings"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(unique=True, max_length=100, index=True)
    value: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SystemOperation(SQLModel, table=True):
    """Log for system operations like cache clearing, migrations."""
    __tablename__ = "system_operations"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    operation_type: str = Field(max_length=50, index=True)  # 'cache_clear', 'migration', 'config_update'
    admin_id: UUID = Field(foreign_key="users.id", index=True)
    parameters: Optional[str] = None  # JSON string
    status: str = Field(max_length=20, index=True)  # 'success', 'failure', 'in_progress'
    output: Optional[str] = None  # Operation output/logs
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: Optional[datetime] = None


# Access audit log for authorization middleware
class AccessAuditLog(SQLModel, table=True):
    """Audit log for access attempts and authorization decisions."""
    __tablename__ = "access_audit_log"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="users.id", default=None, index=True)
    attempted_route: str = Field(max_length=255, index=True)
    route_method: str = Field(max_length=10)
    user_role: Optional[str] = Field(max_length=20)
    required_permission: str = Field(max_length=50)
    access_granted: bool = Field(index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = None
    request_headers: Optional[str] = None  # JSON string
    denial_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True) 