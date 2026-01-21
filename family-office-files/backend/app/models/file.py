"""
File models for document storage
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import Base


class FileSource(str, enum.Enum):
    """File source enumeration"""
    DRIVE = "drive"
    GCS = "gcs"


class FilePermission(str, enum.Enum):
    """File permission enumeration"""
    VIEW = "view"
    EDIT = "edit"


class File(Base):
    """File metadata table"""
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    source = Column(
        Enum(FileSource, name="file_source", values_callable=lambda x: [e.value for e in x], create_constraint=False),
        nullable=False
    )
    source_id = Column(String(500))  # Drive file ID or GCS path
    mime_type = Column(String(100))
    size_bytes = Column(BigInteger)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    deal = relationship("Deal", back_populates="files")
    uploader = relationship("User", back_populates="files_uploaded")
    shares = relationship("FileShare", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<File {self.name}>"


class FileShare(Base):
    """File sharing permissions table"""
    __tablename__ = "file_shares"

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), primary_key=True)
    shared_with = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    permission = Column(
        Enum(FilePermission, name="file_permission", values_callable=lambda x: [e.value for e in x], create_constraint=False),
        default=FilePermission.VIEW,
        nullable=False
    )
    shared_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    file = relationship("File", back_populates="shares")
    shared_with_user = relationship("User", back_populates="file_shares_received")

    def __repr__(self):
        return f"<FileShare file={self.file_id} user={self.shared_with}>"
