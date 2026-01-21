"""
Audit logging module for tracking permission and data changes.

All permission changes (role changes, deal membership, file shares) are logged
to the audit_log table for compliance and security purposes.

Audit entries are immutable - they cannot be updated or deleted through the API.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.audit import AuditLog
from ..models.user import User


# Audit action types
class AuditAction:
    """Standard audit action types"""
    # User/Role changes
    ROLE_CHANGE = "role_change"
    USER_CREATE = "user_create"

    # Deal changes
    DEAL_CREATE = "deal_create"
    DEAL_UPDATE = "deal_update"
    DEAL_DELETE = "deal_delete"

    # Deal membership
    MEMBER_ADD = "member_add"
    MEMBER_REMOVE = "member_remove"
    MEMBER_ROLE_OVERRIDE = "member_role_override"

    # File operations
    FILE_UPLOAD = "file_upload"
    FILE_DELETE = "file_delete"
    FILE_SHARE = "file_share"
    FILE_UNSHARE = "file_unshare"

    # Permission changes
    PERMISSION_CHANGE = "permission_change"


# Entity types for audit logging
class EntityType:
    """Standard entity types for audit entries"""
    USER = "user"
    DEAL = "deal"
    DEAL_MEMBER = "deal_member"
    FILE = "file"
    FILE_SHARE = "file_share"


def create_audit_entry(
    db: Session,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: UUID,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None
) -> AuditLog:
    """
    Create an immutable audit log entry.

    Args:
        db: Database session
        actor: The user performing the action
        action: The type of action (from AuditAction constants)
        entity_type: The type of entity being acted upon (from EntityType constants)
        entity_id: The UUID of the entity being acted upon
        old_value: Previous value (for updates/deletes)
        new_value: New value (for creates/updates)

    Returns:
        The created AuditLog entry
    """
    audit_entry = AuditLog(
        actor_id=actor.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        created_at=datetime.utcnow()
    )

    db.add(audit_entry)
    db.flush()  # Flush to get the ID without committing

    return audit_entry


def log_role_change(
    db: Session,
    actor: User,
    user_id: UUID,
    old_role: str,
    new_role: str
) -> AuditLog:
    """
    Log a user role change.

    Args:
        db: Database session
        actor: The admin making the change
        user_id: The user whose role is being changed
        old_role: Previous role value
        new_role: New role value

    Returns:
        The created AuditLog entry
    """
    return create_audit_entry(
        db=db,
        actor=actor,
        action=AuditAction.ROLE_CHANGE,
        entity_type=EntityType.USER,
        entity_id=user_id,
        old_value={"role": old_role},
        new_value={"role": new_role}
    )


def log_deal_membership_change(
    db: Session,
    actor: User,
    deal_id: UUID,
    user_id: UUID,
    action: str,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None
) -> AuditLog:
    """
    Log a deal membership change (add/remove member).

    Args:
        db: Database session
        actor: The user making the change
        deal_id: The deal being modified
        user_id: The user being added/removed
        action: MEMBER_ADD or MEMBER_REMOVE
        old_value: Previous membership data (for removes)
        new_value: New membership data (for adds)

    Returns:
        The created AuditLog entry
    """
    return create_audit_entry(
        db=db,
        actor=actor,
        action=action,
        entity_type=EntityType.DEAL_MEMBER,
        entity_id=deal_id,  # Use deal_id as the entity for membership tracking
        old_value=old_value or ({"user_id": str(user_id)} if action == AuditAction.MEMBER_REMOVE else None),
        new_value=new_value or ({"user_id": str(user_id)} if action == AuditAction.MEMBER_ADD else None)
    )


def log_file_share(
    db: Session,
    actor: User,
    file_id: UUID,
    shared_with_user_id: UUID,
    permission: str,
    action: str = AuditAction.FILE_SHARE
) -> AuditLog:
    """
    Log a file share operation.

    Args:
        db: Database session
        actor: The user sharing the file
        file_id: The file being shared
        shared_with_user_id: The user receiving access
        permission: The permission level granted
        action: FILE_SHARE or FILE_UNSHARE

    Returns:
        The created AuditLog entry
    """
    value = {
        "shared_with_user_id": str(shared_with_user_id),
        "permission": permission
    }

    return create_audit_entry(
        db=db,
        actor=actor,
        action=action,
        entity_type=EntityType.FILE_SHARE,
        entity_id=file_id,
        old_value=value if action == AuditAction.FILE_UNSHARE else None,
        new_value=value if action == AuditAction.FILE_SHARE else None
    )


def log_deal_role_override(
    db: Session,
    actor: User,
    deal_id: UUID,
    user_id: UUID,
    old_override: Optional[str],
    new_override: Optional[str]
) -> AuditLog:
    """
    Log a deal-level role override change.

    Args:
        db: Database session
        actor: The user making the change
        deal_id: The deal being modified
        user_id: The user whose override is being changed
        old_override: Previous role override (or None)
        new_override: New role override (or None)

    Returns:
        The created AuditLog entry
    """
    return create_audit_entry(
        db=db,
        actor=actor,
        action=AuditAction.MEMBER_ROLE_OVERRIDE,
        entity_type=EntityType.DEAL_MEMBER,
        entity_id=deal_id,
        old_value={"user_id": str(user_id), "role_override": old_override},
        new_value={"user_id": str(user_id), "role_override": new_override}
    )
