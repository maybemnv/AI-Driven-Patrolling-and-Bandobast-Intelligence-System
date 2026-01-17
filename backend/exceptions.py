"""Custom exceptions for the application."""

from typing import Optional


class AppError(Exception):
    """Base exception for application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(AppError):
    """Request validation failed."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field} if field else {},
        )


class DuplicateError(AppError):
    """Duplicate resource."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} already exists: {identifier}",
            error_code="DUPLICATE",
            status_code=409,
            details={"resource": resource, "identifier": identifier},
        )


class AuthenticationError(AppError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTH_REQUIRED",
            status_code=401,
        )


class AuthorizationError(AppError):
    """Authorization failed."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            status_code=403,
        )


class RateLimitError(AppError):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMITED",
            status_code=429,
            details={"retry_after": retry_after},
        )


class ExternalServiceError(AppError):
    """External service call failed."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service},
        )
