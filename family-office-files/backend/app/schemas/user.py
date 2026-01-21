"""
User schemas for user management endpoints
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class UserRoleEnum(str, Enum):
    """User role enumeration for API"""
    ADMIN = "admin"
    PARTNER = "partner"
    VIEWER = "viewer"


class RoleUpdateRequest(BaseModel):
    """Schema for updating a user's role"""
    role: UserRoleEnum = Field(..., description="New role to assign to the user")


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive fields)"""
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
