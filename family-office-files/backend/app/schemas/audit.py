"""
Audit log schemas for audit endpoints
"""
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class AuditActionType(str, Enum):
    """Audit action type enumeration for API"""
    ROLE_CHANGE = "role_change"
    USER_CREATE = "user_create"
    DEAL_CREATE = "deal_create"
    DEAL_UPDATE = "deal_update"
    DEAL_DELETE = "deal_delete"
    MEMBER_ADD = "member_add"
    MEMBER_REMOVE = "member_remove"
    MEMBER_ROLE_OVERRIDE = "member_role_override"
    FILE_UPLOAD = "file_upload"
    FILE_DELETE = "file_delete"
    FILE_SHARE = "file_share"
    FILE_UNSHARE = "file_unshare"
    PERMISSION_CHANGE = "permission_change"


class EntityTypeEnum(str, Enum):
    """Entity type enumeration for API"""
    USER = "user"
    DEAL = "deal"
    DEAL_MEMBER = "deal_member"
    FILE = "file"
    FILE_SHARE = "file_share"


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: UUID
    actor_id: UUID
    actor_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: UUID
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list response"""
    entries: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogFilter(BaseModel):
    """Schema for filtering audit log entries"""
    action: Optional[str] = Field(None, description="Filter by action type")
    actor_id: Optional[UUID] = Field(None, description="Filter by actor UUID")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[UUID] = Field(None, description="Filter by entity UUID")
    from_date: Optional[datetime] = Field(None, description="Filter entries from this date")
    to_date: Optional[datetime] = Field(None, description="Filter entries until this date")
