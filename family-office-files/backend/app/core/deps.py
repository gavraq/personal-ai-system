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
from ..models.user import User, UserRole

# HTTP Bearer token extraction
security = HTTPBearer()


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency factory to check if current user has one of the allowed roles.

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

        user = db.query(User).filter(User.id == user_id).first()
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

    user = db.query(User).filter(User.id == user_id).first()
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
