"""
Agent execution schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from ..models.agent import AgentType, AgentStatus


class AgentRunResponse(BaseModel):
    """Response schema for a single agent run"""
    id: UUID
    deal_id: UUID
    user_id: UUID
    user_email: Optional[str] = None
    agent_type: AgentType
    status: AgentStatus
    input: dict
    output: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentRunListResponse(BaseModel):
    """Response schema for paginated agent run list"""
    runs: list[AgentRunResponse]
    total: int
    page: int
    page_size: int


class AgentRunCreate(BaseModel):
    """Request schema for creating an agent run"""
    deal_id: UUID
    agent_type: AgentType
    input: dict


class AgentSummary(BaseModel):
    """Summary schema for agent output cards on dashboard"""
    id: UUID
    deal_id: UUID
    deal_title: str
    agent_type: AgentType
    status: AgentStatus
    summary_excerpt: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class AgentSummaryListResponse(BaseModel):
    """Response schema for agent summaries per deal"""
    summaries: list[AgentSummary]
    total: int
