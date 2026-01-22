"""
Activity router for activity feed operations
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.audit import Activity
from ..schemas.activity import (
    ActivityResponse,
    ActivityListResponse,
)

router = APIRouter(prefix="/api/activity", tags=["activity"])


def get_user_accessible_deal_ids(db: Session, user: User) -> list[UUID]:
    """Get list of deal IDs the user can access"""
    if user.role == UserRole.ADMIN.value:
        # Admin can see all deals
        deals = db.query(Deal.id).all()
        return [d.id for d in deals]
    else:
        # Non-admin can only see deals they are members of
        memberships = db.query(DealMember.deal_id).filter(
            DealMember.user_id == user.id
        ).all()
        return [m.deal_id for m in memberships]


def activity_to_response(activity: Activity, actor_email: str = None) -> ActivityResponse:
    """Convert Activity model to ActivityResponse with actor email

    Args:
        activity: Activity model instance
        actor_email: Pre-loaded actor email (to avoid N+1 queries)
    """
    return ActivityResponse(
        id=activity.id,
        deal_id=activity.deal_id,
        actor_id=activity.actor_id,
        actor_email=actor_email,
        action=activity.action,
        details=activity.details,
        created_at=activity.created_at
    )


@router.get("", response_model=ActivityListResponse)
async def list_activity(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    deal_id: Optional[UUID] = Query(None, description="Filter by specific deal"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated activity feed for user's accessible deals.

    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 20, max 100)
    - **deal_id**: Optional filter by specific deal
    - **action**: Optional filter by action type (file_upload, deal_create, etc.)

    Returns activities from deals the user has access to, sorted by most recent first.
    """
    offset = (page - 1) * page_size

    # Get accessible deal IDs
    accessible_deal_ids = get_user_accessible_deal_ids(db, current_user)

    if not accessible_deal_ids:
        return ActivityListResponse(
            activities=[],
            total=0,
            page=page,
            page_size=page_size
        )

    # Build query filtering by accessible deals
    query = db.query(Activity).filter(Activity.deal_id.in_(accessible_deal_ids))

    # Optional filter by specific deal
    if deal_id:
        if deal_id not in accessible_deal_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this deal"
            )
        query = query.filter(Activity.deal_id == deal_id)

    # Optional filter by action type
    if action:
        query = query.filter(Activity.action == action)

    # Get total count
    total = query.count()

    # Get paginated activities with eager loading of actor relationship
    activities = query.options(
        joinedload(Activity.actor)
    ).order_by(Activity.created_at.desc()).offset(offset).limit(page_size).all()

    return ActivityListResponse(
        activities=[activity_to_response(a, a.actor.email if a.actor else None) for a in activities],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/deal/{deal_id}", response_model=ActivityListResponse)
async def list_deal_activity(
    deal_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated activity feed for a specific deal.

    - **deal_id**: Deal ID to get activity for
    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 20, max 100)

    User must be a deal member or admin to view activities.
    """
    offset = (page - 1) * page_size

    # Check deal exists
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Check access
    if current_user.role != UserRole.ADMIN.value:
        is_member = db.query(DealMember).filter(
            DealMember.deal_id == deal_id,
            DealMember.user_id == current_user.id
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this deal"
            )

    # Build query
    query = db.query(Activity).filter(Activity.deal_id == deal_id)

    # Get total count
    total = query.count()

    # Get paginated activities with eager loading of actor relationship
    activities = query.options(
        joinedload(Activity.actor)
    ).order_by(Activity.created_at.desc()).offset(offset).limit(page_size).all()

    return ActivityListResponse(
        activities=[activity_to_response(a, a.actor.email if a.actor else None) for a in activities],
        total=total,
        page=page,
        page_size=page_size
    )


# Helper function to log activity (used by other routers)
def log_activity(
    db: Session,
    deal_id: UUID,
    actor_id: UUID,
    action: str,
    details: dict = None
) -> Activity:
    """Log an activity for a deal"""
    activity = Activity(
        deal_id=deal_id,
        actor_id=actor_id,
        action=action,
        details=details
    )
    db.add(activity)
    return activity
