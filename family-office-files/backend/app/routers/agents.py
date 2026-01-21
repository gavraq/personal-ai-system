"""
Agents router for agent run operations
"""
import asyncio
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User, UserRole
from ..models.deal import Deal, DealMember
from ..models.agent import AgentRun, AgentMessage, AgentType, AgentStatus
from ..models.alert import Alert, AlertMatch, AlertFrequency
from ..schemas.agent import (
    AgentRunResponse,
    AgentRunListResponse,
    AgentSummary,
    AgentSummaryListResponse,
    AgentRunStartRequest,
    AgentRunStartResponse,
    AgentMessageResponse,
    AgentMessagesResponse,
    AlertCreateRequest,
    AlertUpdateRequest,
    AlertResponse,
    AlertListResponse,
    AlertMatchResponse,
    AlertMatchListResponse,
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


def check_deal_access(db: Session, user: User, deal_id: UUID) -> Deal:
    """Check if user has access to deal and return deal if accessible"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    if user.role != UserRole.ADMIN.value:
        is_member = db.query(DealMember).filter(
            DealMember.deal_id == deal_id,
            DealMember.user_id == user.id
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this deal"
            )

    return deal


async def run_agent_in_background(
    agent_type: AgentType,
    run_id: UUID,
    input_data: dict,
    user_id: UUID,
    deal_id: UUID
):
    """
    Background task to execute agent.
    Creates a new database session for the background task.
    """
    from datetime import datetime
    from ..core.database import SessionLocal
    from ..agents.market_research import MarketResearchAgent
    from ..agents.document_analysis import DocumentAnalysisAgent
    from ..agents.due_diligence import DueDiligenceAgent
    from ..agents.news_alerts import NewsAlertsAgent

    db = SessionLocal()
    try:
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not agent_run:
            return

        agent_run.status = AgentStatus.RUNNING
        db.commit()

        # Route to appropriate agent implementation
        if agent_type == AgentType.MARKET_RESEARCH:
            agent = MarketResearchAgent(db, user_id, deal_id)
            output = await agent.execute(input_data)
        elif agent_type == AgentType.DOCUMENT_ANALYSIS:
            agent = DocumentAnalysisAgent(db, user_id, deal_id)
            output = await agent.execute(input_data)
        elif agent_type == AgentType.DUE_DILIGENCE:
            agent = DueDiligenceAgent(db, user_id, deal_id)
            output = await agent.execute(input_data)
        elif agent_type == AgentType.NEWS_ALERTS:
            agent = NewsAlertsAgent(db, user_id, deal_id)
            output = await agent.execute(input_data)
        else:
            # Fallback mock for agents not yet implemented
            await asyncio.sleep(1)  # Simulate processing time
            output = {
                "summary": f"Analysis completed for {agent_type.value}",
                "details": {
                    "query": input_data.get("query", ""),
                    "agent_type": agent_type.value
                },
                "sources": []
            }

        agent_run.status = AgentStatus.COMPLETED
        agent_run.output = output
        agent_run.completed_at = datetime.utcnow()
        db.commit()

        # Add assistant message with the summary
        assistant_message = AgentMessage(
            agent_run_id=agent_run.id,
            role="assistant",
            content=output.get("summary", str(output)),
            created_at=datetime.utcnow()
        )
        db.add(assistant_message)
        db.commit()

    except Exception as e:
        # Mark as failed
        agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if agent_run:
            agent_run.status = AgentStatus.FAILED
            agent_run.error_message = str(e)
            from datetime import datetime
            agent_run.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/{agent_type}/run", response_model=AgentRunStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_agent_run(
    agent_type: AgentType,
    request: AgentRunStartRequest,
    deal_id: UUID = Query(..., description="Deal ID to associate the run with"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start an agent run asynchronously.

    - **agent_type**: Type of agent to run (market_research, document_analysis, due_diligence, news_alerts)
    - **deal_id**: Deal to associate the agent run with
    - **request.query**: The query or request for the agent
    - **request.context**: Optional additional context

    Returns immediately with a run_id that can be used to poll for status.
    """
    # Check deal access
    check_deal_access(db, current_user, deal_id)

    # Build input data based on agent type
    from datetime import datetime
    input_data = {"context": request.context}
    if request.query:
        input_data["query"] = request.query
    if request.file_id:
        input_data["file_id"] = str(request.file_id)

    # Create agent run record with pending status
    agent_run = AgentRun(
        deal_id=deal_id,
        user_id=current_user.id,
        agent_type=agent_type,
        input=input_data,
        status=AgentStatus.PENDING,
        started_at=datetime.utcnow()
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)

    # Add user message
    user_message_content = request.query or f"Analyze file: {request.file_id}"
    user_message = AgentMessage(
        agent_run_id=agent_run.id,
        role="user",
        content=user_message_content,
        created_at=datetime.utcnow()
    )
    db.add(user_message)
    db.commit()

    # Schedule background execution
    if background_tasks:
        background_tasks.add_task(
            run_agent_in_background,
            agent_type,
            agent_run.id,
            input_data,
            current_user.id,
            deal_id
        )

    return AgentRunStartResponse(
        run_id=agent_run.id,
        status=agent_run.status,
        message=f"Agent {agent_type.value} run started"
    )


@router.get("/runs/{run_id}/messages", response_model=AgentMessagesResponse)
async def get_agent_run_messages(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history/messages for a specific agent run.

    User must be a deal member or admin to view the messages.
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

    messages = (
        db.query(AgentMessage)
        .filter(AgentMessage.agent_run_id == run_id)
        .order_by(AgentMessage.created_at)
        .all()
    )

    return AgentMessagesResponse(
        messages=[
            AgentMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at
            )
            for m in messages
        ],
        total=len(messages)
    )


# Alert endpoints for News & Alerts agent (feat-26)

def alert_to_response(alert: Alert) -> AlertResponse:
    """Convert Alert model to AlertResponse"""
    return AlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        deal_id=alert.deal_id,
        name=alert.name,
        keywords=alert.keywords or [],
        entities=alert.entities or [],
        frequency=alert.frequency,
        is_active=alert.is_active,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        last_checked_at=alert.last_checked_at
    )


@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    request: AlertCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new alert for news monitoring.

    - **name**: Name/description of the alert
    - **keywords**: List of keywords to monitor
    - **entities**: List of entities (companies, people) to track
    - **frequency**: How often to check (daily, weekly, immediate)
    - **deal_id**: Optional deal to associate with
    """
    # Validate at least one of keywords or entities is provided
    if not request.keywords and not request.entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of keywords or entities must be provided"
        )

    # If deal_id is provided, check access
    if request.deal_id:
        check_deal_access(db, current_user, request.deal_id)

    from datetime import datetime
    alert = Alert(
        user_id=current_user.id,
        deal_id=request.deal_id,
        name=request.name,
        keywords=request.keywords,
        entities=request.entities,
        frequency=request.frequency,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert_to_response(alert)


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    include_inactive: bool = Query(False, description="Include inactive alerts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all alerts for the current user.

    - **include_inactive**: Whether to include inactive alerts (default: false)
    """
    query = db.query(Alert).filter(Alert.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(Alert.is_active == True)

    alerts = query.order_by(Alert.created_at.desc()).all()

    return AlertListResponse(
        alerts=[alert_to_response(a) for a in alerts],
        total=len(alerts)
    )


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific alert by ID.

    User must own the alert or be an admin.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check ownership
    if alert.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    return alert_to_response(alert)


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    request: AlertUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing alert.

    User must own the alert or be an admin.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check ownership
    if alert.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    # Update fields if provided
    if request.name is not None:
        alert.name = request.name
    if request.keywords is not None:
        alert.keywords = request.keywords
    if request.entities is not None:
        alert.entities = request.entities
    if request.frequency is not None:
        alert.frequency = request.frequency
    if request.is_active is not None:
        alert.is_active = request.is_active

    from datetime import datetime
    alert.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert_to_response(alert)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert.

    User must own the alert or be an admin.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check ownership
    if alert.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    db.delete(alert)
    db.commit()

    return None


@router.get("/alerts/{alert_id}/matches", response_model=AlertMatchListResponse)
async def list_alert_matches(
    alert_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List matches for a specific alert.

    User must own the alert or be an admin.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check ownership
    if alert.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    offset = (page - 1) * page_size

    total = db.query(AlertMatch).filter(AlertMatch.alert_id == alert_id).count()
    matches = (
        db.query(AlertMatch)
        .filter(AlertMatch.alert_id == alert_id)
        .order_by(AlertMatch.matched_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return AlertMatchListResponse(
        matches=[
            AlertMatchResponse(
                id=m.id,
                alert_id=m.alert_id,
                headline=m.headline,
                source=m.source,
                url=m.url,
                snippet=m.snippet,
                published_at=m.published_at,
                sentiment=m.sentiment,
                relevance_score=None,  # Convert from UUID type in model
                keywords_matched=m.keywords_matched or [],
                notified=m.notified,
                matched_at=m.matched_at
            )
            for m in matches
        ],
        total=total
    )


async def check_alerts_background(user_id: UUID, alert_id: UUID):
    """
    Background task to check an alert for news matches.
    This runs the NewsAlertsAgent and stores any matches.
    """
    from datetime import datetime
    from ..core.database import SessionLocal
    from ..agents.news_alerts import NewsAlertsAgent

    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert or not alert.is_active:
            return

        # Find a deal to associate with (use alert's deal_id or create a dummy)
        deal_id = alert.deal_id
        if not deal_id:
            # Use user's first deal or skip if no deals
            first_deal = db.query(Deal).first()
            if not first_deal:
                return
            deal_id = first_deal.id

        # Run the news alerts agent
        agent = NewsAlertsAgent(db, user_id, deal_id)
        input_data = {
            "keywords": alert.keywords or [],
            "entities": alert.entities or [],
            "query": alert.name
        }

        try:
            output = await agent.execute(input_data)

            # Store matches
            news_items = output.get("news_items", [])
            for item in news_items:
                match = AlertMatch(
                    alert_id=alert_id,
                    headline=item.get("headline", "Unknown"),
                    source=item.get("source", "Unknown"),
                    url=item.get("url"),
                    snippet=item.get("snippet"),
                    published_at=None,  # Would need to parse date
                    sentiment=item.get("sentiment"),
                    keywords_matched=item.get("keywords_matched", []),
                    notified=False,
                    matched_at=datetime.utcnow()
                )
                db.add(match)

            # Update last_checked_at
            alert.last_checked_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            import logging
            logging.error(f"Error checking alert {alert_id}: {str(e)}")

    finally:
        db.close()


@router.post("/alerts/{alert_id}/check", status_code=status.HTTP_202_ACCEPTED)
async def trigger_alert_check(
    alert_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a check for an alert.

    User must own the alert or be an admin.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Check ownership
    if alert.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this alert"
        )

    # Schedule background check
    background_tasks.add_task(check_alerts_background, current_user.id, alert_id)

    return {"message": "Alert check started", "alert_id": str(alert_id)}
