"""
Agents router for agent run operations
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.agent import AgentRun, AgentType, AgentStatus
from ..schemas.agent import (
    AgentRunResponse,
    AgentRunListResponse,
    AgentSummary,
    AgentSummaryListResponse,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


def get_user_accessible_deal_ids(db: Session, user: User) -> list[UUID]:
    """Get list of deal IDs the user can access"""
    if user.role == UserRole.ADMIN.value:
        deals = db.query(Deal.id).all()
        return [d.id for d in deals]
    else:
        memberships = db.query(DealMember.deal_id).filter(
            DealMember.user_id == user.id
        ).all()
        return [m.deal_id for m in memberships]


def agent_run_to_response(db: Session, run: AgentRun) -> AgentRunResponse:
    """Convert AgentRun model to AgentRunResponse with user email"""
    user = db.query(User).filter(User.id == run.user_id).first()
    return AgentRunResponse(
        id=run.id,
        deal_id=run.deal_id,
        user_id=run.user_id,
        user_email=user.email if user else None,
        agent_type=run.agent_type,
        status=run.status,
        input=run.input or {},
        output=run.output,
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at
    )


def extract_summary_excerpt(output: dict | None) -> str | None:
    """Extract a summary excerpt from agent output"""
    if not output:
        return None
    # Common patterns for summary extraction
    if 'summary' in output:
        text = str(output['summary'])
        return text[:150] + '...' if len(text) > 150 else text
    if 'result' in output:
        text = str(output['result'])
        return text[:150] + '...' if len(text) > 150 else text
    if 'message' in output:
        text = str(output['message'])
        return text[:150] + '...' if len(text) > 150 else text
    # Fallback: stringify first key-value pair
    for key, value in output.items():
        if isinstance(value, str):
            text = value
            return text[:150] + '...' if len(text) > 150 else text
    return None


@router.get("/runs", response_model=AgentRunListResponse)
async def list_agent_runs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    deal_id: Optional[UUID] = Query(None, description="Filter by specific deal"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    status_filter: Optional[AgentStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of agent runs for user's accessible deals.

    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 20, max 100)
    - **deal_id**: Optional filter by specific deal
    - **agent_type**: Optional filter by agent type
    - **status_filter**: Optional filter by status

    Returns agent runs from deals the user has access to, sorted by most recent first.
    """
    offset = (page - 1) * page_size

    # Get accessible deal IDs
    accessible_deal_ids = get_user_accessible_deal_ids(db, current_user)

    if not accessible_deal_ids:
        return AgentRunListResponse(
            runs=[],
            total=0,
            page=page,
            page_size=page_size
        )

    # Build query filtering by accessible deals
    query = db.query(AgentRun).filter(AgentRun.deal_id.in_(accessible_deal_ids))

    # Optional filter by specific deal
    if deal_id:
        if deal_id not in accessible_deal_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this deal"
            )
        query = query.filter(AgentRun.deal_id == deal_id)

    # Optional filter by agent type
    if agent_type:
        query = query.filter(AgentRun.agent_type == agent_type)

    # Optional filter by status
    if status_filter:
        query = query.filter(AgentRun.status == status_filter)

    # Get total count
    total = query.count()

    # Get paginated runs, sorted by most recent first
    runs = query.order_by(AgentRun.started_at.desc()).offset(offset).limit(page_size).all()

    return AgentRunListResponse(
        runs=[agent_run_to_response(db, r) for r in runs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific agent run.

    User must be a deal member or admin to view the run.
    """
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent run not found"
        )

    # Check access
    if current_user.role != UserRole.ADMIN.value:
        is_member = db.query(DealMember).filter(
            DealMember.deal_id == run.deal_id,
            DealMember.user_id == current_user.id
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this agent run"
            )

    return agent_run_to_response(db, run)


@router.get("/summaries", response_model=AgentSummaryListResponse)
async def list_agent_summaries(
    limit: int = Query(10, ge=1, le=50, description="Number of summaries to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latest agent run summaries per agent type per deal for dashboard display.

    Returns the most recent completed (or failed) agent run for each agent type
    in each accessible deal, sorted by most recent first.
    """
    # Get accessible deal IDs
    accessible_deal_ids = get_user_accessible_deal_ids(db, current_user)

    if not accessible_deal_ids:
        return AgentSummaryListResponse(summaries=[], total=0)

    # Use a subquery to get the latest run per agent_type per deal
    from sqlalchemy import func, and_

    subquery = (
        db.query(
            AgentRun.deal_id,
            AgentRun.agent_type,
            func.max(AgentRun.started_at).label('latest_started_at')
        )
        .filter(AgentRun.deal_id.in_(accessible_deal_ids))
        .filter(AgentRun.status.in_([AgentStatus.COMPLETED, AgentStatus.FAILED]))
        .group_by(AgentRun.deal_id, AgentRun.agent_type)
        .subquery()
    )

    # Join with AgentRun to get full records
    runs = (
        db.query(AgentRun)
        .join(
            subquery,
            and_(
                AgentRun.deal_id == subquery.c.deal_id,
                AgentRun.agent_type == subquery.c.agent_type,
                AgentRun.started_at == subquery.c.latest_started_at
            )
        )
        .order_by(AgentRun.started_at.desc())
        .limit(limit)
        .all()
    )

    # Get deal titles
    deal_ids = list(set(r.deal_id for r in runs))
    deals = {d.id: d.title for d in db.query(Deal).filter(Deal.id.in_(deal_ids)).all()}

    summaries = [
        AgentSummary(
            id=run.id,
            deal_id=run.deal_id,
            deal_title=deals.get(run.deal_id, "Unknown Deal"),
            agent_type=run.agent_type,
            status=run.status,
            summary_excerpt=extract_summary_excerpt(run.output),
            started_at=run.started_at,
            completed_at=run.completed_at
        )
        for run in runs
    ]

    return AgentSummaryListResponse(summaries=summaries, total=len(summaries))


@router.get("/deal/{deal_id}/runs", response_model=AgentRunListResponse)
async def list_deal_agent_runs(
    deal_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of agent runs for a specific deal.

    User must be a deal member or admin to view runs.
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
    query = db.query(AgentRun).filter(AgentRun.deal_id == deal_id)

    if agent_type:
        query = query.filter(AgentRun.agent_type == agent_type)

    # Get total count
    total = query.count()

    # Get paginated runs
    runs = query.order_by(AgentRun.started_at.desc()).offset(offset).limit(page_size).all()

    return AgentRunListResponse(
        runs=[agent_run_to_response(db, r) for r in runs],
        total=total,
        page=page,
        page_size=page_size
    )
