"""
Pydantic schemas for Google integration
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GoogleConnectionResponse(BaseModel):
    """Response model for Google connection status"""
    connected: bool
    email: Optional[str] = None
    connected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoogleAuthUrlResponse(BaseModel):
    """Response model containing OAuth authorization URL"""
    authorization_url: str


class GoogleDisconnectResponse(BaseModel):
    """Response model for disconnect operation"""
    message: str
    disconnected: bool = True
