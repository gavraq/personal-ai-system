"""
Users router for user management (admin only)
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import require_admin
from ..core.audit import log_role_change
from ..models.user import User, UserRole
from ..schemas.user import RoleUpdateRequest, UserResponse, UserListResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).

    Returns paginated list of users with their roles.
    """
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    total = db.query(User).count()

    # Get paginated users
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    request: RoleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role (admin only).

    - **user_id**: UUID of the user to update
    - **role**: New role to assign (admin, partner, viewer)

    Returns the updated user.
    """
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from demoting themselves if they're the only admin
    if current_user.id == user_id and request.role != UserRole.ADMIN:
        admin_count = db.query(User).filter(User.role == 'admin').count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last admin user"
            )

    # Capture old role for audit log
    old_role = user.role

    # Update the role
    user.role = request.role.value

    # Log the role change in audit log
    log_role_change(
        db=db,
        actor=current_user,
        user_id=user.id,
        old_role=old_role,
        new_role=request.role.value
    )

    db.commit()
    db.refresh(user)

    return user
