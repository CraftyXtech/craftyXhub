from typing import Dict, List, Optional, Set, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import json
from datetime import datetime

from models.user import User
from schemas.auth import UserRole
from services.admin.audit_service import AuditService
from dependencies.auth import get_current_user
from core.exceptions import AuthorizationError

logger = logging.getLogger(__name__)


class AuthorizationMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.protected_routes = self._initialize_protected_routes()
        self.audit_service: Optional[AuditService] = None
    
    async def dispatch(self, request: Request, call_next: Callable):
        
        try:
            if not self.audit_service:
                from dependencies.database import get_db
                db = await anext(get_db())
                self.audit_service = AuditService(db)
            
            route_path = request.url.path
            method = request.method
            
            if not self._requires_authorization(route_path, method):
                return await call_next(request)
            
            try:
                current_user = await self._get_current_user_from_request(request)
            except Exception:
                current_user = None
            
            access_granted = await self._check_route_access(
                current_user, route_path, method, request
            )
            
            if not access_granted:
                await self._log_unauthorized_access(
                    current_user, route_path, method, request
                )
                
                if not current_user:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": "Authentication required",
                            "type": "authentication_required"
                        },
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                else:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Access denied",
                            "type": "insufficient_permissions"
                        }
                    )
            
            await self._log_successful_access(
                current_user, route_path, method, request
            )
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Authorization middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    def _initialize_protected_routes(self) -> Dict[str, Dict[str, str]]:
       
        return {
            # Admin routes - require admin role
            "/admin": {"permission": "admin", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/admin/": {"permission": "admin", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/admin/*": {"permission": "admin", "methods": ["GET", "POST", "PUT", "DELETE"]},
            
            # Editor routes - require editor or admin role
            "/editor": {"permission": "editor", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/editor/": {"permission": "editor", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/editor/*": {"permission": "editor", "methods": ["GET", "POST", "PUT", "DELETE"]},
            
            # API admin endpoints
            "/api/v1/admin": {"permission": "admin", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/api/v1/admin/*": {"permission": "admin", "methods": ["GET", "POST", "PUT", "DELETE"]},
            
            # API editor endpoints
            "/api/v1/editor": {"permission": "editor", "methods": ["GET", "POST", "PUT", "DELETE"]},
            "/api/v1/editor/*": {"permission": "editor", "methods": ["GET", "POST", "PUT", "DELETE"]},
            
            # Specific protected endpoints
            "/api/v1/posts/*/delete": {"permission": "editor", "methods": ["DELETE"]},
            "/api/v1/posts/*/publish": {"permission": "editor", "methods": ["POST"]},
            "/api/v1/users/*/role": {"permission": "admin", "methods": ["PUT"]},
            "/api/v1/users/*/delete": {"permission": "admin", "methods": ["DELETE"]},
        }
    
    def _requires_authorization(self, path: str, method: str) -> bool:
        public_patterns = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/posts",
            "/api/v1/posts/",
            "/api/v1/categories",
            "/api/v1/tags",
            "/web/posts",
            "/web/posts/",
            "/web/categories",
            "/web/comments",
        ]
        
        for pattern in public_patterns:
            if self._path_matches_pattern(path, pattern):
                return False
        
        for pattern, config in self.protected_routes.items():
            if self._path_matches_pattern(path, pattern):
                if method in config["methods"]:
                    return True
        
        protected_prefixes = ["/admin", "/editor", "/api/v1/admin", "/api/v1/editor"]
        return any(path.startswith(prefix) for prefix in protected_prefixes)
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return path.startswith(prefix)
        else:
            return path == pattern
    
    async def _get_current_user_from_request(self, request: Request) -> Optional[User]:
        
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            
            return None
            
        except Exception:
            return None
    
    async def _check_route_access(
        self, 
        user: Optional[User], 
        path: str, 
        method: str,
        request: Request
    ) -> bool:
        
        # Find matching route pattern
        required_permission = None
        for pattern, config in self.protected_routes.items():
            if self._path_matches_pattern(path, pattern):
                if method in config["methods"]:
                    required_permission = config["permission"]
                    break
        
        if not required_permission:
            return True
        
        if not user:
            return False
        
        return self._user_has_permission(user, required_permission)
    
    def _user_has_permission(self, user: User, permission: str) -> bool:
        
        if permission == "admin":
            return user.role == "admin"
        elif permission == "editor":
            return user.role in ["admin", "editor"]
        elif permission == "user":
            return user.role in ["admin", "editor", "user"]
        
        return False
    
    async def _log_unauthorized_access(
        self, 
        user: Optional[User], 
        path: str, 
        method: str,
        request: Request
    ):
        
        try:
            if self.audit_service:
                await self.audit_service.log_access_attempt(
                    user_id=user.id if user else None,
                    route=path,
                    required_permission=self._get_required_permission(path, method),
                    granted=False,
                    method=method,
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get("User-Agent"),
                    denial_reason="Insufficient permissions" if user else "Not authenticated"
                )
        except Exception as e:
            logger.error(f"Failed to log unauthorized access: {str(e)}")
    
    async def _log_successful_access(
        self, 
        user: Optional[User], 
        path: str, 
        method: str,
        request: Request
    ):
        
        try:
            # Only log access to sensitive routes
            sensitive_prefixes = ["/admin", "/api/v1/admin"]
            if any(path.startswith(prefix) for prefix in sensitive_prefixes):
                if self.audit_service and user:
                    await self.audit_service.log_access_attempt(
                        user_id=user.id,
                        route=path,
                        required_permission=self._get_required_permission(path, method),
                        granted=True,
                        method=method,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.headers.get("User-Agent")
                    )
        except Exception as e:
            logger.error(f"Failed to log successful access: {str(e)}")

    def _get_required_permission(self, path: str, method: str) -> str:
        
        for pattern, config in self.protected_routes.items():
            if self._path_matches_pattern(path, pattern):
                if method in config["methods"]:
                    return config["permission"]
        
        return "unknown"
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None


class AuthorizationUtils:
    
    @staticmethod
    def check_admin_access(user: Optional[User]) -> bool:
        """Check if user has admin access."""
        return user is not None and user.role == "admin"
    
    @staticmethod
    def check_editor_access(user: Optional[User]) -> bool:
        """Check if user has editor access."""
        return user is not None and user.role in ["admin", "editor"]
    
    @staticmethod
    def check_user_access(user: Optional[User]) -> bool:
        """Check if user has basic user access."""
        return user is not None and user.role in ["admin", "editor", "user"]
    
    @staticmethod
    def check_permission(user: Optional[User], permission: str) -> bool:
        """Check if user has specific permission."""
        if not user:
            return False
        
        permission_map = {
            "admin": ["admin"],
            "editor": ["admin", "editor"],
            "user": ["admin", "editor", "user"]
        }
        
        allowed_roles = permission_map.get(permission, [])
        return user.role in allowed_roles
    
    @staticmethod
    def require_permission(required_permission: str):
        
        def decorator(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator


# Route access configuration
ROUTE_PERMISSIONS = {
    # Admin routes
    "admin_dashboard": {"roles": ["admin"], "resource": "admin.dashboard"},
    "admin_users": {"roles": ["admin"], "resource": "admin.users"},
    "admin_settings": {"roles": ["admin"], "resource": "admin.settings"},
    "admin_analytics": {"roles": ["admin"], "resource": "admin.analytics"},
    
    # Editor routes
    "editor_posts": {"roles": ["admin", "editor"], "resource": "editor.posts"},
    "editor_categories": {"roles": ["admin", "editor"], "resource": "editor.categories"},
    "editor_tags": {"roles": ["admin", "editor"], "resource": "editor.tags"},
    "editor_dashboard": {"roles": ["admin", "editor"], "resource": "editor.dashboard"},
    
    # Content management
    "post_create": {"roles": ["admin", "editor"], "resource": "posts.create"},
    "post_edit": {"roles": ["admin", "editor"], "resource": "posts.edit"},
    "post_delete": {"roles": ["admin", "editor"], "resource": "posts.delete"},
    "post_publish": {"roles": ["admin", "editor"], "resource": "posts.publish"},
    
    # User management
    "user_edit_role": {"roles": ["admin"], "resource": "users.edit_role"},
    "user_delete": {"roles": ["admin"], "resource": "users.delete"},
    "user_view_all": {"roles": ["admin"], "resource": "users.view_all"},
} 