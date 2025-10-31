"""
Authentication Module for Risk Agents API
Provides JWT token generation, validation, and API key authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# Password hashing
# Note: Using argon2 as primary, bcrypt as fallback
# Argon2 is more modern and doesn't have the 72-byte password limit
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=512,
    argon2__parallelism=2
)


# Pydantic Models

class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []


class User(BaseModel):
    """User model"""
    user_id: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


# Token Functions

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token (user_id, email, scopes)
        expires_delta: Token expiration time (default: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token

    Args:
        data: Data to encode in token (user_id)

    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        dict: Token payload if valid, None if invalid

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify JWT token and extract data

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenData: Token data if valid, None if invalid
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # Check token type
    if payload.get("type") != token_type:
        return None

    # Extract data
    user_id: str = payload.get("sub")
    email: str = payload.get("email")
    scopes: list = payload.get("scopes", [])

    if user_id is None:
        return None

    return TokenData(user_id=user_id, email=email, scopes=scopes)


def generate_tokens(user_id: str, email: str, scopes: list[str] = None) -> Token:
    """
    Generate access and refresh tokens for a user

    Args:
        user_id: User ID
        email: User email
        scopes: List of permission scopes

    Returns:
        Token: Token response with access and refresh tokens
    """
    if scopes is None:
        scopes = ["read", "write"]

    # Create access token
    access_token_data = {
        "sub": user_id,
        "email": email,
        "scopes": scopes
    }
    access_token = create_access_token(access_token_data)

    # Create refresh token
    refresh_token_data = {"sub": user_id}
    refresh_token = create_refresh_token(refresh_token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    )


# API Key Functions

def generate_api_key() -> str:
    """
    Generate secure API key

    Returns:
        str: Random API key (32 characters)
    """
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key against stored keys

    Args:
        api_key: API key to verify

    Returns:
        bool: True if valid, False otherwise

    Note:
        In production, this should check against a database
        For now, we check against environment variable
    """
    valid_api_keys = os.getenv("API_KEYS", "").split(",")
    return api_key in valid_api_keys


# Password Functions (for future user management)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


# Mock User Database (for development)
# In production, replace with actual database

MOCK_USERS_DB = {
    "test-user-1": {
        "user_id": "test-user-1",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": get_password_hash("testpassword"),
        "disabled": False
    }
}


def get_user(user_id: str) -> Optional[User]:
    """
    Get user from database

    Args:
        user_id: User ID

    Returns:
        User: User object if found, None otherwise
    """
    user_dict = MOCK_USERS_DB.get(user_id)

    if user_dict:
        return User(**user_dict)

    return None


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password

    Args:
        email: User email
        password: Plain text password

    Returns:
        User: User object if authenticated, None otherwise
    """
    # Find user by email (mock implementation)
    user_dict = None
    for uid, udata in MOCK_USERS_DB.items():
        if udata["email"] == email:
            user_dict = udata
            break

    if not user_dict:
        return None

    if not verify_password(password, user_dict["hashed_password"]):
        return None

    return User(**user_dict)
