"""
JWT token creation and verification utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

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
    jti: str  # JWT token ID for blacklist tracking
    iat: datetime  # issued at timestamp


def create_access_token(user_id: UUID) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: The user's UUID

    Returns:
        Encoded JWT access token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        # jti (JWT ID): Unique identifier for this specific token.
        # Used for individual token blacklisting on logout - we can invalidate
        # this exact token without affecting user's other sessions.
        "jti": str(uuid4()),
        # iat (issued at): Timestamp when token was created.
        # Used for user-level blacklisting: when a user changes their password,
        # we store a blacklist timestamp and any token with iat < that timestamp
        # is considered invalid. This invalidates ALL existing tokens for security.
        "iat": now.timestamp()
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a JWT refresh token for a user.

    Refresh tokens have longer expiry (7 days) and are used to obtain new access
    tokens without re-authentication. They use the same jti/iat pattern for
    blacklisting support (see create_access_token comments for details).

    Args:
        user_id: The user's UUID

    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.refresh_token_expiry_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid4()),  # Individual token blacklist ID
        "iat": now.timestamp()  # For user-level blacklist comparison
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access", check_blacklist: bool = True) -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string
        token_type: Expected token type ("access" or "refresh")
        check_blacklist: Whether to check if token is blacklisted

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])

        # Verify token type matches expected
        if payload.get("type") != token_type:
            return None

        jti = payload.get("jti", "")
        iat = payload.get("iat", 0)

        # Two-level token blacklist check:
        # 1. Individual token blacklist (jti) - for single logout
        # 2. User-level blacklist (iat comparison) - for password change / forced logout all
        if check_blacklist and jti:
            from .token_blacklist import is_token_blacklisted, get_user_blacklist_timestamp

            # Level 1: Check if this specific token was blacklisted (e.g., on logout)
            if is_token_blacklisted(jti):
                return None

            # Level 2: Check user-level blacklist for "invalidate all tokens" scenarios
            # (password change, security breach, admin forced logout)
            # Any token issued BEFORE the user's blacklist timestamp is invalid.
            user_blacklist_time = get_user_blacklist_timestamp(payload["sub"])
            if user_blacklist_time:
                token_issued = datetime.fromtimestamp(iat) if iat else datetime.min
                if token_issued < user_blacklist_time:
                    return None

        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"]),
            type=payload["type"],
            jti=jti,
            iat=datetime.fromtimestamp(iat) if iat else datetime.utcnow()
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
