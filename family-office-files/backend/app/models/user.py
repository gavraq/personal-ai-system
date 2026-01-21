"""
User model for authentication and authorization
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    PARTNER = "partner"
    VIEWER = "viewer"


class User(Base):
    """User table for authentication"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.VIEWER,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deals_created = relationship("Deal", back_populates="creator", foreign_keys="Deal.created_by")
    deal_memberships = relationship("DealMember", back_populates="user")
    files_uploaded = relationship("File", back_populates="uploader")
    google_connection = relationship("GoogleConnection", back_populates="user", uselist=False)
    agent_runs = relationship("AgentRun", back_populates="user")
    audit_entries = relationship("AuditLog", back_populates="actor")
    activities = relationship("Activity", back_populates="actor")
    file_shares_received = relationship("FileShare", back_populates="shared_with_user")

    def __repr__(self):
        return f"<User {self.email}>"
