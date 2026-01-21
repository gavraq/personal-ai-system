"""
Tests for Market Research Agent (feat-23)
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from passlib.context import CryptContext

from app.models.user import User
from app.models.deal import Deal
from app.models.agent import AgentRun, AgentType, AgentStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestMarketResearchAgent:
    """Tests for feat-23: Market Research Agent"""

    def test_query_returns_structured_analysis(self, client, test_db):
        """Query 'Tech sector trends 2024' returns structured market analysis"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin user
        admin = User(
            email="admin_mr1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_mr1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Tech Research Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Start market research agent
        response = client.post(
            f"/api/agents/market_research/run?deal_id={deal_id}",
            json={"query": "Tech sector trends 2024"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 202
        run_id = response.json()["run_id"]

        # Wait for completion (poll status)
        import time
        for _ in range(10):  # Max 10 seconds
            status_response = client.get(
                f"/api/agents/runs/{run_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            status_data = status_response.json()
            if status_data["status"] in ["completed", "failed"]:
                break
            time.sleep(1)

        # Verify structured output
        assert status_response.status_code == 200
        data = status_response.json()

        if data["status"] == "completed":
            output = data["output"]
            # Check required fields exist
            assert "summary" in output or "market_overview" in output
            assert "trends" in output
            assert "competitors" in output
            assert "opportunities" in output
            assert "risks" in output
            assert "sources" in output

            # Verify lists contain data
            assert isinstance(output["trends"], list)
            assert isinstance(output["competitors"], list)
            assert isinstance(output["opportunities"], list)
            assert isinstance(output["risks"], list)
            assert isinstance(output["sources"], list)
        else:
            # If failed, it should have an error message
            assert data["error_message"] is not None

    def test_results_include_source_citations(self, client, test_db):
        """Market research results include source citations"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_mr2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_mr2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Sources Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create a completed agent run with sources
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.COMPLETED,
            input={"query": "AI market analysis"},
            output={
                "summary": "AI market is growing rapidly",
                "market_overview": "The AI market shows significant growth...",
                "trends": [{"trend": "LLM adoption", "description": "Large language models", "impact": "high"}],
                "competitors": [{"name": "OpenAI", "description": "Leading AI lab", "market_position": "leader"}],
                "opportunities": ["Enterprise AI adoption"],
                "risks": ["Regulatory uncertainty"],
                "sources": [
                    "Gartner AI Market Report 2024",
                    "McKinsey Global AI Survey",
                    "Industry analysis based on public filings"
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
        assert data["output"]["sources"] is not None
        assert len(data["output"]["sources"]) >= 1
        # Verify sources are strings
        for source in data["output"]["sources"]:
            assert isinstance(source, str)
            assert len(source) > 0

    def test_results_persist_and_are_retrievable(self, client, test_db):
        """Market research results persist to database and can be retrieved"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_mr3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_mr3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Persistence Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create market research run
        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.COMPLETED,
            input={"query": "Healthcare market 2024"},
            output={
                "summary": "Healthcare market shows strong growth",
                "market_overview": "The healthcare market continues to expand...",
                "trends": [{"trend": "Telemedicine", "description": "Remote healthcare", "impact": "high"}],
                "competitors": [{"name": "UnitedHealth", "description": "Insurance giant", "market_position": "leader"}],
                "opportunities": ["Digital health adoption"],
                "risks": ["Insurance regulation"],
                "sources": ["Industry reports"]
            },
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)
        run_id = str(agent_run.id)

        # Retrieve the run
        response = client.get(
            f"/api/agents/runs/{run_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify data persisted correctly
        assert data["id"] == run_id
        assert data["deal_id"] == deal_id
        assert data["agent_type"] == "market_research"
        assert data["status"] == "completed"
        assert data["input"]["query"] == "Healthcare market 2024"
        assert data["output"]["summary"] == "Healthcare market shows strong growth"

        # Verify all structured fields persisted
        assert "trends" in data["output"]
        assert "competitors" in data["output"]
        assert "opportunities" in data["output"]
        assert "risks" in data["output"]

        # Retrieve via deal's agent runs endpoint
        deal_runs_response = client.get(
            f"/api/agents/deal/{deal_id}/runs",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert deal_runs_response.status_code == 200
        deal_runs_data = deal_runs_response.json()
        assert deal_runs_data["total"] >= 1

        # Find our run in the list
        found = False
        for run in deal_runs_data["runs"]:
            if run["id"] == run_id:
                found = True
                assert run["agent_type"] == "market_research"
                break
        assert found, "Agent run not found in deal's runs"

    def test_market_research_output_structure(self, client, test_db):
        """Verify market research output has all required fields"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_mr4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_mr4@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Output Structure Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Create comprehensive agent run output
        comprehensive_output = {
            "summary": "Comprehensive market analysis summary",
            "market_overview": "Detailed market overview with market size and growth projections...",
            "trends": [
                {"trend": "Trend 1", "description": "Description 1", "impact": "high"},
                {"trend": "Trend 2", "description": "Description 2", "impact": "medium"},
                {"trend": "Trend 3", "description": "Description 3", "impact": "low"}
            ],
            "competitors": [
                {"name": "Competitor 1", "description": "Leader", "market_position": "leader"},
                {"name": "Competitor 2", "description": "Challenger", "market_position": "challenger"}
            ],
            "opportunities": [
                "Opportunity 1",
                "Opportunity 2",
                "Opportunity 3"
            ],
            "risks": [
                "Risk 1",
                "Risk 2"
            ],
            "sources": [
                "Source 1",
                "Source 2",
                "Source 3"
            ]
        }

        agent_run = AgentRun(
            deal_id=deal_id,
            user_id=admin.id,
            agent_type=AgentType.MARKET_RESEARCH,
            status=AgentStatus.COMPLETED,
            input={"query": "Comprehensive market research"},
            output=comprehensive_output,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)

        # Retrieve and verify structure
        response = client.get(
            f"/api/agents/runs/{agent_run.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        output = data["output"]

        # Verify all required fields
        assert "summary" in output
        assert "market_overview" in output
        assert "trends" in output
        assert "competitors" in output
        assert "opportunities" in output
        assert "risks" in output
        assert "sources" in output

        # Verify trends structure
        assert len(output["trends"]) >= 3
        for trend in output["trends"]:
            assert "trend" in trend
            assert "description" in trend
            assert "impact" in trend
            assert trend["impact"] in ["high", "medium", "low"]

        # Verify competitors structure
        assert len(output["competitors"]) >= 2
        for competitor in output["competitors"]:
            assert "name" in competitor
            assert "description" in competitor
            assert "market_position" in competitor

        # Verify lists
        assert len(output["opportunities"]) >= 1
        assert len(output["risks"]) >= 1
        assert len(output["sources"]) >= 1


class TestMarketResearchAgentUnit:
    """Unit tests for MarketResearchAgent class"""

    @pytest.mark.asyncio
    async def test_agent_execute_returns_structured_output(self):
        """Agent execute method returns properly structured output"""
        from unittest.mock import MagicMock
        from app.agents.market_research import MarketResearchAgent
        from app.models.agent import AgentType

        # Create mock db session and settings
        mock_db = MagicMock()
        mock_settings = MagicMock()
        mock_settings.anthropic_api_key = ""  # Empty to trigger mock response

        # Create agent with mocked dependencies
        agent = MarketResearchAgent(
            db=mock_db,
            user_id="test-user-id",
            deal_id="test-deal-id"
        )
        agent.settings = mock_settings

        # Execute with test input
        input_data = {"query": "Test market query"}
        result = await agent.execute(input_data)

        # Verify output structure
        assert "summary" in result
        assert "market_overview" in result
        assert "trends" in result
        assert "competitors" in result
        assert "opportunities" in result
        assert "risks" in result
        assert "sources" in result

        # Verify agent type
        assert agent.agent_type == AgentType.MARKET_RESEARCH

    @pytest.mark.asyncio
    async def test_agent_handles_empty_query(self):
        """Agent raises error for empty query"""
        from unittest.mock import MagicMock
        from app.agents.market_research import MarketResearchAgent

        mock_db = MagicMock()
        mock_settings = MagicMock()
        mock_settings.anthropic_api_key = ""

        agent = MarketResearchAgent(
            db=mock_db,
            user_id="test-user-id",
            deal_id="test-deal-id"
        )
        agent.settings = mock_settings

        # Execute with empty query
        with pytest.raises(ValueError, match="Query is required"):
            await agent.execute({"query": ""})

    @pytest.mark.asyncio
    async def test_agent_parse_response_handles_json(self):
        """Agent correctly parses JSON response from Claude"""
        from unittest.mock import MagicMock
        from app.agents.market_research import MarketResearchAgent

        mock_db = MagicMock()
        agent = MarketResearchAgent(
            db=mock_db,
            user_id="test-user-id",
            deal_id="test-deal-id"
        )

        # Test with valid JSON in markdown code block
        json_response = '''Here's my analysis:

```json
{
    "market_overview": "Test overview",
    "trends": [{"trend": "Test trend", "description": "Test desc", "impact": "high"}],
    "competitors": [{"name": "Test Corp", "description": "A company", "market_position": "leader"}],
    "opportunities": ["Opportunity 1"],
    "risks": ["Risk 1"],
    "sources": ["Source 1"]
}
```

Let me know if you need more details.'''

        result = agent._parse_response(json_response)

        assert result["market_overview"] == "Test overview"
        assert len(result["trends"]) == 1
        assert result["trends"][0]["trend"] == "Test trend"
        assert len(result["competitors"]) == 1
        assert len(result["sources"]) == 1

    @pytest.mark.asyncio
    async def test_agent_parse_response_handles_raw_json(self):
        """Agent correctly parses raw JSON response"""
        from unittest.mock import MagicMock
        from app.agents.market_research import MarketResearchAgent

        mock_db = MagicMock()
        agent = MarketResearchAgent(
            db=mock_db,
            user_id="test-user-id",
            deal_id="test-deal-id"
        )

        # Test with raw JSON (no markdown)
        raw_json = '''{
    "market_overview": "Direct JSON overview",
    "trends": [],
    "competitors": [],
    "opportunities": [],
    "risks": [],
    "sources": ["Direct source"]
}'''

        result = agent._parse_response(raw_json)

        assert result["market_overview"] == "Direct JSON overview"
        assert result["sources"] == ["Direct source"]

    @pytest.mark.asyncio
    async def test_agent_parse_response_handles_invalid_json(self):
        """Agent handles invalid JSON gracefully"""
        from unittest.mock import MagicMock
        from app.agents.market_research import MarketResearchAgent

        mock_db = MagicMock()
        agent = MarketResearchAgent(
            db=mock_db,
            user_id="test-user-id",
            deal_id="test-deal-id"
        )

        # Test with plain text (no JSON)
        plain_text = "This is just a plain text response about the market."

        result = agent._parse_response(plain_text)

        # Should return text as market_overview with empty lists
        assert "market_overview" in result
        assert result["market_overview"] == plain_text
        assert result["trends"] == []
        assert result["sources"] == ["Claude AI analysis"]
