"""
Files router for document management operations
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.file import File, FileSource
from ..schemas.file import (
    LinkDriveFileRequest,
    LinkDriveFileResponse,
    FileResponse,
    FileListResponse,
)

router = APIRouter(prefix="/api/deals", tags=["files"])


def is_deal_member(db: Session, deal_id: UUID, user_id: UUID) -> bool:
    """Check if user is a member of the deal"""
    return db.query(DealMember).filter(
        DealMember.deal_id == deal_id,
        DealMember.user_id == user_id
    ).first() is not None


def can_access_deal(db: Session, deal: Deal, user: User) -> bool:
    """Check if user can access the deal (admin or member)"""
    if user.role == UserRole.ADMIN.value:
        return True
    return is_deal_member(db, deal.id, user.id)


def get_deal_role(db: Session, deal: Deal, user: User) -> str:
    """Get user's effective role for a deal"""
    if user.role == UserRole.ADMIN.value:
        return UserRole.ADMIN.value

    membership = db.query(DealMember).filter(
        DealMember.deal_id == deal.id,
        DealMember.user_id == user.id
    ).first()

    if membership and membership.role_override:
        return membership.role_override

    return user.role


def can_upload_files(db: Session, deal: Deal, user: User) -> bool:
    """Check if user can upload/link files (partner or admin)"""
    role = get_deal_role(db, deal, user)
    return role in [UserRole.ADMIN.value, UserRole.PARTNER.value]


@router.post("/{deal_id}/files/link", response_model=LinkDriveFileResponse, status_code=status.HTTP_201_CREATED)
async def link_drive_file(
    deal_id: UUID,
    request: LinkDriveFileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link a Google Drive file to a deal.

    - **drive_file_id**: Google Drive file ID (required)
    - **name**: Display name for the file (required)
    - **mime_type**: MIME type of the file (optional)
    - **size_bytes**: Size in bytes (optional)

    User must be a deal member with partner or admin role.
    """
    # Get the deal
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check access
    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Check permission to upload/link files
    if not can_upload_files(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only partners and admins can link files"
        )

    # Check if deal is closed
    if deal.status == 'closed':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add files to a closed deal"
        )

    # Check if file is already linked to this deal
    existing = db.query(File).filter(
        File.deal_id == deal_id,
        File.source == FileSource.DRIVE,
        File.source_id == request.drive_file_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file is already linked to the deal"
        )

    # Create the file record
    file = File(
        deal_id=deal_id,
        name=request.name,
        source=FileSource.DRIVE,
        source_id=request.drive_file_id,
        mime_type=request.mime_type,
        size_bytes=request.size_bytes,
        uploaded_by=current_user.id
    )

    db.add(file)
    db.commit()
    db.refresh(file)

    return LinkDriveFileResponse(
        id=file.id,
        name=file.name,
        mime_type=file.mime_type,
        size_bytes=file.size_bytes,
        source="drive",
        source_id=file.source_id
    )


@router.get("/{deal_id}/files", response_model=FileListResponse)
async def list_deal_files(
    deal_id: UUID,
    source: Optional[str] = Query(None, description="Filter by source (drive or gcs)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all files associated with a deal.

    Optionally filter by source type (drive or gcs).
    User must be a deal member or admin.
    """
    # Get the deal
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check access
    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Build query
    query = db.query(File).filter(File.deal_id == deal_id)

    if source:
        if source == "drive":
            query = query.filter(File.source == FileSource.DRIVE)
        elif source == "gcs":
            query = query.filter(File.source == FileSource.GCS)

    files = query.order_by(File.created_at.desc()).all()

    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=len(files)
    )
