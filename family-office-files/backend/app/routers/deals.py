"""
Deals router for deal/transaction management
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from sqlalchemy import func

from ..core.database import get_db
from ..core.deps import get_current_user, require_role
from ..core.permissions import (
    can_read_deal,
    can_write_deal,
    can_create_deal,
    can_manage_deal_members,
    require_deal_read_access,
    require_deal_write_access,
)
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.file import File
from ..schemas.deal import (
    DealCreate,
    DealUpdate,
    DealResponse,
    DealListResponse,
    DealMemberCreate,
    DealMemberResponse,
    DealMemberListResponse,
    DealStatusEnum,
)
from .activity import log_activity
from ..core.audit import log_deal_membership_change, log_deal_role_override, AuditAction
from ..core.cache import (
    invalidate_deal_cache,
    invalidate_deal_membership_cache,
)

router = APIRouter(prefix="/api/deals", tags=["deals"])


def is_deal_member(db: Session, deal_id: UUID, user_id: UUID) -> bool:
    """Check if user is a member of the deal"""
    return db.query(DealMember).filter(
        DealMember.deal_id == deal_id,
        DealMember.user_id == user_id
    ).first() is not None


def can_access_deal(db: Session, deal: Deal, user: User) -> bool:
    """Check if user can access the deal (admin or member) - for read operations"""
    return can_read_deal(db, deal, user)


def get_deal_file_count(db: Session, deal_id: UUID) -> int:
    """Get the count of files for a deal"""
    return db.query(func.count(File.id)).filter(File.deal_id == deal_id).scalar() or 0


def deal_to_response(deal: Deal, file_count: int = 0) -> DealResponse:
    """Convert Deal model to DealResponse with file_count

    Args:
        deal: Deal model instance
        file_count: Pre-computed file count (to avoid N+1 queries)
    """
    return DealResponse(
        id=deal.id,
        title=deal.title,
        description=deal.description,
        status=deal.status,
        created_by=deal.created_by,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        file_count=file_count
    )


def get_deals_with_file_counts(db: Session, deal_ids: list[UUID]) -> dict[UUID, int]:
    """Batch query to get file counts for multiple deals in one query.

    Args:
        db: Database session
        deal_ids: List of deal IDs to get file counts for

    Returns:
        Dictionary mapping deal_id to file count
    """
    if not deal_ids:
        return {}

    result = db.query(
        File.deal_id,
        func.count(File.id).label('count')
    ).filter(
        File.deal_id.in_(deal_ids)
    ).group_by(File.deal_id).all()

    return {row.deal_id: row.count for row in result}


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    request: DealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new deal.

    - **title**: Deal title (required)
    - **description**: Deal description (optional)

    Only admin and partner roles can create deals.
    The creator is automatically added as a deal member.
    Default status is 'draft'.
    """
    # Check permission
    if not can_create_deal(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and partners can create deals"
        )

    # Create the deal - status defaults to 'draft' in the model
    deal = Deal(
        title=request.title,
        description=request.description,
        created_by=current_user.id
    )

    db.add(deal)
    db.flush()  # Get the deal ID

    # Auto-assign creator as deal member
    member = DealMember(
        deal_id=deal.id,
        user_id=current_user.id
    )
    db.add(member)

    # Log activity
    log_activity(
        db=db,
        deal_id=deal.id,
        actor_id=current_user.id,
        action="deal_create",
        details={"title": deal.title}
    )

    db.commit()
    db.refresh(deal)

    return deal_to_response(deal, get_deal_file_count(db, deal.id))


@router.get("", response_model=DealListResponse)
async def list_deals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[DealStatusEnum] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List deals accessible to the current user.

    Admins can see all deals.
    Other users can only see deals they are members of.
    """
    offset = (page - 1) * page_size

    # Build base query
    if current_user.role == UserRole.ADMIN.value:
        # Admin can see all deals
        query = db.query(Deal)
    else:
        # Non-admin can only see deals they are members of
        query = db.query(Deal).join(DealMember).filter(
            DealMember.user_id == current_user.id
        )

    # Apply status filter
    if status_filter:
        query = query.filter(Deal.status == status_filter.value)

    # Get total count
    total = query.count()

    # Get paginated deals, sorted by last activity (updated_at, then created_at)
    deals = query.order_by(
        Deal.updated_at.desc().nullslast(),
        Deal.created_at.desc()
    ).offset(offset).limit(page_size).all()

    # Batch query file counts to avoid N+1
    deal_ids = [d.id for d in deals]
    file_counts = get_deals_with_file_counts(db, deal_ids)

    return DealListResponse(
        deals=[deal_to_response(d, file_counts.get(d.id, 0)) for d in deals],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific deal by ID.

    User must be a deal member or admin to access.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    return deal_to_response(deal, get_deal_file_count(db, deal.id))


@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID,
    request: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a deal's metadata.

    - **title**: New title (optional)
    - **description**: New description (optional)
    - **status**: New status (optional, must follow draft→active→closed workflow)

    User must be a deal member with partner or admin role.
    Viewers cannot modify deals.
    Closed deals cannot be edited.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check read access first
    require_deal_read_access(db, deal, current_user)

    # Check write access (partner+ required)
    require_deal_write_access(db, deal, current_user)

    # Check if deal is closed (read-only)
    if deal.status == 'closed' and request.status != DealStatusEnum.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Closed deals cannot be edited"
        )

    # Validate status transitions
    if request.status:
        current_status = deal.status
        new_status = request.status.value

        valid_transitions = {
            'draft': ['active'],
            'active': ['closed'],
            'closed': []  # No transitions from closed
        }

        if new_status != current_status and new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status} to {new_status}"
            )

    # Track changes for activity log
    changes = {}
    if request.title is not None and request.title != deal.title:
        changes["title"] = {"old": deal.title, "new": request.title}
        deal.title = request.title
    if request.description is not None and request.description != deal.description:
        changes["description"] = {"old": deal.description, "new": request.description}
        deal.description = request.description
    if request.status is not None and request.status.value != deal.status:
        changes["status"] = {"old": deal.status, "new": request.status.value}
        deal.status = request.status.value

    # Log activity if there were changes
    if changes:
        log_activity(
            db=db,
            deal_id=deal.id,
            actor_id=current_user.id,
            action="deal_update",
            details={"changes": changes}
        )

    db.commit()
    db.refresh(deal)

    return deal_to_response(deal, get_deal_file_count(db, deal.id))


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: UUID,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Delete a deal (admin only).

    This will cascade delete all deal members and associated data.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    db.delete(deal)
    db.commit()


# Deal Member endpoints

@router.post("/{deal_id}/members", response_model=DealMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_deal_member(
    deal_id: UUID,
    request: DealMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to a deal.

    User must be a deal member with partner or admin role.
    Viewers cannot add members.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check read access first
    require_deal_read_access(db, deal, current_user)

    # Check member management permission (partner+ required)
    if not can_manage_deal_members(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage deal members. Partner or Admin role required."
        )

    # Check if deal is closed
    if deal.status == 'closed':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify members of a closed deal"
        )

    # Check if user exists
    from ..models.user import User as UserModel
    target_user = db.query(UserModel).filter(UserModel.id == request.user_id).first()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already a member
    existing = db.query(DealMember).filter(
        DealMember.deal_id == deal_id,
        DealMember.user_id == request.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this deal"
        )

    # Validate role_override
    if request.role_override and request.role_override not in ['admin', 'partner', 'viewer']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_override. Must be admin, partner, or viewer"
        )

    # Create membership
    member = DealMember(
        deal_id=deal_id,
        user_id=request.user_id,
        role_override=request.role_override
    )
    db.add(member)

    # Log activity
    log_activity(
        db=db,
        deal_id=deal_id,
        actor_id=current_user.id,
        action="member_add",
        details={"user_email": target_user.email, "user_id": str(request.user_id)}
    )

    # Log to audit log
    log_deal_membership_change(
        db=db,
        actor=current_user,
        deal_id=deal_id,
        user_id=request.user_id,
        action=AuditAction.MEMBER_ADD,
        new_value={"user_id": str(request.user_id), "user_email": target_user.email, "role_override": request.role_override}
    )

    db.commit()
    db.refresh(member)

    # Invalidate membership cache for the new member
    invalidate_deal_membership_cache(deal_id, request.user_id)

    return DealMemberResponse(
        deal_id=member.deal_id,
        user_id=member.user_id,
        role_override=member.role_override,
        added_at=member.added_at,
        user_email=target_user.email
    )


@router.get("/{deal_id}/members", response_model=DealMemberListResponse)
async def list_deal_members(
    deal_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all members of a deal.

    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 20, max 100)

    User must be a deal member or admin to view members.
    """
    offset = (page - 1) * page_size

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    if not can_access_deal(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this deal"
        )

    # Get total count
    total = db.query(DealMember).filter(DealMember.deal_id == deal_id).count()

    # Get paginated members with eager loading of user relationship
    members = db.query(DealMember).options(
        joinedload(DealMember.user)
    ).filter(
        DealMember.deal_id == deal_id
    ).order_by(DealMember.added_at.desc()).offset(offset).limit(page_size).all()

    # Build response using eagerly loaded user data (no N+1)
    member_responses = [
        DealMemberResponse(
            deal_id=m.deal_id,
            user_id=m.user_id,
            role_override=m.role_override,
            added_at=m.added_at,
            user_email=m.user.email if m.user else None
        )
        for m in members
    ]

    return DealMemberListResponse(
        members=member_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/{deal_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_deal_member(
    deal_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a deal.

    User must be a deal member with partner or admin role.
    Viewers cannot remove members.
    Cannot remove the deal creator.
    """
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check read access first
    require_deal_read_access(db, deal, current_user)

    # Check member management permission (partner+ required)
    if not can_manage_deal_members(db, deal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage deal members. Partner or Admin role required."
        )

    # Check if deal is closed
    if deal.status == 'closed':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify members of a closed deal"
        )

    # Cannot remove the creator
    if deal.created_by == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the deal creator from the deal"
        )

    member = db.query(DealMember).filter(
        DealMember.deal_id == deal_id,
        DealMember.user_id == user_id
    ).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this deal"
        )

    # Get removed user email for activity log
    from ..models.user import User as UserModel
    removed_user = db.query(UserModel).filter(UserModel.id == user_id).first()

    # Log activity
    log_activity(
        db=db,
        deal_id=deal_id,
        actor_id=current_user.id,
        action="member_remove",
        details={"user_email": removed_user.email if removed_user else None, "user_id": str(user_id)}
    )

    # Log to audit log
    log_deal_membership_change(
        db=db,
        actor=current_user,
        deal_id=deal_id,
        user_id=user_id,
        action=AuditAction.MEMBER_REMOVE,
        old_value={"user_id": str(user_id), "user_email": removed_user.email if removed_user else None, "role_override": member.role_override}
    )

    db.delete(member)
    db.commit()

    # Invalidate membership cache for the removed member
    invalidate_deal_membership_cache(deal_id, user_id)
