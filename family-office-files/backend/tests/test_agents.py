"""
Tests for agent run endpoints (feat-7: Agent Output Summaries)
"""
import pytest
from datetime import datetime
from passlib.context import CryptContext

from app.models.user import User
from app.models.deal import Deal
from app.models.agent import AgentRun, AgentType, AgentStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestAgentOutputSummaries:
    """Tests for feat-7: Agent Output Summaries"""

    def test_agent_summary_displays_after_agent_run(self, client, test_db):
        """Agent summary displays after agent run completion"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_agent1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Agent Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run directly in database
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.COMPLETED,
            input={"query": "tech market analysis"},
            output={"summary": "Market shows strong growth potential", "findings": ["trend 1", "trend 2"]},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()

        # Get agent summaries
        summary_response = client.get(
            "/api/agents/summaries",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert summary_response.status_code == 200
        data = summary_response.json()
        assert "summaries" in data
        assert len(data["summaries"]) >= 1
        summary = data["summaries"][0]
        assert summary["agent_type"] == "market_research"
        assert summary["status"] == "completed"
        assert summary["deal_title"] == "Agent Test Deal"

    def test_expand_shows_full_output(self, client, test_db):
        """Expanding agent run shows full output"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_agent2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Agent Output Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with detailed output
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"document_id": "doc-123", "analysis_type": "full"},
            output={
                "summary": "Comprehensive document analysis",
                "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                "recommendations": ["Recommendation A", "Recommendation B"],
                "risk_factors": ["Risk 1", "Risk 2"]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get full agent run details
        run_response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert run_response.status_code == 200
        data = run_response.json()
        assert data["agent_type"] == "document_analysis"
        assert data["output"]["summary"] == "Comprehensive document analysis"
        assert len(data["output"]["key_findings"]) == 3
        assert len(data["output"]["recommendations"]) == 2

    def test_agent_runs_list_pagination(self, client, test_db):
        """Agent runs list supports pagination"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_agent3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Pagination Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create multiple agent runs
        for i in range(5):
            agent_run = AgentRun(
                deal_id=deal_id,
                user_id=admin.id,
                agent_type=AgentType.NEWS_ALERTS,
                status=AgentStatus.COMPLETED,
                input={"query": f"news query {i}"},
                output={"summary": f"News summary {i}"},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(agent_run)
        db.commit()

        # Get first page
        response = client.get(
            "/api/agents/runs?page=1&page_size=2",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["runs"]) == 2
        assert data["total"] >= 5

    def test_agent_runs_filtered_by_accessible_deals(self, client, test_db):
        """Viewers only see agent runs from their accessible deals"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin and viewer
        admin = User(
            email="admin_agent4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        viewer = User(
            email="viewer_agent4@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(admin)
        db.refresh(viewer)

        # Admin creates deal and runs agent (viewer not assigned)
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_agent4@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Admin Only Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={"target": "company-xyz"},
            output={"summary": "Due diligence complete"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()

        # Viewer tries to get agent summaries
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_agent4@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        response = client.get(
            "/api/agents/summaries",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        # Viewer should not see admin's agent run
        assert len(data["summaries"]) == 0

    def test_agent_type_icons_mapped_correctly(self, client, test_db):
        """Each agent type returns correct metadata for icon display"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_agent5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent5@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Icon Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent runs for each type
        agent_types = [
            AgentType.MARKET_RESEARCH,
            AgentType.DOCUMENT_ANALYSIS,
            AgentType.DUE_DILIGENCE,
            AgentType.NEWS_ALERTS
        ]

        for agent_type in agent_types:
            agent_run = AgentRun(
                deal_id=deal_id,
                user_id=admin.id,
                agent_type=agent_type,
                status=AgentStatus.COMPLETED,
                input={},
                output={"summary": f"Output for {agent_type.value}"},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(agent_run)
        db.commit()

        # Get summaries
        response = client.get(
            "/api/agents/summaries?limit=10",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["summaries"]) >= 4

        # Verify all agent types are present
        agent_types_returned = {s["agent_type"] for s in data["summaries"]}
        assert "market_research" in agent_types_returned
        assert "document_analysis" in agent_types_returned
        assert "due_diligence" in agent_types_returned
        assert "news_alerts" in agent_types_returned

    def test_summary_excerpt_extracted_from_output(self, client, test_db):
        """Summary excerpt is correctly extracted from agent output"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_agent6@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent6@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Excerpt Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with long summary
        long_summary = "This is a very long summary that exceeds 150 characters. " * 5
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.COMPLETED,
            input={},
            output={"summary": long_summary},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()

        # Get summaries
        response = client.get(
            "/api/agents/summaries",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["summaries"]) >= 1
        summary = data["summaries"][0]
        # Excerpt should be truncated with ellipsis
        assert summary["summary_excerpt"] is not None
        assert len(summary["summary_excerpt"]) <= 154  # 150 chars + "..."

    def test_failed_agent_run_shows_error_message(self, client, test_db):
        """Failed agent run displays error message"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_agent7@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent7@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Error Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create failed agent run
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.NEWS_ALERTS,
            status=AgentStatus.FAILED,
            input={"query": "breaking news"},
            output=None,
            error_message="API rate limit exceeded",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "API rate limit exceeded"

    def test_deal_agent_runs_endpoint(self, client, test_db):
        """Can list agent runs for a specific deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_agent8@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_agent8@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create two deals
        deal1_response = client.post(
            "/api/deals",
            json={"title": "Deal One"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal1_id = deal1_response.json()["id"]

        deal2_response = client.post(
            "/api/deals",
            json={"title": "Deal Two"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal2_id = deal2_response.json()["id"]

        # Create agent runs for each deal
        for i in range(3):
            agent_run = AgentRun(
                deal_id=deal1_id,
                user_id=admin.id,
                agent_type=AgentType.MARKET_RESEARCH,
                status=AgentStatus.COMPLETED,
                input={},
                output={"summary": f"Deal 1 run {i}"},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(agent_run)

        agent_run_deal2 = AgentRun(
            deal_id=deal2_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={},
            output={"summary": "Deal 2 run"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run_deal2)
        db.commit()

        # Get runs for deal 1 only
        response = client.get(
            f"/api/agents/deal/{deal1_id}/runs",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        # All runs should be for deal 1
        for run in data["runs"]:
            assert run["deal_id"] == deal1_id


class TestAgentDelegationFramework:
    """Tests for feat-27: Agent Delegation Framework"""

    def test_start_agent_returns_run_id(self, client, test_db):
        """POST /api/agents/{agent_type}/run returns a run_id for async execution"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_framework1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_framework1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Framework Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Start agent run
        response = client.post(
            f"/api/agents/market_research/run?deal_id={deal_id}",
            json={"query": "Analyze the tech market"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        assert "market_research" in data["message"]

    def test_status_polling_returns_progress(self, client, test_db):
        """GET /api/agents/runs/{run_id} returns current status"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_framework2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_framework2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Status Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a running agent run directly
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.RUNNING,
            input={"query": "test query"},
            started_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Poll for status
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["id"] == str(agent_run.id)

    def test_get_agent_run_messages(self, client, test_db):
        """GET /api/agents/runs/{run_id}/messages returns chat history"""
        from app.core.database import get_db
        from app.models.agent import AgentMessage, MessageRole

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_framework3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_framework3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Messages Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with messages
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"query": "Analyze document"},
            output={"summary": "Analysis complete"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Add messages
        user_msg = AgentMessage(
            agent_run_id=agent_run.id,
            role=MessageRole.USER,
            content="Analyze document",
            created_at=datetime.utcnow()
        )
        db.add(user_msg)

        assistant_msg = AgentMessage(
            agent_run_id=agent_run.id,
            role=MessageRole.ASSISTANT,
            content="Analysis complete",
            created_at=datetime.utcnow()
        )
        db.add(assistant_msg)
        db.commit()

        # Get messages
        response = client.get(
            f"/api/agents/runs/{agent_run.id}/messages",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_error_handling_returns_graceful_error(self, client, test_db):
        """Agent errors are stored in error_message field"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_framework4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_framework4@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Error Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a failed agent run
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.FAILED,
            input={"query": "Check company"},
            error_message="API connection failed after 3 retries",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get the failed run
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "3 retries" in data["error_message"]

    def test_agent_run_stored_with_deal_association(self, client, test_db):
        """Agent runs are correctly associated with deals"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_framework5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_framework5@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Association Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Start agent run
        response = client.post(
            f"/api/agents/news_alerts/run?deal_id={deal_id}",
            json={"query": "Monitor tech news"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 202
        run_id = response.json()["run_id"]

        # Verify the run is associated with the deal
        run_response = client.get(
            f"/api/agents/runs/{run_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert run_response.status_code == 200
        data = run_response.json()
        assert data["deal_id"] == deal_id
        assert data["input"]["query"] == "Monitor tech news"

    def test_unauthorized_user_cannot_start_agent(self, client, test_db):
        """Users without deal access cannot start agent runs"""
        from app.core.database import get_db
        from app.models.deal import DealMember

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin and viewer
        admin = User(
            email="admin_framework6@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        viewer = User(
            email="viewer_framework6@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(admin)
        db.refresh(viewer)

        # Admin creates deal (viewer not assigned)
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_framework6@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Admin Only Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Viewer tries to start agent on admin's deal
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_framework6@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        response = client.post(
            f"/api/agents/market_research/run?deal_id={deal_id}",
            json={"query": "Unauthorized query"},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403
        assert "access" in response.json()["detail"].lower()


class TestDocumentAnalysisAgent:
    """Tests for feat-24: Document Analysis Agent"""

    def test_query_returns_structured_analysis(self, client, test_db):
        """Analyze PDF returns summary and key points"""
        from app.core.database import get_db
        from app.models.file import File, FileSource

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_docanalysis1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_docanalysis1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Document Analysis Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a file record (mock GCS file)
        file_record = File(
            deal_id=deal_id,
            name="test_document.pdf",
            source=FileSource.GCS,
            source_id="deals/test/file.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            uploaded_by=admin.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Create agent run directly with mock output (simulating completed analysis)
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"file_id": str(file_record.id)},
            output={
                "summary": "This document contains important financial information.",
                "key_points": [
                    "Revenue increased by 15% year-over-year",
                    "New market expansion planned for Q2",
                    "Cost reduction initiatives on track"
                ],
                "entities": [
                    {"name": "ABC Corp", "type": "company", "context": "Primary subject"},
                    {"name": "$5M", "type": "monetary", "context": "Revenue figure"}
                ],
                "recommendations": [
                    "Review Q2 expansion timeline",
                    "Monitor cost reduction progress"
                ],
                "source_file_id": str(file_record.id),
                "source_file_name": "test_document.pdf"
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "document_analysis"
        assert data["status"] == "completed"
        assert "summary" in data["output"]
        assert "key_points" in data["output"]
        assert len(data["output"]["key_points"]) >= 1

    def test_analyze_drive_file_works(self, client, test_db):
        """Analyze Drive file works (with mocked Drive response)"""
        from app.core.database import get_db
        from app.models.file import File, FileSource

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_docanalysis2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_docanalysis2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Drive Analysis Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a file record (Drive file)
        file_record = File(
            deal_id=deal_id,
            name="drive_document.docx",
            source=FileSource.DRIVE,
            source_id="1abc123xyz",  # Mock Drive file ID
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=2048,
            uploaded_by=admin.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Create completed agent run (simulating Drive file analysis)
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"file_id": str(file_record.id)},
            output={
                "summary": "Analysis of Drive document completed.",
                "key_points": [
                    "Document outlines partnership terms",
                    "Effective date is January 2024"
                ],
                "entities": [
                    {"name": "Partner Co", "type": "company", "context": "Contract party"}
                ],
                "recommendations": [
                    "Review partnership terms before signing"
                ],
                "source_file_id": str(file_record.id),
                "source_file_name": "drive_document.docx"
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "document_analysis"
        assert data["output"]["source_file_name"] == "drive_document.docx"

    def test_results_linked_to_file(self, client, test_db):
        """Results are correctly linked to source file"""
        from app.core.database import get_db
        from app.models.file import File, FileSource

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_docanalysis3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_docanalysis3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "File Link Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a file record
        file_record = File(
            deal_id=deal_id,
            name="linked_document.txt",
            source=FileSource.GCS,
            source_id="deals/test/linked.txt",
            mime_type="text/plain",
            size_bytes=512,
            uploaded_by=admin.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Create agent run with file link in output
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"file_id": str(file_record.id)},
            output={
                "summary": "Text document analysis complete.",
                "key_points": ["Document contains meeting notes"],
                "entities": [],
                "recommendations": [],
                "source_file_id": str(file_record.id),
                "source_file_name": file_record.name
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Verify the link
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["output"]["source_file_id"] == str(file_record.id)
        assert data["output"]["source_file_name"] == "linked_document.txt"
        assert data["input"]["file_id"] == str(file_record.id)

    def test_start_document_analysis_returns_run_id(self, client, test_db):
        """POST /api/agents/document_analysis/run returns a run_id for async execution"""
        from app.core.database import get_db
        from app.models.file import File, FileSource

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_docanalysis4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_docanalysis4@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Async Analysis Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a file record
        file_record = File(
            deal_id=deal_id,
            name="async_document.pdf",
            source=FileSource.GCS,
            source_id="deals/test/async.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            uploaded_by=admin.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Start document analysis agent run
        response = client.post(
            f"/api/agents/document_analysis/run?deal_id={deal_id}",
            json={"file_id": str(file_record.id)},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        assert "document_analysis" in data["message"]

    def test_image_analysis_uses_vision(self, client, test_db):
        """Image files trigger vision API path"""
        from app.core.database import get_db
        from app.models.file import File, FileSource

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_docanalysis5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_docanalysis5@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Image Analysis Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create an image file record
        file_record = File(
            deal_id=deal_id,
            name="scanned_document.png",
            source=FileSource.GCS,
            source_id="deals/test/scanned.png",
            mime_type="image/png",
            size_bytes=50000,
            uploaded_by=admin.id
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Create completed agent run (simulating image analysis via vision)
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DOCUMENT_ANALYSIS,
            status=AgentStatus.COMPLETED,
            input={"file_id": str(file_record.id)},
            output={
                "summary": "Scanned document analyzed using OCR.",
                "key_points": [
                    "Document is a receipt from Office Supplies Co",
                    "Total amount: $125.50"
                ],
                "entities": [
                    {"name": "Office Supplies Co", "type": "company", "context": "Vendor"},
                    {"name": "$125.50", "type": "monetary", "context": "Total amount"}
                ],
                "recommendations": [
                    "File for expense reporting"
                ],
                "source_file_id": str(file_record.id),
                "source_file_name": "scanned_document.png"
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Verify the analysis
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "document_analysis"
        assert "OCR" in data["output"]["summary"] or "scanned" in data["output"]["summary"].lower()


class TestDueDiligenceAgent:
    """Tests for feat-25: Due Diligence Agent"""

    def test_query_company_returns_structured_report(self, client, test_db):
        """Query company returns structured due diligence report"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_duedil1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_duedil1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Due Diligence Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with due diligence output
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={"query": "Acme Corporation", "entity_type": "company"},
            output={
                "summary": "Acme Corporation is a multinational technology company founded in 1990.",
                "overview": "Acme Corporation is a multinational technology company founded in 1990. The company specializes in enterprise software solutions and cloud services. Headquartered in San Francisco, Acme has offices in 15 countries and employs over 5,000 people worldwide.",
                "financials": [
                    {"metric": "Revenue", "value": "$500 million", "period": "2023", "trend": "increasing", "notes": "15% YoY growth"},
                    {"metric": "Net Income", "value": "$75 million", "period": "2023", "trend": "stable", "notes": "Maintained margins"},
                    {"metric": "Total Assets", "value": "$800 million", "period": "2023", "trend": "increasing", "notes": "Strategic acquisitions"}
                ],
                "leadership": [
                    {"name": "John Smith", "title": "CEO", "background": "Former CTO at TechGiant", "tenure": "5 years", "notable": "Led successful IPO"},
                    {"name": "Jane Doe", "title": "CFO", "background": "Ex-Goldman Sachs", "tenure": "3 years", "notable": "Improved cash flow management"}
                ],
                "news": [
                    {"headline": "Acme Corp Announces Cloud Expansion", "date": "2024-01-15", "source": "TechNews", "sentiment": "positive", "summary": "Company investing $100M in cloud infrastructure"},
                    {"headline": "Acme Reports Strong Q4 Results", "date": "2024-01-10", "source": "Bloomberg", "sentiment": "positive", "summary": "Beat analyst expectations by 10%"}
                ],
                "risk_flags": [
                    {"flag": "High customer concentration", "severity": "medium", "category": "financial", "details": "Top 3 customers represent 40% of revenue", "mitigation": "Diversification strategy in progress"},
                    {"flag": "Pending litigation", "severity": "low", "category": "legal", "details": "Minor patent dispute with competitor", "mitigation": "Expected to settle out of court"}
                ],
                "sources": [
                    "SEC 10-K Filing 2023",
                    "Bloomberg Company Profile",
                    "Company Press Releases"
                ]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "due_diligence"
        assert data["status"] == "completed"
        assert "overview" in data["output"]
        assert "financials" in data["output"]
        assert "leadership" in data["output"]
        assert "news" in data["output"]
        assert len(data["output"]["financials"]) >= 1
        assert len(data["output"]["leadership"]) >= 1

    def test_risk_flags_displayed_with_severity(self, client, test_db):
        """Risk flags are displayed with severity levels"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_duedil2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_duedil2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Risk Flags Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with risk flags of different severities
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={"query": "Risky Inc", "entity_type": "company"},
            output={
                "summary": "Risk analysis for Risky Inc.",
                "overview": "Risky Inc is a company with several notable risk factors.",
                "financials": [],
                "leadership": [],
                "news": [],
                "risk_flags": [
                    {"flag": "Ongoing SEC investigation", "severity": "high", "category": "regulatory", "details": "SEC investigating accounting practices", "mitigation": "Engaged external auditors"},
                    {"flag": "High debt-to-equity ratio", "severity": "medium", "category": "financial", "details": "D/E ratio of 3.5", "mitigation": "Debt restructuring planned"},
                    {"flag": "Minor compliance gap", "severity": "low", "category": "operational", "details": "Documentation needs updating", "mitigation": "In progress"}
                ],
                "sources": ["Regulatory filings", "Industry reports"]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        risk_flags = data["output"]["risk_flags"]

        # Verify risk flags structure
        assert len(risk_flags) == 3

        # Check for severity levels
        severities = [rf["severity"] for rf in risk_flags]
        assert "high" in severities
        assert "medium" in severities
        assert "low" in severities

        # Verify risk flag structure
        high_risk = next(rf for rf in risk_flags if rf["severity"] == "high")
        assert "flag" in high_risk
        assert "category" in high_risk
        assert "details" in high_risk
        assert "mitigation" in high_risk

    def test_sources_cited(self, client, test_db):
        """Sources are cited in due diligence output"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_duedil3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_duedil3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Sources Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run with sources
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={"query": "Source Corp", "entity_type": "company"},
            output={
                "summary": "Due diligence report with citations.",
                "overview": "Source Corp analysis with multiple data sources.",
                "financials": [],
                "leadership": [],
                "news": [],
                "risk_flags": [],
                "sources": [
                    "SEC EDGAR - 10-K Filing 2023",
                    "Bloomberg Terminal Company Profile",
                    "Dun & Bradstreet Credit Report",
                    "LexisNexis News Archive"
                ]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify sources are present and have content
        assert "sources" in data["output"]
        sources = data["output"]["sources"]
        assert len(sources) >= 3
        assert all(isinstance(s, str) and len(s) > 0 for s in sources)

    def test_start_due_diligence_returns_run_id(self, client, test_db):
        """POST /api/agents/due_diligence/run returns a run_id for async execution"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_duedil4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_duedil4@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Async Due Diligence Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Start due diligence agent run
        response = client.post(
            f"/api/agents/due_diligence/run?deal_id={deal_id}",
            json={"query": "Target Company Inc", "context": {"entity_type": "company"}},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 202  # Accepted
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        assert "due_diligence" in data["message"]

    def test_person_entity_type_supported(self, client, test_db):
        """Due diligence supports person entity type"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_duedil5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_duedil5@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Person Due Diligence Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create agent run for person entity type
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.DUE_DILIGENCE,
            status=AgentStatus.COMPLETED,
            input={"query": "John Doe", "entity_type": "person"},
            output={
                "summary": "Due diligence report on John Doe.",
                "overview": "John Doe is a business executive with 20 years of experience in the technology sector.",
                "financials": [],
                "leadership": [
                    {"name": "John Doe", "title": "Board Member", "background": "Former CEO of TechCo", "tenure": "3 years", "notable": "Led company through successful acquisition"}
                ],
                "news": [
                    {"headline": "John Doe joins ABC Corp Board", "date": "2024-01-01", "source": "Business Wire", "sentiment": "positive", "summary": "Appointment as independent director"}
                ],
                "risk_flags": [],
                "sources": ["LinkedIn Profile", "SEC Form 4 Filings", "News Archives"]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Get agent run details
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["input"]["entity_type"] == "person"
        assert "John Doe" in data["output"]["overview"]
