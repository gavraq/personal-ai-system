"""
Agent execution schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from ..models.agent import AgentType, AgentStatus, MessageRole
from ..models.alert import AlertFrequency


class AgentRunStartRequest(BaseModel):
    """Request schema for starting an agent run"""
    query: Optional[str] = Field(default=None, description="The query or request for the agent")
    file_id: Optional[UUID] = Field(default=None, description="File ID for document analysis agent")
    context: Optional[dict] = Field(default=None, description="Additional context")


class AgentRunStartResponse(BaseModel):
    """Response schema after starting an agent run"""
    run_id: UUID
    status: AgentStatus
    message: str = "Agent run started"


class AgentMessageResponse(BaseModel):
    """Response schema for a single agent message"""
    id: UUID
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgentMessagesResponse(BaseModel):
    """Response schema for agent messages list"""
    messages: list[AgentMessageResponse]
    total: int


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


# Alert schemas for News & Alerts agent (feat-26)

class AlertCreateRequest(BaseModel):
    """Request schema for creating an alert"""
    name: str = Field(..., min_length=1, max_length=255, description="Alert name")
    keywords: list[str] = Field(default=[], description="Keywords to monitor")
    entities: list[str] = Field(default=[], description="Entities to track")
    frequency: AlertFrequency = Field(default=AlertFrequency.DAILY, description="Check frequency")
    deal_id: Optional[UUID] = Field(default=None, description="Optional deal to associate with")


class AlertUpdateRequest(BaseModel):
    """Request schema for updating an alert"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    keywords: Optional[list[str]] = None
    entities: Optional[list[str]] = None
    frequency: Optional[AlertFrequency] = None
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    """Response schema for a single alert"""
    id: UUID
    user_id: UUID
    deal_id: Optional[UUID] = None
    name: str
    keywords: list[str]
    entities: list[str]
    frequency: AlertFrequency
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_checked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Response schema for alert list"""
    alerts: list[AlertResponse]
    total: int


class AlertMatchResponse(BaseModel):
    """Response schema for an alert match"""
    id: UUID
    alert_id: UUID
    headline: str
    source: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    published_at: Optional[datetime] = None
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None
    keywords_matched: list[str]
    notified: bool
    matched_at: datetime

    class Config:
        from_attributes = True


class AlertMatchListResponse(BaseModel):
    """Response schema for alert matches list"""
    matches: list[AlertMatchResponse]
    total: int
