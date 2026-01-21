"""
Audit log router for viewing audit entries (admin only).

Audit entries are immutable - this router only provides read access.
No UPDATE or DELETE operations are supported.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..core.database import get_db
from ..core.deps import require_admin
from ..models.user import User
from ..models.audit import AuditLog
from ..schemas.audit import AuditLogResponse, AuditLogListResponse

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    actor_id: Optional[UUID] = Query(None, description="Filter by actor UUID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[UUID] = Query(None, description="Filter by entity UUID"),
    from_date: Optional[datetime] = Query(None, description="Filter entries from this date"),
    to_date: Optional[datetime] = Query(None, description="Filter entries until this date"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List audit log entries (admin only).

    Returns a paginated list of audit entries with optional filtering.
    Entries are sorted by created_at in descending order (newest first).

    Filters:
    - **action**: Filter by action type (e.g., role_change, member_add)
    - **actor_id**: Filter by the user who performed the action
    - **entity_type**: Filter by entity type (user, deal, file, etc.)
    - **entity_id**: Filter by specific entity UUID
    - **from_date**: Filter entries created on or after this date
    - **to_date**: Filter entries created on or before this date
    """
    # Build query with filters
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if from_date:
        query = query.filter(AuditLog.created_at >= from_date)
    if to_date:
        query = query.filter(AuditLog.created_at <= to_date)

    # Get total count
    total = query.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated results, ordered by newest first
    entries = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size).all()

    # Enrich with actor email
    response_entries = []
    for entry in entries:
        actor = db.query(User).filter(User.id == entry.actor_id).first()
        response_entry = AuditLogResponse(
            id=entry.id,
            actor_id=entry.actor_id,
            actor_email=actor.email if actor else None,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            old_value=entry.old_value,
            new_value=entry.new_value,
            created_at=entry.created_at
        )
        response_entries.append(response_entry)

    return AuditLogListResponse(
        entries=response_entries,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{entry_id}", response_model=AuditLogResponse)
async def get_audit_entry(
    entry_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific audit log entry by ID (admin only).

    Returns the full audit entry including old_value and new_value.
    """
    entry = db.query(AuditLog).filter(AuditLog.id == entry_id).first()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit entry not found"
        )

    # Get actor email
    actor = db.query(User).filter(User.id == entry.actor_id).first()

    return AuditLogResponse(
        id=entry.id,
        actor_id=entry.actor_id,
        actor_email=actor.email if actor else None,
        action=entry.action,
        entity_type=entry.entity_type,
        entity_id=entry.entity_id,
        old_value=entry.old_value,
        new_value=entry.new_value,
        created_at=entry.created_at
    )
