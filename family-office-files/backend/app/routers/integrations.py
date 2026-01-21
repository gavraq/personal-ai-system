"""
Google integration router for OAuth and Drive access
"""
from datetime import datetime, timedelta
from typing import Optional
import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import get_settings
from ..core.deps import get_current_user
from ..models.user import User
from ..models.google import GoogleConnection
from ..schemas.google import (
    GoogleConnectionResponse,
    GoogleAuthUrlResponse,
    GoogleDisconnectResponse,
)

router = APIRouter(prefix="/api/integrations/google", tags=["integrations"])

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Required scopes for Google Drive access
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
]


def build_auth_url(redirect_uri: str, client_id: str, state: str) -> str:
    """Build Google OAuth authorization URL"""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query_string}"


async def exchange_code_for_tokens(
    code: str, redirect_uri: str, client_id: str, client_secret: str
) -> dict:
    """Exchange authorization code for access and refresh tokens"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for tokens: {response.text}",
            )
        return response.json()


async def refresh_access_token(
    refresh_token: str, client_id: str, client_secret: str
) -> dict:
    """Refresh an expired access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to refresh access token",
            )
        return response.json()


async def get_google_user_email(access_token: str) -> str:
    """Get the Google user's email address"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )
        data = response.json()
        return data.get("email", "")


@router.get("/status", response_model=GoogleConnectionResponse)
async def get_connection_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current user's Google Drive connection status.

    Returns whether the user has connected their Google account
    and the email associated with the connection.
    """
    connection = (
        db.query(GoogleConnection)
        .filter(GoogleConnection.user_id == current_user.id)
        .first()
    )

    if connection is None:
        return GoogleConnectionResponse(connected=False)

    # Check if we need to refresh the token
    settings = get_settings()
    if connection.token_expiry and connection.token_expiry < datetime.utcnow():
        try:
            tokens = await refresh_access_token(
                connection.refresh_token,
                settings.google_client_id,
                settings.google_client_secret,
            )
            connection.access_token = tokens["access_token"]
            connection.token_expiry = datetime.utcnow() + timedelta(
                seconds=tokens.get("expires_in", 3600)
            )
            db.commit()
        except HTTPException:
            # Token refresh failed, connection is stale
            return GoogleConnectionResponse(
                connected=False,
                email=None,
                connected_at=connection.created_at,
            )

    # Get email from Google
    try:
        email = await get_google_user_email(connection.access_token)
    except HTTPException:
        email = None

    return GoogleConnectionResponse(
        connected=True,
        email=email,
        connected_at=connection.created_at,
    )


@router.get("/auth", response_model=GoogleAuthUrlResponse)
async def initiate_oauth(
    current_user: User = Depends(get_current_user),
):
    """
    Initiate Google OAuth flow.

    Returns the authorization URL that the frontend should redirect the user to.
    The state parameter contains the user ID for verification during callback.
    """
    settings = get_settings()

    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured",
        )

    # Use user ID as state for verification
    state = str(current_user.id)

    auth_url = build_auth_url(
        redirect_uri=settings.google_redirect_uri,
        client_id=settings.google_client_id,
        state=state,
    )

    return GoogleAuthUrlResponse(authorization_url=auth_url)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter (user ID)"),
    db: Session = Depends(get_db),
):
    """
    Handle Google OAuth callback.

    This endpoint is called by Google after the user authorizes the application.
    It exchanges the authorization code for tokens and stores them.

    Note: This endpoint does not require authentication since it's called
    by Google's redirect. The state parameter contains the user ID.
    """
    settings = get_settings()

    # Verify user exists
    from uuid import UUID
    try:
        user_id = UUID(state)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user in state",
        )

    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(
        code=code,
        redirect_uri=settings.google_redirect_uri,
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in", 3600)

    if not access_token or not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get tokens from Google",
        )

    # Calculate token expiry
    token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

    # Check if connection already exists
    existing = (
        db.query(GoogleConnection)
        .filter(GoogleConnection.user_id == user_id)
        .first()
    )

    if existing:
        # Update existing connection
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.token_expiry = token_expiry
        existing.updated_at = datetime.utcnow()
    else:
        # Create new connection
        connection = GoogleConnection(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry,
        )
        db.add(connection)

    db.commit()

    # Redirect to frontend success page
    return RedirectResponse(
        url="http://localhost:3000/settings?google=connected",
        status_code=status.HTTP_302_FOUND,
    )


@router.delete("", response_model=GoogleDisconnectResponse)
async def disconnect_google(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Disconnect Google Drive from the user's account.

    This removes the stored OAuth tokens. The user will need to
    re-authorize to connect again.
    """
    connection = (
        db.query(GoogleConnection)
        .filter(GoogleConnection.user_id == current_user.id)
        .first()
    )

    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Google connection found",
        )

    # Optionally revoke the token with Google
    settings = get_settings()
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://oauth2.googleapis.com/revoke?token={connection.access_token}"
            )
    except Exception:
        # Revocation failed but we'll still delete locally
        pass

    db.delete(connection)
    db.commit()

    return GoogleDisconnectResponse(
        message="Google Drive disconnected successfully",
        disconnected=True,
    )


async def get_valid_access_token(user_id, db: Session) -> Optional[str]:
    """
    Get a valid access token for a user, refreshing if necessary.

    This is a utility function for other parts of the application
    that need to make Google API calls.
    """
    from uuid import UUID

    connection = (
        db.query(GoogleConnection)
        .filter(GoogleConnection.user_id == user_id)
        .first()
    )

    if connection is None:
        return None

    settings = get_settings()

    # Check if token needs refresh
    if connection.token_expiry and connection.token_expiry < datetime.utcnow():
        try:
            tokens = await refresh_access_token(
                connection.refresh_token,
                settings.google_client_id,
                settings.google_client_secret,
            )
            connection.access_token = tokens["access_token"]
            connection.token_expiry = datetime.utcnow() + timedelta(
                seconds=tokens.get("expires_in", 3600)
            )
            db.commit()
        except HTTPException:
            return None

    return connection.access_token
