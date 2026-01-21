"""
Base agent class for AI-powered research and analysis
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..models.agent import AgentRun, AgentMessage, AgentStatus, AgentType, MessageRole

logger = logging.getLogger(__name__)


class AgentInput(BaseModel):
    """Base input schema for agents"""
    query: str = Field(..., description="The query or request for the agent")
    context: Optional[dict] = Field(default=None, description="Additional context for the agent")


class AgentOutput(BaseModel):
    """Base output schema for agents"""
    summary: str = Field(..., description="Brief summary of the agent's findings")
    details: dict = Field(default_factory=dict, description="Detailed findings")
    sources: list[str] = Field(default_factory=list, description="Sources consulted")


class BaseAgent(ABC):
    """
    Abstract base class for all research agents.

    Provides:
    - Async execution pattern with status tracking
    - Error handling with retry logic (max 3 attempts)
    - Message history for chat-style interactions
    - Database persistence of results
    """

    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2

    def __init__(self, db: Session, user_id: UUID, deal_id: UUID):
        """
        Initialize agent with database session and context.

        Args:
            db: SQLAlchemy database session
            user_id: ID of the user running the agent
            deal_id: ID of the deal this agent run is associated with
        """
        self.db = db
        self.user_id = user_id
        self.deal_id = deal_id
        self.settings = get_settings()
        self._current_run: Optional[AgentRun] = None

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return the agent type enum value"""
        pass

    @abstractmethod
    async def execute(self, input_data: dict) -> dict:
        """
        Execute the agent's main logic.

        Args:
            input_data: The input parameters for the agent

        Returns:
            dict: The agent's output/results

        Raises:
            Exception: If the agent fails to complete its task
        """
        pass

    async def run(self, input_data: dict) -> AgentRun:
        """
        Run the agent with full lifecycle management.

        Creates a new AgentRun, executes with retry logic,
        and persists results to the database.

        Args:
            input_data: The input parameters for the agent

        Returns:
            AgentRun: The completed (or failed) agent run record
        """
        # Create the agent run record
        agent_run = AgentRun(
            deal_id=self.deal_id,
            user_id=self.user_id,
            agent_type=self.agent_type,
            input=input_data,
            status=AgentStatus.PENDING,
            started_at=datetime.utcnow()
        )
        self.db.add(agent_run)
        self.db.commit()
        self.db.refresh(agent_run)
        self._current_run = agent_run

        # Log the user's input as a message
        self._add_message(MessageRole.USER, str(input_data.get("query", input_data)))

        # Update status to running
        agent_run.status = AgentStatus.RUNNING
        self.db.commit()

        # Execute with retry logic
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"Agent {self.agent_type.value} attempt {attempt}/{self.MAX_RETRIES}")
                output = await self.execute(input_data)

                # Success - update run with output
                agent_run.status = AgentStatus.COMPLETED
                agent_run.output = output
                agent_run.completed_at = datetime.utcnow()
                self.db.commit()

                # Log the agent's response as a message
                summary = output.get("summary", str(output))
                self._add_message(MessageRole.ASSISTANT, summary)

                logger.info(f"Agent {self.agent_type.value} completed successfully")
                return agent_run

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Agent {self.agent_type.value} attempt {attempt} failed: {str(e)}"
                )
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS * attempt)

        # All retries failed
        agent_run.status = AgentStatus.FAILED
        agent_run.error_message = str(last_error)
        agent_run.completed_at = datetime.utcnow()
        self.db.commit()

        # Log the error as a system message
        self._add_message(
            MessageRole.SYSTEM,
            f"Agent failed after {self.MAX_RETRIES} attempts: {str(last_error)}"
        )

        logger.error(f"Agent {self.agent_type.value} failed: {str(last_error)}")
        return agent_run

    def _add_message(self, role: MessageRole, content: str) -> AgentMessage:
        """
        Add a message to the agent run's chat history.

        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content

        Returns:
            AgentMessage: The created message record
        """
        if not self._current_run:
            raise RuntimeError("Cannot add message without an active agent run")

        message = AgentMessage(
            agent_run_id=self._current_run.id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        return message

    def get_messages(self) -> list[AgentMessage]:
        """
        Get all messages for the current agent run.

        Returns:
            list[AgentMessage]: All messages in chronological order
        """
        if not self._current_run:
            return []

        return (
            self.db.query(AgentMessage)
            .filter(AgentMessage.agent_run_id == self._current_run.id)
            .order_by(AgentMessage.created_at)
            .all()
        )

    @staticmethod
    def get_run_status(db: Session, run_id: UUID) -> Optional[AgentRun]:
        """
        Get the current status of an agent run.

        Args:
            db: Database session
            run_id: The ID of the agent run

        Returns:
            AgentRun if found, None otherwise
        """
        return db.query(AgentRun).filter(AgentRun.id == run_id).first()

    @staticmethod
    def get_run_messages(db: Session, run_id: UUID) -> list[AgentMessage]:
        """
        Get all messages for an agent run.

        Args:
            db: Database session
            run_id: The ID of the agent run

        Returns:
            list[AgentMessage]: All messages in chronological order
        """
        return (
            db.query(AgentMessage)
            .filter(AgentMessage.agent_run_id == run_id)
            .order_by(AgentMessage.created_at)
            .all()
        )
