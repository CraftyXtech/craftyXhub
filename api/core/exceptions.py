
from typing import Optional, Dict, Any, Union
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ValidationException
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, DatabaseError, TimeoutError
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class CraftyXHubException(Exception):
   
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(CraftyXHubException):
   
    
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.field_errors = field_errors or {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={**(details or {}), "field_errors": self.field_errors}
        )


class AuthenticationException(CraftyXHubException):
   
    
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(CraftyXHubException):
    """Raised when user lacks required permissions."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details={
                **(details or {}),
                "required_permission": required_permission
            }
        )


class ResourceNotFoundException(CraftyXHubException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Union[str, int]] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if not message:
            if resource_id:
                message = f"{resource_type} with ID '{resource_id}' not found"
            else:
                message = f"{resource_type} not found"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={
                **(details or {}),
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class DuplicateResourceException(CraftyXHubException):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(
        self,
        resource_type: str,
        field: str,
        value: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if not message:
            message = f"{resource_type} with {field} '{value}' already exists"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            details={
                **(details or {}),
                "resource_type": resource_type,
                "field": field,
                "value": value
            }
        )


class RateLimitException(CraftyXHubException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                **(details or {}),
                "retry_after": retry_after
            }
        )


class DatabaseException(CraftyXHubException):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details={
                **(details or {}),
                "operation": operation
            }
        )


class ExternalServiceException(CraftyXHubException):
    """Raised when external service calls fail."""
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={
                **(details or {}),
                "service_name": service_name
            }
        )


class FileUploadException(CraftyXHubException):
    """Raised when file upload operations fail."""
    
    def __init__(
        self,
        message: str = "File upload failed",
        filename: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
            details={
                **(details or {}),
                "filename": filename,
                "reason": reason
            }
        )


# ---------------------------------------------------------------------------
# Application-specific Exceptions
# ---------------------------------------------------------------------------


class UserManagementError(CraftyXHubException):
    """Raised when user management operations fail."""
    
    def __init__(
        self,
        message: str = "User management operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="USER_MANAGEMENT_ERROR",
            details=details
        )


class UserNotFoundError(ResourceNotFoundException):
    """Raised when a user is not found."""
    
    def __init__(
        self,
        user_id: Optional[Union[str, int]] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            resource_type="User",
            resource_id=user_id,
            message=message,
            details=details
        )


class PermissionError(AuthorizationException):
    """Raised when user lacks required permissions."""
    
    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            required_permission=required_permission,
            details=details
        )


class ContentManagementError(CraftyXHubException):
    """Raised when content management operations fail."""
    
    def __init__(
        self,
        message: str = "Content management operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CONTENT_MANAGEMENT_ERROR",
            details=details
        )


class AuditServiceError(CraftyXHubException):
    """Raised when audit service operations fail."""
    
    def __init__(
        self,
        message: str = "Audit service operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="AUDIT_SERVICE_ERROR",
            details=details
        )


class AuthorizationError(AuthorizationException):
    """Alias for AuthorizationException for backward compatibility."""
    pass


class AuthenticationError(AuthenticationException):
    """Alias for AuthenticationException for backward compatibility."""
    pass


def create_error_response(
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    error_code: str = "INTERNAL_ERROR",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response format.
    
    Args:
        message: Human-readable error message
        status_code: HTTP status code
        error_code: Machine-readable error code
        details: Additional error details
        request_id: Unique request identifier for tracking
    
    Returns:
        Dictionary containing standardized error response
    """
    error_response = {
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return error_response


async def craftyhub_exception_handler(
    request: Request, 
    exc: CraftyXHubException
) -> JSONResponse:
    """
    Handle custom CraftyXHub exceptions.
    
    Args:
        request: FastAPI request object
        exc: CraftyXHub custom exception
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log the exception
    logger.error(
        f"CraftyXHub exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        message=exc.message,
        status_code=exc.status_code,
        error_code=exc.error_code,
        details=exc.details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTP exception
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        message=str(exc.detail),
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request object
        exc: Request validation error
    
    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Format validation errors
    field_errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_errors[field_path] = error["msg"]
    
    logger.warning(
        f"Validation error: {field_errors}",
        extra={
            "field_errors": field_errors,
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        details={"field_errors": field_errors},
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def database_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    Handle database-related exceptions.
    
    Args:
        request: FastAPI request object
        exc: Database exception
    
    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exc, IntegrityError):
        # Handle database constraint violations
        error_code = "DATABASE_CONSTRAINT_ERROR"
        message = "Data integrity constraint violation"
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, TimeoutError):
        # Handle database timeouts
        error_code = "DATABASE_TIMEOUT"
        message = "Database operation timed out"
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
    else:
        # Handle general database errors
        error_code = "DATABASE_ERROR"
        message = "Database operation failed"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    logger.error(
        f"Database exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        message=message,
        status_code=status_code,
        error_code=error_code,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Args:
        request: FastAPI request object
        exc: Unexpected exception
    
    Returns:
        JSONResponse with generic error message
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Log the full traceback for debugging
    logger.error(
        f"Unexpected exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    error_response = create_error_response(
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Custom CraftyXHub exceptions
    app.add_exception_handler(CraftyXHubException, craftyhub_exception_handler)
    
    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # Database exceptions
    app.add_exception_handler(IntegrityError, database_exception_handler)
    app.add_exception_handler(DatabaseError, database_exception_handler)
    app.add_exception_handler(TimeoutError, database_exception_handler)
    
    # General exception handler (should be last)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully") 