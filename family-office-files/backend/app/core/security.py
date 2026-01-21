"""
JWT token creation and verification utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel

from .config import get_settings

settings = get_settings()

# JWT algorithm
ALGORITHM = "HS256"


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: str  # user id
    exp: datetime
    type: str  # "access" or "refresh"


def create_access_token(user_id: UUID) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: The user's UUID

    Returns:
        Encoded JWT access token string
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a JWT refresh token for a user.

    Args:
        user_id: The user's UUID

    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expiry_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])

        # Verify token type matches expected
        if payload.get("type") != token_type:
            return None

        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"]),
            type=payload["type"]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def decode_token_unverified(token: str) -> Optional[dict]:
    """
    Decode a token without verification (for debugging/logging).

    Args:
        token: The JWT token string

    Returns:
        Decoded payload dict or None
    """
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM], options={"verify_exp": False})
    except JWTError:
        return None
