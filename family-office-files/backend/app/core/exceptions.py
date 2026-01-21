"""
Custom exception classes and global error handlers for consistent API error responses.

Error Response Format:
{
    "error": "ERROR_CODE",           # Machine-readable error code (e.g., "VALIDATION_ERROR")
    "message": "Human-readable message",
    "details": {...}                  # Optional additional context
}
"""
from enum import Enum
from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""
    # Authentication errors (401)
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Permission errors (403)
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Not found errors (404)
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # Validation errors (400/422)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    INVALID_INPUT = "INVALID_INPUT"

    # Conflict errors (409)
    CONFLICT = "CONFLICT"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Server errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"

    # Rate limiting (429)
    RATE_LIMITED = "RATE_LIMITED"


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str
    message: str
    details: Optional[dict[str, Any]] = None


class AppException(Exception):
    """
    Base application exception that converts to a standardized API error response.

    Usage:
        raise AppException(
            status_code=400,
            error=ErrorCode.VALIDATION_ERROR,
            message="Invalid email format"
        )
    """
    def __init__(
        self,
        status_code: int,
        error: ErrorCode | str,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error = error.value if isinstance(error, ErrorCode) else error
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception (404)."""
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error=ErrorCode.NOT_FOUND,
            message=message,
            details=details,
        )


class UnauthorizedException(AppException):
    """Authentication required exception (401)."""
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error=ErrorCode.UNAUTHORIZED,
            message=message,
            details=details,
        )


class ForbiddenException(AppException):
    """Permission denied exception (403)."""
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error=ErrorCode.FORBIDDEN,
            message=message,
            details=details,
        )


class ValidationException(AppException):
    """Validation error exception (400)."""
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
        )


class ConflictException(AppException):
    """Resource conflict exception (409)."""
    def __init__(
        self,
        message: str = "Resource already exists",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error=ErrorCode.CONFLICT,
            message=message,
            details=details,
        )


class InternalServerException(AppException):
    """Internal server error exception (500)."""
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=ErrorCode.INTERNAL_ERROR,
            message=message,
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for AppException and subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error,
            message=exc.message,
            details=exc.details,
        ).model_dump(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for standard HTTP exceptions to convert to our format."""
    # Map status codes to error codes
    error_code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMITED,
        500: ErrorCode.INTERNAL_ERROR,
    }

    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_code.value,
            message=str(exc.detail) if exc.detail else "An error occurred",
            details=None,
        ).model_dump(exclude_none=True),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors."""
    # Extract validation error details
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error["loc"])
        errors.append({
            "field": loc,
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=ErrorCode.VALIDATION_ERROR.value,
            message="Request validation failed",
            details={"validation_errors": errors},
        ).model_dump(exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected exceptions to prevent stack traces in responses."""
    # Log the actual exception (in production, use proper logging)
    import logging
    logging.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorCode.INTERNAL_ERROR.value,
            message="An unexpected error occurred",
            details=None,
        ).model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
