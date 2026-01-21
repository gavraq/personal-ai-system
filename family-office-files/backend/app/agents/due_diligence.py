"""
Due Diligence Agent for AI-powered entity investigation

This agent provides due diligence capabilities including:
- Company/person/transaction overview and background
- Financial analysis and metrics
- Leadership team assessment
- News and media coverage
- Risk flag identification with severity levels
- Regulatory and legal considerations
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


class DueDiligenceOutput:
    """Structure for due diligence output"""

    def __init__(
        self,
        overview: str,
        financials: list[dict],
        leadership: list[dict],
        news: list[dict],
        risk_flags: list[dict],
        sources: list[str]
    ):
        self.overview = overview
        self.financials = financials
        self.leadership = leadership
        self.news = news
        self.risk_flags = risk_flags
        self.sources = sources

    def to_dict(self) -> dict:
        return {
            "summary": self.overview[:500] if self.overview else "",
            "overview": self.overview,
            "financials": self.financials,
            "leadership": self.leadership,
            "news": self.news,
            "risk_flags": self.risk_flags,
            "sources": self.sources
        }


class DueDiligenceAgent(BaseAgent):
    """
    Due Diligence Agent for comprehensive entity investigation.

    Input: entity_name, entity_type (company/person/transaction)
    Output: overview, financials, leadership, news, risk_flags, sources
    """

    SYSTEM_PROMPT = """You are a professional due diligence analyst. Your task is to provide comprehensive due diligence research on the specified entity.

Provide your analysis in the following JSON structure:
{
    "overview": "A comprehensive overview of the entity including background, history, and current status (2-3 paragraphs)",
    "financials": [
        {"metric": "Revenue", "value": "$X million", "period": "2023", "trend": "increasing/decreasing/stable", "notes": "Additional context"}
    ],
    "leadership": [
        {"name": "Person Name", "title": "Position", "background": "Brief background", "tenure": "Years in role", "notable": "Key achievements or concerns"}
    ],
    "news": [
        {"headline": "News headline", "date": "YYYY-MM-DD", "source": "Publication", "sentiment": "positive/negative/neutral", "summary": "Brief summary"}
    ],
    "risk_flags": [
        {"flag": "Risk description", "severity": "high/medium/low", "category": "regulatory/financial/operational/reputational/legal", "details": "Additional context", "mitigation": "Potential mitigation if applicable"}
    ],
    "sources": ["Source 1 with URL or description", "Source 2 with URL or description"]
}

Important guidelines:
- Provide factual, well-researched information based on publicly available data
- For companies: Include registration details, market position, competitive landscape
- For persons: Include professional history, public roles, media presence
- For transactions: Include parties involved, terms, regulatory considerations
- Risk flags should be specific and actionable with severity levels:
  - HIGH: Immediate concerns requiring attention (litigation, regulatory action, fraud allegations)
  - MEDIUM: Potential issues requiring monitoring (financial stress, management turnover, industry headwinds)
  - LOW: Minor concerns or areas for awareness (minor regulatory items, normal business challenges)
- Include regulatory and legal considerations where relevant
- Cite all sources clearly
- If information is unavailable or uncertain, clearly indicate this
- Focus on material information relevant to investment or business decisions"""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DUE_DILIGENCE

    async def execute(self, input_data: dict) -> dict:
        """
        Execute due diligence analysis using Claude API.

        Args:
            input_data: Dict containing:
                - query: The entity name or search query
                - entity_type: Type of entity (company/person/transaction)
                - context: Optional additional context

        Returns:
            Dict with overview, financials, leadership, news, risk_flags, sources
        """
        query = input_data.get("query", "")
        entity_type = input_data.get("entity_type", "company")
        context = input_data.get("context", {})

        if not query:
            raise ValueError("Query is required for due diligence")

        # Build the user message
        user_message = f"Please conduct due diligence research on: {query}"
        user_message += f"\nEntity type: {entity_type}"
        if context:
            user_message += f"\n\nAdditional context: {context}"

        # Check for API key
        if not self.settings.anthropic_api_key:
            logger.warning("No Anthropic API key configured, using mock response")
            return self._generate_mock_response(query, entity_type)

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
                return self._generate_mock_response(query, entity_type)
            raise

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse Claude's response into structured output.

        Args:
            response_text: Raw text response from Claude

        Returns:
            Structured dict with due diligence data
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
                    "overview": response_text,
                    "financials": [],
                    "leadership": [],
                    "news": [],
                    "risk_flags": [],
                    "sources": ["Claude AI analysis"]
                }

        try:
            data = json.loads(json_str)

            # Ensure all expected fields exist
            output = {
                "summary": data.get("overview", "")[:500] if data.get("overview") else "",
                "overview": data.get("overview", ""),
                "financials": data.get("financials", []),
                "leadership": data.get("leadership", []),
                "news": data.get("news", []),
                "risk_flags": data.get("risk_flags", []),
                "sources": data.get("sources", ["Claude AI analysis"])
            }

            return output

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            return {
                "summary": response_text[:500],
                "overview": response_text,
                "financials": [],
                "leadership": [],
                "news": [],
                "risk_flags": [],
                "sources": ["Claude AI analysis"]
            }

    def _generate_mock_response(self, query: str, entity_type: str) -> dict:
        """
        Generate a mock response when API is not available.

        Args:
            query: The entity query
            entity_type: Type of entity

        Returns:
            Mock structured response
        """
        return {
            "summary": f"Due diligence analysis for: {query} ({entity_type}). This is a mock response - configure ANTHROPIC_API_KEY for real analysis.",
            "overview": f"This is a mock due diligence overview for '{query}' ({entity_type}). In production, this would contain detailed background research from Claude AI, including company history, market position, and key developments.",
            "financials": [
                {"metric": "Revenue", "value": "N/A (mock data)", "period": "2024", "trend": "stable", "notes": "Mock response - API key not configured"},
                {"metric": "Net Income", "value": "N/A (mock data)", "period": "2024", "trend": "stable", "notes": "Mock response - API key not configured"},
                {"metric": "Total Assets", "value": "N/A (mock data)", "period": "2024", "trend": "stable", "notes": "Mock response - API key not configured"}
            ],
            "leadership": [
                {"name": "Sample Executive", "title": "CEO", "background": "Mock leadership data", "tenure": "N/A", "notable": "Configure API for real data"},
                {"name": "Sample Director", "title": "CFO", "background": "Mock leadership data", "tenure": "N/A", "notable": "Configure API for real data"}
            ],
            "news": [
                {"headline": "Mock News Article", "date": "2024-01-01", "source": "Mock Source", "sentiment": "neutral", "summary": "This is mock news data. Configure ANTHROPIC_API_KEY for real analysis."},
                {"headline": "Sample Industry Update", "date": "2024-01-01", "source": "Mock Source", "sentiment": "neutral", "summary": "Mock news for demonstration purposes."}
            ],
            "risk_flags": [
                {"flag": "API Configuration Required", "severity": "medium", "category": "operational", "details": "ANTHROPIC_API_KEY not configured for real due diligence analysis", "mitigation": "Configure API key in environment"},
                {"flag": "Mock Data Limitation", "severity": "low", "category": "operational", "details": "Current output is placeholder data only", "mitigation": "Enable production API access"},
                {"flag": "Sample Risk Flag", "severity": "high", "category": "reputational", "details": "This demonstrates a high-severity risk flag format", "mitigation": "In production, specific mitigation steps would be provided"}
            ],
            "sources": [
                "Mock data - API key not configured",
                "Configure ANTHROPIC_API_KEY for real due diligence research"
            ]
        }
