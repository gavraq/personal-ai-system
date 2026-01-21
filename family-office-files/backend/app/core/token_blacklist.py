"""
Token blacklist service using Redis for logout and token invalidation.

This module provides functionality to:
- Add tokens to a blacklist on logout
- Check if tokens are blacklisted during authentication
- Automatic expiry of blacklisted tokens (matching their original TTL)
"""
import redis
from typing import Optional
from datetime import datetime

from .config import get_settings

settings = get_settings()

# Redis client for token blacklist
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client singleton.

    Returns:
        Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def blacklist_token(jti: str, exp: datetime) -> bool:
    """
    Add a token to the blacklist.

    The token is stored with TTL matching its expiration time,
    so it automatically gets removed when the token would have expired anyway.

    Args:
        jti: JWT token ID (unique identifier for the token)
        exp: Token expiration datetime

    Returns:
        True if successfully blacklisted, False otherwise
    """
    try:
        client = get_redis_client()

        # Calculate TTL (seconds until expiration)
        now = datetime.utcnow()
        ttl_seconds = int((exp - now).total_seconds())

        # Only blacklist if token hasn't expired
        if ttl_seconds <= 0:
            return True  # Token already expired, no need to blacklist

        # Store in Redis with automatic expiry
        key = f"blacklist:{jti}"
        client.setex(key, ttl_seconds, "1")

        return True
    except redis.RedisError:
        # Log error but don't crash - security degraded but app continues
        return False


def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        jti: JWT token ID to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    try:
        client = get_redis_client()
        key = f"blacklist:{jti}"
        return client.exists(key) > 0
    except redis.RedisError:
        # On Redis error, fail open (allow token) to prevent DoS
        # In production, you might want to fail closed instead
        return False


def blacklist_all_user_tokens(user_id: str, until: datetime) -> bool:
    """
    Blacklist all tokens for a user (for password change, account lock, etc.)

    This adds a user-level blacklist entry that invalidates all tokens
    issued before the specified time.

    Args:
        user_id: User ID to blacklist
        until: Tokens issued before this time are invalidated

    Returns:
        True if successfully blacklisted, False otherwise
    """
    try:
        client = get_redis_client()

        # Store the timestamp - any token with iat < this is invalid
        key = f"user_blacklist:{user_id}"
        # Keep for max refresh token lifetime (7 days)
        ttl_seconds = settings.refresh_token_expiry_days * 24 * 60 * 60
        client.setex(key, ttl_seconds, until.isoformat())

        return True
    except redis.RedisError:
        return False


def get_user_blacklist_timestamp(user_id: str) -> Optional[datetime]:
    """
    Get the blacklist timestamp for a user.

    Args:
        user_id: User ID to check

    Returns:
        Datetime before which tokens are invalid, or None if no blacklist
    """
    try:
        client = get_redis_client()
        key = f"user_blacklist:{user_id}"
        value = client.get(key)
        if value:
            return datetime.fromisoformat(value)
        return None
    except redis.RedisError:
        return None
