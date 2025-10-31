"""
Custom Middleware for Risk Agents API
Provides logging, timing, request tracking, and error handling
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
import logging
from typing import Callable
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("risk-agents-api")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request for tracking

    The request ID is:
    - Generated as a UUID
    - Added to response headers
    - Available in request.state for logging
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store in request state for access by other middleware/routes
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all API requests and responses

    Logs:
    - Request method, path, client IP
    - Request headers (excluding sensitive data)
    - Response status code
    - Request/response timing
    """

    def __init__(self, app: ASGIApp, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get request ID (set by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")

        # Extract client info
        client_host = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Client: {client_host}"
        )

        # Optionally log request body (for debugging)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Note: This consumes the body, so we'd need to reconstruct it
                # For production, consider using a request body logger that preserves the stream
                pass
            except Exception as e:
                logger.warning(f"[{request_id}] Could not log request body: {e}")

        # Process request
        try:
            response = await call_next(request)

            # Log response
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Status: {response.status_code}"
            )

            return response

        except Exception as e:
            # Log errors
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Error: {str(e)}",
                exc_info=True
            )
            raise


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Measure and log request processing time

    Adds:
    - X-Process-Time header with duration in seconds
    - Logs slow requests (> 1 second)
    """

    def __init__(self, app: ASGIApp, slow_threshold: float = 1.0):
        super().__init__(app)
        self.slow_threshold = slow_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get request ID
        request_id = getattr(request.state, "request_id", "unknown")

        # Start timer
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        # Log slow requests
        if process_time > self.slow_threshold:
            logger.warning(
                f"[{request_id}] SLOW REQUEST: {request.method} {request.url.path} - "
                f"Duration: {process_time:.3f}s"
            )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handler for unhandled exceptions

    Catches:
    - Unhandled exceptions
    - Server errors
    - Unexpected failures

    Returns:
    - Consistent error response format
    - Request ID for debugging
    - Appropriate status codes
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            return await call_next(request)

        except Exception as e:
            # Log the error
            logger.error(
                f"[{request_id}] Unhandled exception: {str(e)}",
                exc_info=True
            )

            # Return error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(e),
                    "request_id": request_id,
                    "path": str(request.url.path)
                },
                headers={"X-Request-ID": request_id}
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses

    Headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (for HTTPS)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add HSTS for HTTPS (only in production)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# Middleware utility functions

def get_request_id(request: Request) -> str:
    """
    Get request ID from request state

    Args:
        request: FastAPI Request object

    Returns:
        str: Request ID or "unknown" if not set
    """
    return getattr(request.state, "request_id", "unknown")


def log_request_info(request: Request, extra_info: dict = None):
    """
    Log detailed request information

    Args:
        request: FastAPI Request object
        extra_info: Additional information to log
    """
    request_id = get_request_id(request)

    info = {
        "request_id": request_id,
        "method": request.method,
        "path": str(request.url.path),
        "query_params": dict(request.query_params),
        "client": request.client.host if request.client else "unknown",
    }

    if extra_info:
        info.update(extra_info)

    logger.info(f"Request details: {json.dumps(info)}")
