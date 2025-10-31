"""
Rate Limiting for Risk Agents API
Protects against abuse and ensures fair usage
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Callable
import time
import logging
from collections import defaultdict

from api.exceptions import RateLimitExceededError

logger = logging.getLogger("risk-agents-api")


class RateLimiter:
    """
    Token bucket rate limiter

    Allows bursts up to max_requests, then enforces rate limiting
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed

        Args:
            key: Rate limit key (usually IP address or user ID)

        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Get requests for this key
        key_requests = self.requests[key]

        # Remove old requests outside window
        key_requests[:] = [req_time for req_time in key_requests if req_time > window_start]

        # Check if under limit
        if len(key_requests) < self.max_requests:
            key_requests.append(now)
            return True, 0

        # Calculate retry after
        oldest_request = min(key_requests)
        retry_after = int(oldest_request + self.window_seconds - now) + 1

        return False, retry_after

    def reset(self, key: str):
        """Reset rate limit for key"""
        if key in self.requests:
            del self.requests[key]

    def get_stats(self, key: str) -> Dict[str, int]:
        """
        Get rate limit stats for key

        Returns:
            dict: Stats including remaining requests and reset time
        """
        now = time.time()
        window_start = now - self.window_seconds

        key_requests = self.requests[key]
        key_requests[:] = [req_time for req_time in key_requests if req_time > window_start]

        remaining = self.max_requests - len(key_requests)

        if key_requests:
            oldest = min(key_requests)
            reset_time = int(oldest + self.window_seconds - now) + 1
        else:
            reset_time = self.window_seconds

        return {
            "limit": self.max_requests,
            "remaining": max(0, remaining),
            "reset": reset_time,
            "window": self.window_seconds
        }


# Global rate limiters

# Default rate limiter (100 requests per minute)
default_limiter = RateLimiter(max_requests=100, window_seconds=60)

# Strict rate limiter for auth endpoints (10 requests per minute)
auth_limiter = RateLimiter(max_requests=10, window_seconds=60)

# Generous rate limiter for read-only endpoints (500 requests per minute)
read_limiter = RateLimiter(max_requests=500, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware

    Applies rate limits based on client IP or user ID
    """

    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter = None,
        key_func: Callable = None
    ):
        """
        Initialize rate limit middleware

        Args:
            app: ASGI application
            limiter: Rate limiter instance (default: default_limiter)
            key_func: Function to extract rate limit key from request
        """
        super().__init__(app)
        self.limiter = limiter or default_limiter
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request: Request) -> str:
        """
        Default key function: use client IP

        Args:
            request: FastAPI request

        Returns:
            str: Rate limit key
        """
        # Try to get user from token (if authenticated)
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.user_id}"

        # Fall back to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check rate limit and process request

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response: HTTP response

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        # Get rate limit key
        key = self.key_func(request)

        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(key)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {key}")
            raise RateLimitExceededError(retry_after=retry_after)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        stats = self.limiter.get_stats(key)
        response.headers["X-RateLimit-Limit"] = str(stats["limit"])
        response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
        response.headers["X-RateLimit-Reset"] = str(stats["reset"])

        return response


# Route-specific rate limit decorator

def rate_limit(limiter: RateLimiter = default_limiter):
    """
    Decorator for route-specific rate limiting

    Args:
        limiter: Rate limiter to use

    Example:
        @router.post("/expensive-operation")
        @rate_limit(strict_limiter)
        async def expensive_operation():
            ...
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get rate limit key
            client_host = request.client.host if request.client else "unknown"
            key = f"ip:{client_host}"

            # Check rate limit
            allowed, retry_after = limiter.is_allowed(key)

            if not allowed:
                logger.warning(f"Rate limit exceeded for {key} on {func.__name__}")
                raise RateLimitExceededError(retry_after=retry_after)

            # Call function
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# Helper functions

def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key from request

    Uses user ID if authenticated, otherwise IP address

    Args:
        request: FastAPI request

    Returns:
        str: Rate limit key
    """
    # Try to get user from request state
    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user.user_id}"

    # Fall back to IP
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


def check_rate_limit(request: Request, limiter: RateLimiter = default_limiter):
    """
    Check rate limit for request

    Args:
        request: FastAPI request
        limiter: Rate limiter to use

    Raises:
        RateLimitExceededError: If rate limit exceeded
    """
    key = get_rate_limit_key(request)
    allowed, retry_after = limiter.is_allowed(key)

    if not allowed:
        logger.warning(f"Rate limit exceeded for {key}")
        raise RateLimitExceededError(retry_after=retry_after)
