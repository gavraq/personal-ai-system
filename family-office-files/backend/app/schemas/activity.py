"""
Activity schemas for activity feed endpoints
"""
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ActivityType(str, Enum):
    """Activity type enumeration for API"""
    FILE_UPLOAD = "file_upload"
    FILE_LINK = "file_link"
    FILE_DELETE = "file_delete"
    DEAL_CREATE = "deal_create"
    DEAL_UPDATE = "deal_update"
    DEAL_DELETE = "deal_delete"
    MEMBER_ADD = "member_add"
    MEMBER_REMOVE = "member_remove"
    AGENT_RUN = "agent_run"


class ActivityResponse(BaseModel):
    """Schema for activity response"""
    id: UUID
    deal_id: UUID
    actor_id: UUID
    actor_email: Optional[str] = None
    action: str
    details: Optional[dict] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ActivityListResponse(BaseModel):
    """Schema for paginated activity list response"""
    activities: List[ActivityResponse]
    total: int
    page: int
    page_size: int


class ActivityCreate(BaseModel):
    """Schema for creating a new activity (internal use)"""
    deal_id: UUID
    actor_id: UUID
    action: str = Field(..., description="Activity type")
    details: Optional[dict] = Field(None, description="Additional context")
