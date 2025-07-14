"""
Logging system for CraftyXhub FastAPI application.
Centralized logging configuration.
"""
import logging
import logging.config
import json
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp



class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that creates structured JSON logs.
    Provides consistent log formatting with additional context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from LogRecord
        extra_fields = {
            key: value for key, value in record.__dict__.items()
            if key not in [
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "getMessage", "exc_info",
                "exc_text", "stack_info"
            ]
        }
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    Tracks request performance and adds request IDs for tracing.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("craftyx.requests")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process HTTP request with logging and performance tracking.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
            
        Returns:
            HTTP response with added logging
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Track request start time
        start_time = time.time()
        
        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log incoming request
        self.logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers),
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            self.logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 3),
                    "response_size": len(response.body) if hasattr(response, 'body') else None,
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate processing time even for errors
            process_time = time.time() - start_time
            
            # Log request error
            self.logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": round(process_time, 3),
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.
        
        Args:
            request: HTTP request object
            
        Returns:
            Client IP address as string
        """
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return getattr(request.client, "host", "unknown")


class DatabaseLoggingHandler:
    """
    Handler for logging database operations and performance.
    Provides insights into database query performance and issues.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("craftyx.database")
    
    def log_query_start(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        operation_type: str = "query"
    ) -> str:
        """
        Log the start of a database query.
        
        Args:
            query: SQL query string
            params: Query parameters
            operation_type: Type of operation (query, insert, update, delete)
            
        Returns:
            Query ID for tracking
        """
        query_id = str(uuid.uuid4())
        
        self.logger.debug(
            "Database query started",
            extra={
                "query_id": query_id,
                "operation_type": operation_type,
                "query": query,
                "params": params,
            }
        )
        
        return query_id
    
    def log_query_end(
        self,
        query_id: str,
        duration: float,
        row_count: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log the completion of a database query.
        
        Args:
            query_id: Query identifier from log_query_start
            duration: Query execution time in seconds
            row_count: Number of affected/returned rows
            success: Whether query was successful
            error: Error message if query failed
        """
        log_level = logging.INFO if success else logging.ERROR
        message = "Database query completed" if success else "Database query failed"
        
        extra_data = {
            "query_id": query_id,
            "duration": round(duration, 3),
            "row_count": row_count,
            "success": success,
        }
        
        if error:
            extra_data["error"] = error
        
        self.logger.log(log_level, message, extra=extra_data)


class SecurityLoggingHandler:
    """
    Handler for logging security-related events.
    Tracks authentication, authorization, and suspicious activities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("craftyx.security")
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str] = None
    ):
        """
        Log user login attempts.
        
        Args:
            email: User email address
            success: Whether login was successful
            ip_address: Client IP address
            user_agent: Client user agent
            failure_reason: Reason for login failure
        """
        message = "User login successful" if success else "User login failed"
        log_level = logging.INFO if success else logging.WARNING
        
        extra_data = {
            "event_type": "login_attempt",
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        
        if failure_reason:
            extra_data["failure_reason"] = failure_reason
        
        self.logger.log(log_level, message, extra=extra_data)
    
    def log_permission_check(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        reason: Optional[str] = None
    ):
        """
        Log permission checks for authorization auditing.
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            granted: Whether permission was granted
            reason: Reason for permission decision
        """
        message = "Permission granted" if granted else "Permission denied"
        log_level = logging.INFO if granted else logging.WARNING
        
        self.logger.log(
            log_level,
            message,
            extra={
                "event_type": "permission_check",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "granted": granted,
                "reason": reason,
            }
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        ip_address: str,
        user_id: Optional[str] = None,
        severity: str = "medium"
    ):
        """
        Log suspicious security activities.
        
        Args:
            activity_type: Type of suspicious activity
            description: Description of the activity
            ip_address: Client IP address
            user_id: User ID if known
            severity: Severity level (low, medium, high, critical)
        """
        self.logger.warning(
            "Suspicious activity detected",
            extra={
                "event_type": "suspicious_activity",
                "activity_type": activity_type,
                "description": description,
                "ip_address": ip_address,
                "user_id": user_id,
                "severity": severity,
            }
        )


def setup_logging() -> None:
    """
    Configure application logging based on settings.
    Sets up loggers, handlers, and formatters.
    """
 
  
    
    log_file ="logs/development.log"
    log_file_path = Path(log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_level = "INFO"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers":False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
            "simple": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": log_level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "maxBytes": 10485760,
                "backupCount":  5,
                "formatter": "structured",
                "level": log_level,
            },
        },
        "loggers": {
            "craftyx": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "craftyx.requests": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "craftyx.database": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "craftyx.security": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console", "file"],
        },
    }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Log configuration success
    logger = logging.getLogger("craftyx.core")
    logger.info(
        "Logging system initialized",
        extra={
            "log_level": log_level,
            "log_file": log_file,
            "environment": "development",
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"craftyx.{name}")


# Initialize logging handlers
db_logging_handler = DatabaseLoggingHandler()
security_logging_handler = SecurityLoggingHandler() 