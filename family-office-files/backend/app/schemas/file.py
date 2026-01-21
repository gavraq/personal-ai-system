"""
Pydantic schemas for file operations
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class FileSourceEnum(str, Enum):
    """File source type"""
    DRIVE = "drive"
    GCS = "gcs"


class LinkDriveFileRequest(BaseModel):
    """Request to link a Google Drive file to a deal"""
    drive_file_id: str = Field(..., description="Google Drive file ID")
    name: str = Field(..., description="File name", max_length=255)
    mime_type: Optional[str] = Field(None, description="MIME type of the file", max_length=100)
    size_bytes: Optional[int] = Field(None, description="File size in bytes", ge=0)


class FileResponse(BaseModel):
    """Response model for file metadata"""
    id: UUID
    deal_id: UUID
    name: str
    source: FileSourceEnum
    source_id: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response model for list of files"""
    files: List[FileResponse]
    total: int


class LinkDriveFileResponse(BaseModel):
    """Response model for linking a Drive file"""
    id: UUID
    name: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    source: str = "drive"
    source_id: str

    class Config:
        from_attributes = True


class UploadFileResponse(BaseModel):
    """Response model for uploading a file to GCS"""
    id: UUID
    name: str
    mime_type: Optional[str] = None
    size_bytes: int
    source: str = "gcs"
    source_id: str

    class Config:
        from_attributes = True


class FileDownloadResponse(BaseModel):
    """Response model for file download URL"""
    id: UUID
    name: str
    download_url: str
    expires_in_minutes: int = 60


class FilePermissionEnum(str, Enum):
    """File permission type"""
    VIEW = "view"
    EDIT = "edit"


class ShareFileRequest(BaseModel):
    """Request to share a file with another user"""
    user_id: UUID = Field(..., description="ID of the user to share with")
    permission: FilePermissionEnum = Field(
        default=FilePermissionEnum.VIEW,
        description="Permission level to grant (view or edit)"
    )


class FileShareResponse(BaseModel):
    """Response model for a file share"""
    file_id: UUID
    shared_with: UUID
    permission: FilePermissionEnum
    shared_at: datetime

    class Config:
        from_attributes = True


class ShareFileResponse(BaseModel):
    """Response model for sharing a file"""
    message: str
    share: FileShareResponse
