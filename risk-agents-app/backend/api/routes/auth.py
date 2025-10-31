"""
Authentication Routes
Provides endpoints for login, token refresh, and validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

from api.auth import (
    authenticate_user,
    generate_tokens,
    verify_token,
    generate_api_key,
    Token,
    User
)
from api.dependencies import get_current_token, get_current_user
from api.exceptions import AuthenticationError, InvalidTokenError
from api.rate_limit import auth_limiter, check_rate_limit
from fastapi import Request

logger = logging.getLogger("risk-agents-api")

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models

class LoginRequest(BaseModel):
    """Login request"""
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "password": "testpassword"
            }
        }


class RefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ValidateResponse(BaseModel):
    """Token validation response"""
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user_id": "test-user-1",
                "email": "test@example.com",
                "scopes": ["read", "write"]
            }
        }


class ApiKeyResponse(BaseModel):
    """API key generation response"""
    api_key: str
    note: str

    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "sk_1a2b3c4d5e6f7g8h9i0j",
                "note": "Store this key securely. It will not be shown again."
            }
        }


# Endpoints

@router.post("/token", response_model=Token)
async def login(request: Request, credentials: LoginRequest):
    """
    Login with email and password to get JWT tokens

    Returns access token and refresh token.
    Access token expires in 1 hour, refresh token in 7 days.

    Args:
        credentials: Email and password

    Returns:
        Token: Access and refresh tokens

    Raises:
        HTTPException: 401 if authentication fails
        HTTPException: 429 if rate limit exceeded
    """
    # Check rate limit (10 requests per minute for auth endpoints)
    check_rate_limit(request, auth_limiter)

    # Authenticate user
    user = authenticate_user(credentials.email, credentials.password)

    if not user:
        logger.warning(f"Failed login attempt for {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    tokens = generate_tokens(
        user_id=user.user_id,
        email=user.email,
        scopes=["read", "write"]  # Default scopes
    )

    logger.info(f"User logged in: {user.email}")

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, refresh_request: RefreshRequest):
    """
    Refresh access token using refresh token

    Args:
        refresh_request: Refresh token

    Returns:
        Token: New access and refresh tokens

    Raises:
        HTTPException: 401 if refresh token is invalid
        HTTPException: 429 if rate limit exceeded
    """
    # Check rate limit
    check_rate_limit(request, auth_limiter)

    # Verify refresh token
    token_data = verify_token(refresh_request.refresh_token, token_type="refresh")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Generate new tokens
    tokens = generate_tokens(
        user_id=token_data.user_id,
        email=token_data.email or "",
        scopes=token_data.scopes
    )

    logger.info(f"Token refreshed for user: {token_data.user_id}")

    return tokens


@router.post("/validate", response_model=ValidateResponse)
async def validate_token_endpoint(request: Request):
    """
    Validate current access token

    Requires authentication via Bearer token.

    Returns:
        ValidateResponse: Token validation status and user info

    Raises:
        HTTPException: 401 if token is invalid
    """
    try:
        # This dependency will raise exception if token invalid
        token_data = await get_current_token()

        return ValidateResponse(
            valid=True,
            user_id=token_data.user_id,
            email=token_data.email,
            scopes=token_data.scopes
        )

    except (AuthenticationError, InvalidTokenError) as e:
        return ValidateResponse(valid=False)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Requires authentication via Bearer token.

    Returns:
        User: Current user information

    Raises:
        HTTPException: 401 if not authenticated
    """
    return current_user


@router.post("/api-key", response_model=ApiKeyResponse)
async def generate_api_key_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Generate new API key for current user

    Requires authentication via Bearer token.
    API keys can be used instead of JWT tokens for authentication.

    Returns:
        ApiKeyResponse: New API key

    Raises:
        HTTPException: 401 if not authenticated

    Note:
        In production, API keys should be stored in database
        associated with the user account.
    """
    api_key = generate_api_key()

    logger.info(f"API key generated for user: {current_user.email}")

    return ApiKeyResponse(
        api_key=api_key,
        note="Store this key securely. It will not be shown again. "
             "Add to API_KEYS environment variable to enable."
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user

    Note: JWT tokens are stateless, so logout is client-side only.
    Client should delete the token. Token will expire naturally.

    In production, consider implementing token blacklist for immediate revocation.

    Returns:
        dict: Success message
    """
    logger.info(f"User logged out: {current_user.email}")

    return {
        "message": "Successfully logged out",
        "note": "Delete your access token and refresh token on the client side"
    }


# Health check for auth service
@router.get("/health")
async def auth_health():
    """
    Check authentication service health

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "features": [
            "JWT token generation",
            "Token refresh",
            "Token validation",
            "API key generation",
            "Rate limiting"
        ]
    }
