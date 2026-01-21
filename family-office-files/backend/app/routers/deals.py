"""
Deals router for deal/transaction management
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import get_current_user, require_role
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
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

router = APIRouter(prefix="/api/deals", tags=["deals"])


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


def can_create_deal(user: User) -> bool:
    """Check if user can create deals (admin or partner only)"""
    return user.role in [UserRole.ADMIN.value, UserRole.PARTNER.value]


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

    db.commit()
    db.refresh(deal)

    return deal


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

    # Get paginated deals
    deals = query.order_by(Deal.created_at.desc()).offset(offset).limit(page_size).all()

    return DealListResponse(
        deals=[DealResponse.model_validate(d) for d in deals],
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

    return deal


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

    User must be a deal member or admin.
    Closed deals cannot be edited.
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

    # Update fields
    if request.title is not None:
        deal.title = request.title
    if request.description is not None:
        deal.description = request.description
    if request.status is not None:
        deal.status = request.status.value

    db.commit()
    db.refresh(deal)

    return deal


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

    User must be a deal member or admin to add members.
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
    db.commit()
    db.refresh(member)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all members of a deal.

    User must be a deal member or admin to view members.
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

    members = db.query(DealMember).filter(DealMember.deal_id == deal_id).all()

    # Get user emails for response
    from ..models.user import User as UserModel
    member_responses = []
    for m in members:
        user = db.query(UserModel).filter(UserModel.id == m.user_id).first()
        member_responses.append(DealMemberResponse(
            deal_id=m.deal_id,
            user_id=m.user_id,
            role_override=m.role_override,
            added_at=m.added_at,
            user_email=user.email if user else None
        ))

    return DealMemberListResponse(
        members=member_responses,
        total=len(members)
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

    User must be a deal member or admin to remove members.
    Cannot remove the deal creator.
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

    db.delete(member)
    db.commit()
