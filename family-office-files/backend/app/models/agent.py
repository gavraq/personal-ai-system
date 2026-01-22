"""
Agent execution models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base import Base


class AgentType(str, enum.Enum):
    """Agent type enumeration"""
    MARKET_RESEARCH = "market_research"
    DOCUMENT_ANALYSIS = "document_analysis"
    DUE_DILIGENCE = "due_diligence"
    NEWS_ALERTS = "news_alerts"


class AgentStatus(str, enum.Enum):
    """Agent run status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    """Chat message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AgentRun(Base):
    """Agent execution run table"""
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)  # ix_agent_runs_deal_id
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # ix_agent_runs_user_id
    agent_type = Column(
        Enum(AgentType, name="agent_type", create_constraint=True),
        nullable=False
    )
    input = Column(JSONB, nullable=False)
    output = Column(JSONB)
    status = Column(
        Enum(AgentStatus, name="agent_status", create_constraint=True),
        default=AgentStatus.PENDING,
        nullable=False,
        index=True  # ix_agent_runs_status
    )
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)

    # Relationships
    deal = relationship("Deal", back_populates="agent_runs")
    user = relationship("User", back_populates="agent_runs")
    messages = relationship("AgentMessage", back_populates="agent_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AgentRun {self.agent_type} status={self.status}>"


class AgentMessage(Base):
    """Agent chat messages table"""
    __tablename__ = "agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    role = Column(
        Enum(MessageRole, name="message_role", create_constraint=True),
        nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    agent_run = relationship("AgentRun", back_populates="messages")

    def __repr__(self):
        return f"<AgentMessage role={self.role}>"
