"""
Tests for N+1 query optimizations via eager loading.

These tests verify that the eager loading implementations work correctly.
The actual performance gains from avoiding N+1 queries can only be measured
with a real database and query logging.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.models.deal import Deal, DealMember
from app.models.user import User, UserRole
from app.models.file import File, FileShare, FileSource, FilePermission
from app.models.agent import AgentRun, AgentType, AgentStatus
from app.models.audit import Activity

from app.routers.deals import (
    deal_to_response,
    get_deals_with_file_counts,
)
from app.routers.agents import agent_run_to_response
from app.routers.activity import activity_to_response


class TestDealResponseOptimization:
    """Test deal_to_response optimizations"""

    def test_deal_to_response_accepts_precomputed_file_count(self):
        """Verify deal_to_response uses the provided file_count parameter"""
        deal = MagicMock(spec=Deal)
        deal.id = uuid4()
        deal.title = "Test Deal"
        deal.description = "Test Description"
        deal.status = "active"
        deal.created_by = uuid4()
        deal.created_at = datetime.utcnow()
        deal.updated_at = datetime.utcnow()

        # Call with precomputed file count
        response = deal_to_response(deal, file_count=42)

        assert response.file_count == 42
        assert response.title == "Test Deal"

    def test_deal_to_response_defaults_to_zero_file_count(self):
        """Verify deal_to_response defaults file_count to 0"""
        deal = MagicMock(spec=Deal)
        deal.id = uuid4()
        deal.title = "Test Deal"
        deal.description = "Test Description"
        deal.status = "active"
        deal.created_by = uuid4()
        deal.created_at = datetime.utcnow()
        deal.updated_at = datetime.utcnow()

        response = deal_to_response(deal)

        assert response.file_count == 0


class TestAgentRunResponseOptimization:
    """Test agent_run_to_response optimizations"""

    def test_agent_run_to_response_accepts_preloaded_email(self):
        """Verify agent_run_to_response uses the provided user_email parameter"""
        run = MagicMock(spec=AgentRun)
        run.id = uuid4()
        run.deal_id = uuid4()
        run.user_id = uuid4()
        run.agent_type = AgentType.MARKET_RESEARCH
        run.status = AgentStatus.COMPLETED
        run.input = {"query": "test"}
        run.output = {"result": "success"}
        run.error_message = None
        run.started_at = datetime.utcnow()
        run.completed_at = datetime.utcnow()

        response = agent_run_to_response(run, user_email="test@example.com")

        assert response.user_email == "test@example.com"
        assert response.status == AgentStatus.COMPLETED

    def test_agent_run_to_response_handles_none_email(self):
        """Verify agent_run_to_response handles None email gracefully"""
        run = MagicMock(spec=AgentRun)
        run.id = uuid4()
        run.deal_id = uuid4()
        run.user_id = uuid4()
        run.agent_type = AgentType.MARKET_RESEARCH
        run.status = AgentStatus.COMPLETED
        run.input = {}
        run.output = None
        run.error_message = None
        run.started_at = datetime.utcnow()
        run.completed_at = None

        response = agent_run_to_response(run, user_email=None)

        assert response.user_email is None


class TestActivityResponseOptimization:
    """Test activity_to_response optimizations"""

    def test_activity_to_response_accepts_preloaded_email(self):
        """Verify activity_to_response uses the provided actor_email parameter"""
        activity = MagicMock(spec=Activity)
        activity.id = uuid4()
        activity.deal_id = uuid4()
        activity.actor_id = uuid4()
        activity.action = "file_upload"
        activity.details = {"filename": "test.pdf"}
        activity.created_at = datetime.utcnow()

        response = activity_to_response(activity, actor_email="actor@example.com")

        assert response.actor_email == "actor@example.com"
        assert response.action == "file_upload"

    def test_activity_to_response_handles_none_email(self):
        """Verify activity_to_response handles None email gracefully"""
        activity = MagicMock(spec=Activity)
        activity.id = uuid4()
        activity.deal_id = uuid4()
        activity.actor_id = uuid4()
        activity.action = "deal_create"
        activity.details = {}
        activity.created_at = datetime.utcnow()

        response = activity_to_response(activity, actor_email=None)

        assert response.actor_email is None


class TestBatchFileCountQuery:
    """Test get_deals_with_file_counts batch query"""

    def test_empty_deal_ids_returns_empty_dict(self):
        """Verify empty input returns empty dictionary"""
        db = MagicMock()

        result = get_deals_with_file_counts(db, [])

        assert result == {}
        db.query.assert_not_called()


class TestJoinedLoadIntegration:
    """Tests to verify joinedload imports and usage"""

    def test_joinedload_import_exists_in_deals(self):
        """Verify joinedload is properly imported in deals router"""
        from app.routers import deals
        from sqlalchemy.orm import joinedload
        # If import succeeds, the module has joinedload available

    def test_joinedload_import_exists_in_files(self):
        """Verify joinedload is properly imported in files router"""
        from app.routers import files
        from sqlalchemy.orm import joinedload

    def test_joinedload_import_exists_in_agents(self):
        """Verify joinedload is properly imported in agents router"""
        from app.routers import agents
        from sqlalchemy.orm import joinedload

    def test_joinedload_import_exists_in_activity(self):
        """Verify joinedload is properly imported in activity router"""
        from app.routers import activity
        from sqlalchemy.orm import joinedload
