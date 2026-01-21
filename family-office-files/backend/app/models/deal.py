"""
Deal/Transaction models for project organization
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class DealStatus(str, enum.Enum):
    """Deal status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class Deal(Base):
    """Deal/Transaction table"""
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        Enum(DealStatus, name="deal_status", create_constraint=True),
        default=DealStatus.DRAFT,
        nullable=False
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="deals_created", foreign_keys=[created_by])
    members = relationship("DealMember", back_populates="deal", cascade="all, delete-orphan")
    files = relationship("File", back_populates="deal", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="deal", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="deal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Deal {self.title}>"


class DealMember(Base):
    """Deal membership junction table"""
    __tablename__ = "deal_members"

    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_override = Column(String(20))  # NULL means use user's global role
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    deal = relationship("Deal", back_populates="members")
    user = relationship("User", back_populates="deal_memberships")

    def __repr__(self):
        return f"<DealMember deal={self.deal_id} user={self.user_id}>"
