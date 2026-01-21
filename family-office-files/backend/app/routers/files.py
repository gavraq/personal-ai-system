"""
Files router for document management operations
"""
from uuid import UUID, uuid4
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import get_current_user
from ..core.storage import get_storage_service, StorageService
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.file import File, FileSource, FileShare, FilePermission
from ..schemas.file import (
    LinkDriveFileRequest,
    LinkDriveFileResponse,
    FileResponse,
    FileListResponse,
    UploadFileResponse,
    FileDownloadResponse,
    ShareFileRequest,
    ShareFileResponse,
    FileShareResponse,
    SharedFileResponse,
    SharedFileListResponse,
)
from .activity import log_activity
from ..core.audit import log_file_share, AuditAction

router = APIRouter(prefix="/api", tags=["files"])


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


def can_delete_files(db: Session, deal: Deal, user: User) -> bool:
    """Check if user can delete files (admin only)"""
    role = get_deal_role(db, deal, user)
    return role == UserRole.ADMIN.value


def can_access_file(db: Session, file: File, user: User) -> bool:
    """Check if user can access a file (member of associated deal, admin, or shared with user)"""
    # Admin can access all files
    if user.role == UserRole.ADMIN.value:
        return True

    # Check if user has a direct file share
    share = db.query(FileShare).filter(
        FileShare.file_id == file.id,
        FileShare.shared_with == user.id
    ).first()
    if share is not None:
        return True

    # Check if user is a member of the associated deal
    deal = db.query(Deal).filter(Deal.id == file.deal_id).first()
    if deal is None:
        return False
    return can_access_deal(db, deal, user)


def can_download_file(db: Session, file: File, user: User) -> bool:
    """Check if user can download a file.

    Requires:
    - Admin role, OR
    - Deal membership (any role can download), OR
    - File share with 'download' or 'edit' permission
    """
    # Admin can download all files
    if user.role == UserRole.ADMIN.value:
        return True

    # Check if user is a member of the associated deal
    deal = db.query(Deal).filter(Deal.id == file.deal_id).first()
    if deal and can_access_deal(db, deal, user):
        return True

    # Check if user has a file share with download or edit permission
    share = db.query(FileShare).filter(
        FileShare.file_id == file.id,
        FileShare.shared_with == user.id
    ).first()
    if share is not None:
        # VIEW permission doesn't allow download, DOWNLOAD and EDIT do
        return share.permission in [FilePermission.DOWNLOAD, FilePermission.EDIT]

    return False


@router.post("/deals/{deal_id}/files/link", response_model=LinkDriveFileResponse, status_code=status.HTTP_201_CREATED)
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
    db.flush()

    # Log activity
    log_activity(
        db=db,
        deal_id=deal_id,
        actor_id=current_user.id,
        action="file_link",
        details={"file_name": file.name, "file_id": str(file.id), "source": "drive"}
    )

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


@router.post("/deals/{deal_id}/files/upload", response_model=UploadFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    deal_id: UUID,
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Upload a file directly to the platform (GCS).

    - **file**: Multipart file upload (max 100MB)

    Allowed file types: PDF, Word, Excel, PowerPoint, images, text, CSV, archives.
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

    # Check permission to upload files
    if not can_upload_files(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only partners and admins can upload files"
        )

    # Check if deal is closed
    if deal.status == 'closed':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot upload files to a closed deal"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    is_valid, error_msg = storage.validate_file_size(file_size)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=error_msg
        )

    # Validate MIME type
    mime_type = file.content_type or "application/octet-stream"
    is_valid, error_msg = storage.validate_mime_type(mime_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=error_msg
        )

    # Generate file ID and upload to GCS
    file_id = uuid4()
    filename = file.filename or "unnamed_file"

    try:
        gcs_path = await storage.upload_file(
            deal_id=deal_id,
            file_id=file_id,
            filename=filename,
            content=content,
            mime_type=mime_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {str(e)}"
        )

    # Create the file record
    file_record = File(
        id=file_id,
        deal_id=deal_id,
        name=filename,
        source=FileSource.GCS,
        source_id=gcs_path,
        mime_type=mime_type,
        size_bytes=file_size,
        uploaded_by=current_user.id
    )

    db.add(file_record)

    # Log activity
    log_activity(
        db=db,
        deal_id=deal_id,
        actor_id=current_user.id,
        action="file_upload",
        details={"file_name": filename, "file_id": str(file_id), "source": "gcs", "size_bytes": file_size}
    )

    db.commit()
    db.refresh(file_record)

    return UploadFileResponse(
        id=file_record.id,
        name=file_record.name,
        mime_type=file_record.mime_type,
        size_bytes=file_record.size_bytes,
        source="gcs",
        source_id=file_record.source_id
    )


@router.get("/deals/{deal_id}/files", response_model=FileListResponse)
async def list_deal_files(
    deal_id: UUID,
    source: Optional[str] = Query(None, description="Filter by source (drive or gcs)"),
    search: Optional[str] = Query(None, description="Search files by name (case-insensitive partial match)"),
    sort_by: Optional[str] = Query("date", description="Sort by: name, date, type"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all files associated with a deal.

    - **source**: Filter by source type (drive or gcs)
    - **search**: Search files by name (case-insensitive partial match)
    - **sort_by**: Sort by field (name, date, type). Defaults to date.
    - **sort_order**: Sort direction (asc, desc). Defaults to desc.

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

    # Filter by source
    if source:
        if source == "drive":
            query = query.filter(File.source == FileSource.DRIVE)
        elif source == "gcs":
            query = query.filter(File.source == FileSource.GCS)

    # Search by filename (case-insensitive)
    if search:
        query = query.filter(File.name.ilike(f"%{search}%"))

    # Determine sort column
    sort_column = File.created_at  # default
    if sort_by == "name":
        sort_column = File.name
    elif sort_by == "type":
        sort_column = File.mime_type
    elif sort_by == "date":
        sort_column = File.created_at

    # Apply sort order
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    files = query.all()

    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=len(files)
    )


@router.get("/files/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Get a download URL for a file.

    For GCS files, returns a signed URL valid for 60 minutes.
    For Drive files, returns the Google Drive file URL.

    User must be a member of the deal associated with the file,
    or have a file share with 'download' or 'edit' permission.
    """
    # Get the file
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Check download permission (stricter than access)
    if not can_download_file(db, file, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download this file"
        )

    # Generate download URL based on source
    if file.source == FileSource.GCS:
        if not file.source_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File storage path not found"
            )
        try:
            download_url = storage.generate_signed_url(
                gcs_path=file.source_id,
                expiration_minutes=60,
                for_download=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download URL: {str(e)}"
            )
    elif file.source == FileSource.DRIVE:
        # For Drive files, return the Google Drive URL
        download_url = f"https://drive.google.com/file/d/{file.source_id}/view"
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown file source"
        )

    return FileDownloadResponse(
        id=file.id,
        name=file.name,
        download_url=download_url,
        expires_in_minutes=60 if file.source == FileSource.GCS else 0
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Delete a file.

    Only admins can delete files.
    For GCS files, the file will also be deleted from storage.

    User must be a member of the deal associated with the file.
    """
    # Get the file
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Get the deal
    deal = db.query(Deal).filter(Deal.id == file.deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated deal not found"
        )

    # Check access to deal
    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Check permission to delete files
    if not can_delete_files(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete files"
        )

    # Delete from GCS if applicable
    if file.source == FileSource.GCS and file.source_id:
        try:
            storage.delete_file(file.source_id)
        except Exception as e:
            # Log the error but continue with database deletion
            # The file record should be removed even if GCS deletion fails
            print(f"Warning: Failed to delete file from GCS: {e}")

    # Log activity before deletion
    log_activity(
        db=db,
        deal_id=file.deal_id,
        actor_id=current_user.id,
        action="file_delete",
        details={"file_name": file.name, "file_id": str(file.id)}
    )

    # Delete the file record
    db.delete(file)
    db.commit()

    return None


@router.post("/files/{file_id}/share", response_model=ShareFileResponse, status_code=status.HTTP_201_CREATED)
async def share_file(
    file_id: UUID,
    request: ShareFileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a file with another user (cross-FO sharing).

    - **user_id**: ID of the user to share the file with
    - **permission**: Permission level to grant (view or edit)

    Only admins can share files. The target user will be able to access
    this specific file even if they are not a member of the associated deal.
    """
    # Get the file
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Get the deal
    deal = db.query(Deal).filter(Deal.id == file.deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated deal not found"
        )

    # Check access to deal
    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Only admins can share files
    role = get_deal_role(db, deal, current_user)
    if role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can share files"
        )

    # Check if target user exists
    target_user = db.query(User).filter(User.id == request.user_id).first()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )

    # Check if share already exists
    existing_share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.shared_with == request.user_id
    ).first()

    if existing_share:
        # Update existing share with new permission
        existing_share.permission = FilePermission(request.permission.value)
        db.commit()
        db.refresh(existing_share)
        share = existing_share
    else:
        # Create new file share
        share = FileShare(
            file_id=file_id,
            shared_with=request.user_id,
            permission=FilePermission(request.permission.value)
        )
        db.add(share)

        # Log to audit log
        log_file_share(
            db=db,
            actor=current_user,
            file_id=file_id,
            shared_with_user_id=request.user_id,
            permission=request.permission.value,
            action=AuditAction.FILE_SHARE
        )

        db.commit()
        db.refresh(share)

    return ShareFileResponse(
        message="File shared successfully",
        share=FileShareResponse(
            file_id=share.file_id,
            shared_with=share.shared_with,
            permission=share.permission,
            shared_at=share.shared_at
        )
    )


@router.delete("/files/{file_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_file_share(
    file_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a file share (cross-FO sharing).

    - **file_id**: ID of the file
    - **user_id**: ID of the user to revoke access from

    Only admins can revoke file shares.
    """
    # Get the file
    file = db.query(File).filter(File.id == file_id).first()
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Get the deal
    deal = db.query(Deal).filter(Deal.id == file.deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated deal not found"
        )

    # Check access to deal
    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Only admins can revoke file shares
    role = get_deal_role(db, deal, current_user)
    if role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can revoke file shares"
        )

    # Find the share
    share = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.shared_with == user_id
    ).first()

    if share is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File share not found"
        )

    # Log to audit log before deletion
    log_file_share(
        db=db,
        actor=current_user,
        file_id=file_id,
        shared_with_user_id=user_id,
        permission=share.permission.value,
        action=AuditAction.FILE_UNSHARE
    )

    # Delete the share
    db.delete(share)
    db.commit()

    return None


@router.get("/files/shared", response_model=SharedFileListResponse)
async def list_shared_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all files shared with the current user.

    Returns files that have been explicitly shared with the user via file shares,
    along with the permission level granted.
    """
    # Get all file shares for the current user
    shares = db.query(FileShare).filter(
        FileShare.shared_with == current_user.id
    ).all()

    # Build response with file details and share info
    shared_files = []
    for share in shares:
        file = db.query(File).filter(File.id == share.file_id).first()
        if file:
            shared_files.append(SharedFileResponse(
                id=file.id,
                deal_id=file.deal_id,
                name=file.name,
                source=file.source.value,
                source_id=file.source_id,
                mime_type=file.mime_type,
                size_bytes=file.size_bytes,
                uploaded_by=file.uploaded_by,
                created_at=file.created_at,
                permission=share.permission.value,
                shared_at=share.shared_at
            ))

    return SharedFileListResponse(
        files=shared_files,
        total=len(shared_files)
    )
