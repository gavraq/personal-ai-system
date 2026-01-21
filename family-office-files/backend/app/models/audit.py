"""
Audit and activity tracking models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class AuditLog(Base):
    """Audit log for tracking permission and data changes"""
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "role_change", "deal_create"
    entity_type = Column(String(50), nullable=False)  # e.g., "user", "deal", "file"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    actor = relationship("User", back_populates="audit_entries")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}>"


class Activity(Base):
    """Activity feed for deals"""
    __tablename__ = "activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "file_upload", "agent_run"
    details = Column(JSONB)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    deal = relationship("Deal", back_populates="activities")
    actor = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity {self.action} on deal={self.deal_id}>"
