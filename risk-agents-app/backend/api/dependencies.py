"""
FastAPI Dependencies for Authentication and Authorization
Provides dependency injection for route protection
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional
import logging

from api.auth import verify_token, verify_api_key, get_user, TokenData, User
from api.exceptions import AuthenticationError, InvalidTokenError, PermissionDeniedError

logger = logging.getLogger("risk-agents-api")

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Authentication Dependencies

async def get_current_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> TokenData:
    """
    Extract and validate JWT token from Authorization header

    Args:
        credentials: Bearer token credentials

    Returns:
        TokenData: Validated token data

    Raises:
        AuthenticationError: If no credentials provided
        InvalidTokenError: If token is invalid or expired
    """
    if credentials is None:
        raise AuthenticationError("No authentication credentials provided")

    token = credentials.credentials

    # Verify token
    token_data = verify_token(token, token_type="access")

    if token_data is None:
        raise InvalidTokenError("Invalid or expired token")

    logger.info(f"Authenticated user: {token_data.user_id}")

    return token_data


async def get_current_user(
    token_data: TokenData = Depends(get_current_token)
) -> User:
    """
    Get current user from token data

    Args:
        token_data: Validated token data

    Returns:
        User: Current user object

    Raises:
        AuthenticationError: If user not found or disabled
    """
    user = get_user(token_data.user_id)

    if user is None:
        raise AuthenticationError("User not found")

    if user.disabled:
        raise AuthenticationError("User account is disabled")

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    Useful for endpoints that work with or without authentication

    Args:
        credentials: Bearer token credentials

    Returns:
        User: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token_data = await get_current_token(credentials)
        user = await get_current_user(token_data)
        return user
    except (AuthenticationError, InvalidTokenError):
        return None


# API Key Authentication

async def verify_api_key_header(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Verify API key from X-API-Key header

    Args:
        api_key: API key from header

    Returns:
        str: Validated API key

    Raises:
        AuthenticationError: If no API key provided
        InvalidTokenError: If API key is invalid
    """
    if api_key is None:
        raise AuthenticationError("No API key provided")

    if not verify_api_key(api_key):
        raise InvalidTokenError("Invalid API key")

    logger.info(f"Authenticated via API key: {api_key[:8]}...")

    return api_key


# Combined Authentication (JWT or API Key)

async def get_authenticated_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header)
) -> User:
    """
    Authenticate user via JWT token OR API key

    Args:
        credentials: Bearer token credentials
        api_key: API key from header

    Returns:
        User: Authenticated user

    Raises:
        AuthenticationError: If no authentication method provided
        InvalidTokenError: If authentication fails
    """
    # Try JWT first
    if credentials is not None:
        try:
            token_data = await get_current_token(credentials)
            user = await get_current_user(token_data)
            return user
        except (AuthenticationError, InvalidTokenError):
            pass

    # Try API key
    if api_key is not None:
        try:
            await verify_api_key_header(api_key)
            # For API key auth, return a system user
            # In production, API keys would be associated with specific users
            return User(
                user_id="api-key-user",
                email="api@example.com",
                full_name="API Key User",
                disabled=False
            )
        except (AuthenticationError, InvalidTokenError):
            pass

    # No valid authentication
    raise AuthenticationError("Authentication required (JWT token or API key)")


# Permission/Scope Dependencies

def require_scope(required_scope: str):
    """
    Dependency factory that requires specific scope

    Args:
        required_scope: Required permission scope

    Returns:
        Dependency function that checks for scope

    Example:
        @router.post("/admin", dependencies=[Depends(require_scope("admin"))])
    """

    async def check_scope(token_data: TokenData = Depends(get_current_token)):
        if required_scope not in token_data.scopes:
            raise PermissionDeniedError(
                f"Insufficient permissions. Required scope: {required_scope}"
            )
        return token_data

    return check_scope


def require_scopes(required_scopes: list[str], require_all: bool = True):
    """
    Dependency factory that requires multiple scopes

    Args:
        required_scopes: List of required permission scopes
        require_all: If True, all scopes required. If False, any scope sufficient.

    Returns:
        Dependency function that checks for scopes

    Example:
        @router.post("/data", dependencies=[Depends(require_scopes(["read", "write"]))])
    """

    async def check_scopes(token_data: TokenData = Depends(get_current_token)):
        user_scopes = set(token_data.scopes)
        required = set(required_scopes)

        if require_all:
            # All scopes required
            if not required.issubset(user_scopes):
                missing = required - user_scopes
                raise PermissionDeniedError(
                    f"Insufficient permissions. Missing scopes: {', '.join(missing)}"
                )
        else:
            # Any scope sufficient
            if not required.intersection(user_scopes):
                raise PermissionDeniedError(
                    f"Insufficient permissions. Required one of: {', '.join(required)}"
                )

        return token_data

    return check_scopes


# Admin-only dependency

async def require_admin(token_data: TokenData = Depends(get_current_token)):
    """
    Require admin scope

    Raises:
        PermissionDeniedError: If user doesn't have admin scope
    """
    if "admin" not in token_data.scopes:
        raise PermissionDeniedError("Admin access required")
    return token_data


# Development-only bypass (for testing without authentication)

async def optional_auth_for_dev(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[User]:
    """
    Optional authentication for development
    In development mode, allows unauthenticated access
    In production, requires authentication

    Args:
        credentials: Bearer token credentials

    Returns:
        User: Authenticated user or dev user
    """
    import os

    # In production, require auth
    if os.getenv("ENVIRONMENT") == "production":
        token_data = await get_current_token(credentials)
        return await get_current_user(token_data)

    # In development, allow without auth
    if credentials is None:
        logger.warning("Development mode: Allowing unauthenticated access")
        return User(
            user_id="dev-user",
            email="dev@example.com",
            full_name="Development User",
            disabled=False
        )

    # If credentials provided, validate them
    try:
        token_data = await get_current_token(credentials)
        return await get_current_user(token_data)
    except (AuthenticationError, InvalidTokenError):
        # In dev, fall back to dev user
        logger.warning("Development mode: Invalid token, using dev user")
        return User(
            user_id="dev-user",
            email="dev@example.com",
            full_name="Development User",
            disabled=False
        )
