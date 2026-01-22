"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .security import verify_token
from .cache import get_cached_user, cache_user
from ..models.user import User, UserRole

# HTTP Bearer token extraction
security = HTTPBearer()


def _get_user_with_cache(db: Session, user_id: UUID) -> Optional[User]:
    """
    Get user by ID with Redis cache.

    First checks cache, falls back to database if not cached.
    Caches the result on database hit.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User object or None if not found
    """
    # Try cache first for quick existence check
    cached = get_cached_user(user_id)
    if cached:
        # IMPORTANT: Even on cache hit, we fetch from DB. This is NOT redundant.
        # The cache stores user data as a dict, not an SQLAlchemy ORM object.
        # We need the actual ORM object attached to the DB session for:
        # 1. Lazy loading of relationships (e.g., user.deals)
        # 2. Session identity map consistency (SQLAlchemy tracks objects)
        # 3. Future DB operations that require a managed entity
        # The cache validates the user exists before this (now guaranteed) DB hit.
        user = db.query(User).filter(User.id == user_id).first()
        return user

    # Cache miss - fetch from database
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        # Cache the user data
        cache_user(user_id, {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        })

    return user


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to check if current user has one of the allowed roles.

    This uses the factory pattern: returns a closure (role_checker) that captures
    the allowed_roles list. Each call to require_role([...]) creates a new closure
    with its own allowed_roles, enabling flexible per-endpoint role requirements.

    Args:
        allowed_roles: List of UserRole values that are allowed

    Returns:
        A dependency function that validates the user's role

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role([UserRole.ADMIN]))])
        async def admin_endpoint(...):
            ...

    Or as a direct dependency:
        async def endpoint(current_user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    # Factory pattern: role_checker closes over allowed_roles
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Inner dependency that checks role after authentication"""
        # First authenticate the user
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = credentials.credentials
        token_payload = verify_token(token, token_type="access")

        if token_payload is None:
            raise credentials_exception

        try:
            user_id = UUID(token_payload.sub)
        except ValueError:
            raise credentials_exception

        user = _get_user_with_cache(db, user_id)
        if user is None:
            raise credentials_exception

        # Check role authorization
        if user.role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Required role: " + ", ".join([r.value for r in allowed_roles])
            )

        return user

    return role_checker


# Convenience dependency for admin-only endpoints
require_admin = require_role([UserRole.ADMIN])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: Bearer token credentials from request header
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    token_payload = verify_token(token, token_type="access")

    if token_payload is None:
        raise credentials_exception

    try:
        user_id = UUID(token_payload.sub)
    except ValueError:
        raise credentials_exception

    user = _get_user_with_cache(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional dependency to get current user if authenticated.

    Returns None if no token provided, raises 401 if token is invalid.
    """
    if credentials is None:
        return None

    return await get_current_user(credentials, db)
