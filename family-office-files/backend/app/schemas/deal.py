"""
Deal schemas for deal management endpoints
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class DealStatusEnum(str, Enum):
    """Deal status enumeration for API"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class DealCreate(BaseModel):
    """Schema for creating a new deal"""
    title: str = Field(..., min_length=1, max_length=255, description="Deal title")
    description: Optional[str] = Field(None, description="Deal description")


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Deal title")
    description: Optional[str] = Field(None, description="Deal description")
    status: Optional[DealStatusEnum] = Field(None, description="Deal status")


class DealResponse(BaseModel):
    """Schema for deal response"""
    id: UUID
    title: str
    description: Optional[str]
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    file_count: int = 0

    model_config = {
        "from_attributes": True
    }


class DealListResponse(BaseModel):
    """Schema for paginated deal list response"""
    deals: List[DealResponse]
    total: int
    page: int
    page_size: int


class DealMemberCreate(BaseModel):
    """Schema for adding a member to a deal"""
    user_id: UUID = Field(..., description="User ID to add as member")
    role_override: Optional[str] = Field(
        None,
        description="Optional role override for this deal (admin, partner, viewer)"
    )


class DealMemberResponse(BaseModel):
    """Schema for deal member response"""
    deal_id: UUID
    user_id: UUID
    role_override: Optional[str]
    added_at: datetime
    user_email: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class DealMemberListResponse(BaseModel):
    """Schema for paginated deal member list response"""
    members: List[DealMemberResponse]
    total: int
    page: int
    page_size: int
