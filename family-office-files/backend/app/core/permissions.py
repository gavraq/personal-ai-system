"""
Permissions module for role-based access control (RBAC).

Implements a role hierarchy: Admin > Partner > Viewer
- Admin: Full access to all resources and actions
- Partner: Can create, read, update deals and files (but not delete)
- Viewer: Read-only access to assigned deals

Also supports deal-level role overrides via DealMember.role_override.
"""
from enum import IntEnum
from uuid import UUID
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from .cache import (
    get_cached_deal_membership,
    cache_deal_membership,
)


class RoleLevel(IntEnum):
    """
    Numeric role levels for hierarchy comparison.
    Higher number = more permissions.
    """
    VIEWER = 1
    PARTNER = 2
    ADMIN = 3


# Map string role values to RoleLevel
# NOTE: Maps both string literals ('admin', 'partner', 'viewer') AND UserRole enum values
# because different parts of the codebase pass different formats. This ensures compatibility
# across internal operations (using enums) and external APIs (using strings).
ROLE_LEVEL_MAP = {
    'viewer': RoleLevel.VIEWER,
    'partner': RoleLevel.PARTNER,
    'admin': RoleLevel.ADMIN,
    UserRole.VIEWER.value: RoleLevel.VIEWER,
    UserRole.PARTNER.value: RoleLevel.PARTNER,
    UserRole.ADMIN.value: RoleLevel.ADMIN,
}


def get_role_level(role: str) -> RoleLevel:
    """Convert a role string to its numeric level."""
    return ROLE_LEVEL_MAP.get(role, RoleLevel.VIEWER)


def has_minimum_role(user_role: str, minimum_role: str) -> bool:
    """
    Check if user's role meets or exceeds the minimum required role.

    Args:
        user_role: The user's current role (as string)
        minimum_role: The minimum required role (as string)

    Returns:
        True if user's role level >= minimum role level
    """
    user_level = get_role_level(user_role)
    min_level = get_role_level(minimum_role)
    return user_level >= min_level


def is_admin(user: User) -> bool:
    """Check if user is an admin."""
    return user.role == UserRole.ADMIN.value


def is_partner_or_above(user: User) -> bool:
    """Check if user is a partner or admin."""
    return user.role in [UserRole.ADMIN.value, UserRole.PARTNER.value]


def is_viewer(user: User) -> bool:
    """Check if user is a viewer (lowest role)."""
    return user.role == UserRole.VIEWER.value


def _get_deal_membership_with_cache(db: Session, deal_id: UUID, user_id: UUID) -> Optional[DealMember]:
    """
    Get deal membership with Redis cache.

    First checks cache, falls back to database if not cached.
    Caches the result on database hit.

    Args:
        db: Database session
        deal_id: Deal UUID
        user_id: User UUID

    Returns:
        DealMember object or None if not a member
    """
    # Try cache first for quick membership status check
    cached = get_cached_deal_membership(deal_id, user_id)
    if cached is not None:
        if not cached["is_member"]:
            return None
        # IMPORTANT: Even on cache hit, we must fetch the actual ORM object from DB.
        # The cache only stores a dict with is_member and role_override - not the full
        # SQLAlchemy object. We need the ORM object attached to the session for:
        # 1. Lazy loading of relationships to work
        # 2. SQLAlchemy session tracking and identity map consistency
        # 3. Any future attribute access that requires DB state
        # The cache validation confirms membership exists before the (now guaranteed) DB query.
        membership = db.query(DealMember).filter(
            DealMember.deal_id == deal_id,
            DealMember.user_id == user_id
        ).first()
        return membership

    # Cache miss - fetch from database
    membership = db.query(DealMember).filter(
        DealMember.deal_id == deal_id,
        DealMember.user_id == user_id
    ).first()

    # Cache the result
    cache_deal_membership(
        deal_id,
        user_id,
        is_member=membership is not None,
        role_override=membership.role_override if membership else None
    )

    return membership


def get_effective_deal_role(db: Session, deal: Deal, user: User) -> str:
    """
    Get user's effective role for a specific deal.

    Role resolution order (three-tier hierarchy):
    1. If user is admin -> admin (global bypass, skips membership check entirely)
    2. If user has deal membership with role_override -> role_override
    3. Otherwise -> user's global role

    This allows flexible permission models:
    - A Partner can be granted Viewer-only access to sensitive deals (role_override = 'viewer')
    - A Viewer can be temporarily elevated to Partner on specific deals (role_override = 'partner')
    - Admins always have full access regardless of membership

    Uses cache to avoid N+1 queries when checking multiple users/deals.

    Args:
        db: Database session
        deal: The deal to check
        user: The user to check

    Returns:
        The effective role string for this user on this deal
    """
    # Admin always has admin access - bypass membership lookup entirely for performance
    if user.role == UserRole.ADMIN.value:
        return UserRole.ADMIN.value

    # Check for deal membership with role override (using cache to avoid N+1)
    membership = _get_deal_membership_with_cache(db, deal.id, user.id)

    # Deal-level override takes precedence over global role when present
    if membership and membership.role_override:
        return membership.role_override

    # Fall back to global role (from user record)
    return user.role


def can_read_deal(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can read a deal.

    Requires: deal membership or admin role.
    """
    if user.role == UserRole.ADMIN.value:
        return True

    # Use cached membership lookup
    membership = _get_deal_membership_with_cache(db, deal.id, user.id)
    return membership is not None


def can_write_deal(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can modify a deal (update, manage members).

    Requires: deal membership with partner+ role or admin.
    Viewers cannot modify deals.
    """
    effective_role = get_effective_deal_role(db, deal, user)
    return has_minimum_role(effective_role, UserRole.PARTNER.value)


def can_delete_deal(user: User) -> bool:
    """
    Check if user can delete deals.

    Requires: admin role only.
    """
    return user.role == UserRole.ADMIN.value


def can_create_deal(user: User) -> bool:
    """
    Check if user can create new deals.

    Requires: partner or admin role.
    """
    return user.role in [UserRole.ADMIN.value, UserRole.PARTNER.value]


def can_upload_files(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can upload/link files to a deal.

    Requires: deal membership with partner+ role or admin.
    """
    effective_role = get_effective_deal_role(db, deal, user)
    return has_minimum_role(effective_role, UserRole.PARTNER.value)


def can_delete_files(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can delete files from a deal.

    Requires: admin role only.
    """
    effective_role = get_effective_deal_role(db, deal, user)
    return effective_role == UserRole.ADMIN.value


def can_share_files(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can share files with other users.

    Requires: admin role only.
    """
    effective_role = get_effective_deal_role(db, deal, user)
    return effective_role == UserRole.ADMIN.value


def can_manage_deal_members(db: Session, deal: Deal, user: User) -> bool:
    """
    Check if user can add/remove members from a deal.

    Requires: deal membership with partner+ role or admin.
    """
    effective_role = get_effective_deal_role(db, deal, user)
    return has_minimum_role(effective_role, UserRole.PARTNER.value)


def can_manage_users(user: User) -> bool:
    """
    Check if user can manage other users (view list, change roles).

    Requires: admin role only.
    """
    return user.role == UserRole.ADMIN.value


def can_view_audit_log(user: User) -> bool:
    """
    Check if user can view the audit log.

    Requires: admin role only.
    """
    return user.role == UserRole.ADMIN.value


def require_deal_read_access(db: Session, deal: Deal, user: User) -> None:
    """
    Raise 403 if user cannot read the deal.

    Args:
        db: Database session
        deal: The deal to check
        user: The user to check

    Raises:
        HTTPException: 403 if user lacks read access
    """
    if not can_read_deal(db, deal, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )


def require_deal_write_access(db: Session, deal: Deal, user: User) -> None:
    """
    Raise 403 if user cannot modify the deal.

    Args:
        db: Database session
        deal: The deal to check
        user: The user to check

    Raises:
        HTTPException: 403 if user lacks write access
    """
    if not can_write_deal(db, deal, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this deal. Partner or Admin role required."
        )


def require_minimum_role(user: User, minimum_role: UserRole) -> None:
    """
    Raise 403 if user's role is below the minimum.

    Args:
        user: The user to check
        minimum_role: The minimum required role

    Raises:
        HTTPException: 403 if user lacks the minimum role
    """
    if not has_minimum_role(user.role, minimum_role.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {minimum_role.value} or higher"
        )


# Permission matrix documentation
PERMISSION_MATRIX = """
Permission Matrix:

Action                    | Viewer | Partner | Admin
--------------------------|--------|---------|------
Register/Login            | ✓      | ✓       | ✓
View own profile          | ✓      | ✓       | ✓
List accessible deals     | ✓      | ✓       | ✓
View deal details         | ✓*     | ✓*      | ✓
Create deal               | ✗      | ✓       | ✓
Update deal               | ✗      | ✓*      | ✓
Delete deal               | ✗      | ✗       | ✓
List deal files           | ✓*     | ✓*      | ✓
Download file             | ✓*     | ✓*      | ✓
Upload/Link file          | ✗      | ✓*      | ✓
Delete file               | ✗      | ✗       | ✓
Share file                | ✗      | ✗       | ✓
Add deal member           | ✗      | ✓*      | ✓
Remove deal member        | ✗      | ✓*      | ✓
View activity feed        | ✓*     | ✓*      | ✓
Run agent                 | ✓*     | ✓*      | ✓
Manage alerts             | ✓**    | ✓**     | ✓
List all users            | ✗      | ✗       | ✓
Change user roles         | ✗      | ✗       | ✓
View audit log            | ✗      | ✗       | ✓

* = Requires deal membership (or role override on deal)
** = Only own alerts, unless admin
"""
