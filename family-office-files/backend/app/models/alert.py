"""
Alert configuration models for News & Alerts agent
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum

from .base import Base


class AlertFrequency(str, enum.Enum):
    """Alert check frequency enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    IMMEDIATE = "immediate"


class Alert(Base):
    """Alert configuration table for news monitoring"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=True)

    # Alert configuration
    name = Column(String(255), nullable=False)
    keywords = Column(ARRAY(String), nullable=False, default=[])
    entities = Column(ARRAY(String), nullable=False, default=[])
    frequency = Column(
        Enum(AlertFrequency, name="alert_frequency", create_constraint=True),
        default=AlertFrequency.DAILY,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_checked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="alerts")
    deal = relationship("Deal", back_populates="alerts")
    matches = relationship("AlertMatch", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Alert {self.name} frequency={self.frequency}>"


class AlertMatch(Base):
    """Alert match records for storing news that matched alert criteria"""
    __tablename__ = "alert_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)

    # Match details
    headline = Column(String(500), nullable=False)
    source = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    relevance_score = Column(UUID, nullable=True)  # Store as float compatible type
    keywords_matched = Column(ARRAY(String), nullable=False, default=[])

    # Notification status
    notified = Column(Boolean, default=False, nullable=False)
    notified_at = Column(DateTime, nullable=True)

    # Timestamps
    matched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    alert = relationship("Alert", back_populates="matches")

    def __repr__(self):
        return f"<AlertMatch headline='{self.headline[:30]}...'>"
