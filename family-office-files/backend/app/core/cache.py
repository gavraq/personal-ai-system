"""
Redis caching service for frequently accessed data.

This module provides caching for:
- User lookups (frequently accessed during authentication)
- Deal membership lookups (checked on almost every deal operation)
- Deal details (commonly fetched)

Cache keys use prefixes for namespace isolation:
- user:{user_id} - User data by ID
- user_email:{email} - User ID lookup by email
- deal:{deal_id} - Deal data by ID
- deal_member:{deal_id}:{user_id} - Deal membership status
- deal_members:{deal_id} - List of deal member user IDs
"""
import json
import redis
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from .config import get_settings

settings = get_settings()

# Redis client singleton
_cache_client: Optional[redis.Redis] = None

# Default TTLs in seconds
USER_CACHE_TTL = 300  # 5 minutes
DEAL_CACHE_TTL = 300  # 5 minutes
MEMBERSHIP_CACHE_TTL = 60  # 1 minute (shorter since permissions matter)


def get_cache_client() -> redis.Redis:
    """
    Get or create Redis client singleton for caching.

    Returns:
        Redis client instance
    """
    global _cache_client
    if _cache_client is None:
        _cache_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _cache_client


def _serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _deserialize_datetime(data: Dict[str, Any], datetime_fields: List[str]) -> Dict[str, Any]:
    """Convert ISO format strings back to datetime objects."""
    for field in datetime_fields:
        if field in data and data[field]:
            try:
                data[field] = datetime.fromisoformat(data[field])
            except (ValueError, TypeError):
                pass
    return data


# ========================================
# User Caching
# ========================================

def cache_user(user_id: UUID, user_data: Dict[str, Any]) -> bool:
    """
    Cache user data by ID.

    Args:
        user_id: User UUID
        user_data: Dictionary of user attributes (id, email, role, created_at, updated_at)

    Returns:
        True if cached successfully, False otherwise
    """
    try:
        client = get_cache_client()
        key = f"user:{user_id}"

        # Serialize with datetime handling
        serialized = json.dumps(user_data, default=_serialize_datetime)
        client.setex(key, USER_CACHE_TTL, serialized)

        # Also cache email-to-id mapping
        if "email" in user_data:
            email_key = f"user_email:{user_data['email']}"
            client.setex(email_key, USER_CACHE_TTL, str(user_id))

        return True
    except redis.RedisError:
        return False


def get_cached_user(user_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached user data by ID.

    Args:
        user_id: User UUID

    Returns:
        User data dictionary or None if not cached
    """
    try:
        client = get_cache_client()
        key = f"user:{user_id}"
        data = client.get(key)

        if data:
            user_data = json.loads(data)
            return _deserialize_datetime(user_data, ["created_at", "updated_at"])
        return None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def get_cached_user_id_by_email(email: str) -> Optional[UUID]:
    """
    Get cached user ID by email.

    Args:
        email: User email

    Returns:
        User UUID or None if not cached
    """
    try:
        client = get_cache_client()
        key = f"user_email:{email}"
        user_id = client.get(key)

        if user_id:
            return UUID(user_id)
        return None
    except (redis.RedisError, ValueError):
        return None


def invalidate_user_cache(user_id: UUID, email: Optional[str] = None) -> bool:
    """
    Invalidate cached user data.

    Args:
        user_id: User UUID
        email: User email (optional, for email index invalidation)

    Returns:
        True if invalidated successfully, False otherwise
    """
    try:
        client = get_cache_client()
        keys_to_delete = [f"user:{user_id}"]

        if email:
            keys_to_delete.append(f"user_email:{email}")

        client.delete(*keys_to_delete)
        return True
    except redis.RedisError:
        return False


# ========================================
# Deal Caching
# ========================================

def cache_deal(deal_id: UUID, deal_data: Dict[str, Any]) -> bool:
    """
    Cache deal data by ID.

    Args:
        deal_id: Deal UUID
        deal_data: Dictionary of deal attributes

    Returns:
        True if cached successfully, False otherwise
    """
    try:
        client = get_cache_client()
        key = f"deal:{deal_id}"

        serialized = json.dumps(deal_data, default=_serialize_datetime)
        client.setex(key, DEAL_CACHE_TTL, serialized)
        return True
    except redis.RedisError:
        return False


def get_cached_deal(deal_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached deal data by ID.

    Args:
        deal_id: Deal UUID

    Returns:
        Deal data dictionary or None if not cached
    """
    try:
        client = get_cache_client()
        key = f"deal:{deal_id}"
        data = client.get(key)

        if data:
            deal_data = json.loads(data)
            return _deserialize_datetime(deal_data, ["created_at", "updated_at"])
        return None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def invalidate_deal_cache(deal_id: UUID) -> bool:
    """
    Invalidate cached deal data.

    Args:
        deal_id: Deal UUID

    Returns:
        True if invalidated successfully, False otherwise
    """
    try:
        client = get_cache_client()
        client.delete(f"deal:{deal_id}")
        return True
    except redis.RedisError:
        return False


# ========================================
# Deal Membership Caching
# ========================================

def cache_deal_membership(deal_id: UUID, user_id: UUID, is_member: bool, role_override: Optional[str] = None) -> bool:
    """
    Cache deal membership status for a user.

    Args:
        deal_id: Deal UUID
        user_id: User UUID
        is_member: Whether user is a member
        role_override: Deal-specific role override (if any)

    Returns:
        True if cached successfully, False otherwise
    """
    try:
        client = get_cache_client()
        key = f"deal_member:{deal_id}:{user_id}"

        data = {
            "is_member": is_member,
            "role_override": role_override
        }

        serialized = json.dumps(data)
        client.setex(key, MEMBERSHIP_CACHE_TTL, serialized)
        return True
    except redis.RedisError:
        return False


def get_cached_deal_membership(deal_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get cached deal membership status.

    Args:
        deal_id: Deal UUID
        user_id: User UUID

    Returns:
        Dict with is_member and role_override, or None if not cached
    """
    try:
        client = get_cache_client()
        key = f"deal_member:{deal_id}:{user_id}"
        data = client.get(key)

        if data:
            return json.loads(data)
        return None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def invalidate_deal_membership_cache(deal_id: UUID, user_id: Optional[UUID] = None) -> bool:
    """
    Invalidate deal membership cache.

    If user_id is provided, only that user's membership is invalidated.
    If user_id is None, all memberships for the deal are invalidated.

    Args:
        deal_id: Deal UUID
        user_id: User UUID (optional)

    Returns:
        True if invalidated successfully, False otherwise
    """
    try:
        client = get_cache_client()

        if user_id:
            # Invalidate specific membership
            client.delete(f"deal_member:{deal_id}:{user_id}")
        else:
            # Invalidate all memberships for the deal (pattern delete)
            pattern = f"deal_member:{deal_id}:*"
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=pattern, count=100)
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break

        return True
    except redis.RedisError:
        return False


def invalidate_user_memberships_cache(user_id: UUID) -> bool:
    """
    Invalidate all deal membership cache entries for a user.

    Use when user role changes (affects all deal permissions).

    Args:
        user_id: User UUID

    Returns:
        True if invalidated successfully, False otherwise
    """
    try:
        client = get_cache_client()

        # Pattern delete all memberships for this user
        pattern = f"deal_member:*:{user_id}"
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor, match=pattern, count=100)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break

        return True
    except redis.RedisError:
        return False


# ========================================
# Cache Statistics (for monitoring)
# ========================================

def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics for monitoring.

    Returns:
        Dictionary with cache statistics
    """
    try:
        client = get_cache_client()
        info = client.info("stats")
        keyspace = client.info("keyspace")

        # Count keys by prefix
        user_keys = len(list(client.scan_iter("user:*", count=100)))
        deal_keys = len(list(client.scan_iter("deal:*", count=100)))
        membership_keys = len(list(client.scan_iter("deal_member:*", count=100)))

        return {
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "user_cache_size": user_keys,
            "deal_cache_size": deal_keys,
            "membership_cache_size": membership_keys,
            "connected_clients": client.info("clients").get("connected_clients", 0),
        }
    except redis.RedisError:
        return {"error": "Cache unavailable"}


def clear_all_cache() -> bool:
    """
    Clear all cache entries (for testing/maintenance).

    Returns:
        True if cleared successfully, False otherwise
    """
    try:
        client = get_cache_client()

        # Clear all app cache keys (not blacklist)
        patterns = ["user:*", "user_email:*", "deal:*", "deal_member:*"]

        for pattern in patterns:
            keys = list(client.scan_iter(match=pattern, count=100))
            if keys:
                client.delete(*keys)

        return True
    except redis.RedisError:
        return False
