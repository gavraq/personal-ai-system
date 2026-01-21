"""
Market Research Agent for AI-powered market analysis

This agent provides market research capabilities including:
- Market overview and trends
- Competitor analysis
- Opportunities and risks
- Source citations
"""
import logging
from typing import Any, Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session

from .base import BaseAgent
from ..models.agent import AgentType

logger = logging.getLogger(__name__)


class MarketResearchOutput:
    """Structure for market research output"""

    def __init__(
        self,
        market_overview: str,
        trends: list[dict],
        competitors: list[dict],
        opportunities: list[str],
        risks: list[str],
        sources: list[str]
    ):
        self.market_overview = market_overview
        self.trends = trends
        self.competitors = competitors
        self.opportunities = opportunities
        self.risks = risks
        self.sources = sources

    def to_dict(self) -> dict:
        return {
            "summary": self.market_overview[:500] if self.market_overview else "",
            "market_overview": self.market_overview,
            "trends": self.trends,
            "competitors": self.competitors,
            "opportunities": self.opportunities,
            "risks": self.risks,
            "sources": self.sources
        }


class MarketResearchAgent(BaseAgent):
    """
    Market Research Agent for analyzing markets, sectors, and companies.

    Input: company name, sector, or market query
    Output: market_overview, trends, competitors, opportunities, risks, sources
    """

    SYSTEM_PROMPT = """You are a professional market research analyst. Your task is to provide comprehensive market analysis based on the user's query.

Provide your analysis in the following JSON structure:
{
    "market_overview": "A comprehensive overview of the market/sector/company (2-3 paragraphs)",
    "trends": [
        {"trend": "Trend name", "description": "Brief description", "impact": "high/medium/low"}
    ],
    "competitors": [
        {"name": "Company name", "description": "Brief description", "market_position": "leader/challenger/follower/niche"}
    ],
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "risks": ["Risk 1", "Risk 2"],
    "sources": ["Source 1 description", "Source 2 description"]
}

Important guidelines:
- Provide factual, well-researched information
- Be specific about market sizes, growth rates, and key players when available
- Clearly state if information is based on estimates or projections
- Include at least 3 trends, competitors, opportunities, and risks when possible
- Always provide sources for your information, even if they are general knowledge sources
- If you don't have specific data, provide reasonable estimates based on industry knowledge
- Focus on actionable insights for investment/business decisions"""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.MARKET_RESEARCH

    async def execute(self, input_data: dict) -> dict:
        """
        Execute market research analysis using Claude API.

        Args:
            input_data: Dict containing:
                - query: The research query (company name, sector, or market)
                - context: Optional additional context

        Returns:
            Dict with market_overview, trends, competitors, opportunities, risks, sources
        """
        query = input_data.get("query", "")
        context = input_data.get("context", {})

        if not query:
            raise ValueError("Query is required for market research")

        # Build the user message
        user_message = f"Please analyze: {query}"
        if context:
            user_message += f"\n\nAdditional context: {context}"

        # Check for API key
        if not self.settings.anthropic_api_key:
            logger.warning("No Anthropic API key configured, using mock response")
            return self._generate_mock_response(query)

        try:
            # Initialize Anthropic client
            client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

            # Call Claude API
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Parse the response
            response_text = message.content[0].text
            parsed_output = self._parse_response(response_text)

            return parsed_output

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            # If API fails, provide a graceful fallback
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                return self._generate_mock_response(query)
            raise

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse Claude's response into structured output.

        Args:
            response_text: Raw text response from Claude

        Returns:
            Structured dict with market research data
        """
        import json
        import re

        # Try to extract JSON from the response
        # Claude may wrap JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end + 1]
            else:
                # Couldn't find JSON, return text as summary
                return {
                    "summary": response_text[:500],
                    "market_overview": response_text,
                    "trends": [],
                    "competitors": [],
                    "opportunities": [],
                    "risks": [],
                    "sources": ["Claude AI analysis"]
                }

        try:
            data = json.loads(json_str)

            # Ensure all expected fields exist
            output = {
                "summary": data.get("market_overview", "")[:500] if data.get("market_overview") else "",
                "market_overview": data.get("market_overview", ""),
                "trends": data.get("trends", []),
                "competitors": data.get("competitors", []),
                "opportunities": data.get("opportunities", []),
                "risks": data.get("risks", []),
                "sources": data.get("sources", ["Claude AI analysis"])
            }

            return output

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            return {
                "summary": response_text[:500],
                "market_overview": response_text,
                "trends": [],
                "competitors": [],
                "opportunities": [],
                "risks": [],
                "sources": ["Claude AI analysis"]
            }

    def _generate_mock_response(self, query: str) -> dict:
        """
        Generate a mock response when API is not available.

        Args:
            query: The research query

        Returns:
            Mock structured response
        """
        return {
            "summary": f"Market analysis for: {query}. This is a mock response - configure ANTHROPIC_API_KEY for real analysis.",
            "market_overview": f"This is a mock market overview for '{query}'. In production, this would contain detailed market analysis from Claude AI, including market size, growth projections, and key dynamics.",
            "trends": [
                {"trend": "Digital Transformation", "description": "Increasing adoption of digital technologies", "impact": "high"},
                {"trend": "Sustainability Focus", "description": "Growing emphasis on environmental responsibility", "impact": "medium"},
                {"trend": "AI Integration", "description": "Adoption of artificial intelligence across industries", "impact": "high"}
            ],
            "competitors": [
                {"name": "Sample Competitor A", "description": "Market leader", "market_position": "leader"},
                {"name": "Sample Competitor B", "description": "Emerging challenger", "market_position": "challenger"}
            ],
            "opportunities": [
                "Market expansion potential",
                "Technology innovation opportunities",
                "Strategic partnership possibilities"
            ],
            "risks": [
                "Market competition intensity",
                "Regulatory changes",
                "Economic uncertainty"
            ],
            "sources": [
                "Mock data - API key not configured",
                "Configure ANTHROPIC_API_KEY for real market research"
            ]
        }
