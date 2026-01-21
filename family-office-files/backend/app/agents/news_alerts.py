"""
News & Alerts Agent for AI-powered news monitoring and alert generation

This agent provides news monitoring capabilities including:
- Keyword and entity-based news search
- Alert configuration management
- News source aggregation
- Sentiment analysis
- Match scoring and notification generation
"""
import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session

from .base import BaseAgent
from ..models.agent import AgentType

logger = logging.getLogger(__name__)


class NewsAlertsOutput:
    """Structure for news alerts output"""

    def __init__(
        self,
        news_items: list[dict],
        summary: str,
        total_matches: int,
        keywords_matched: list[str],
        sources: list[str]
    ):
        self.news_items = news_items
        self.summary = summary
        self.total_matches = total_matches
        self.keywords_matched = keywords_matched
        self.sources = sources

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "news_items": self.news_items,
            "total_matches": self.total_matches,
            "keywords_matched": self.keywords_matched,
            "sources": self.sources
        }


class NewsAlertsAgent(BaseAgent):
    """
    News & Alerts Agent for monitoring and alerting on news items.

    Input: keywords, entities, query
    Output: news_items, summary, total_matches, keywords_matched, sources
    """

    SYSTEM_PROMPT = """You are a professional news analyst and monitoring specialist. Your task is to search for and analyze news related to the specified keywords, entities, or topics.

Provide your analysis in the following JSON structure:
{
    "summary": "A brief overview of the key findings and notable news (2-3 sentences)",
    "news_items": [
        {
            "headline": "News article headline",
            "date": "YYYY-MM-DD",
            "source": "Publication name",
            "url": "Source URL if available",
            "snippet": "Brief excerpt or summary (2-3 sentences)",
            "relevance_score": 0.95,
            "sentiment": "positive/negative/neutral",
            "keywords_matched": ["keyword1", "keyword2"],
            "entities_mentioned": ["Entity1", "Entity2"]
        }
    ],
    "total_matches": 5,
    "keywords_matched": ["keyword1", "keyword2"],
    "sources": ["Source 1", "Source 2"]
}

Important guidelines:
- Search for the most recent and relevant news based on the query
- Prioritize authoritative and reliable sources
- Include relevance scores (0.0-1.0) for each news item
- Perform sentiment analysis on each article
- Identify and tag keywords and entities mentioned
- If specific keywords are provided, highlight matches
- Include source citations for all news items
- If no relevant news is found, indicate this clearly
- Focus on material information relevant to business and investment decisions"""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.NEWS_ALERTS

    async def execute(self, input_data: dict) -> dict:
        """
        Execute news search and analysis using Claude API.

        Args:
            input_data: Dict containing:
                - query: The news search query
                - keywords: List of keywords to monitor
                - entities: List of entities to track
                - context: Optional additional context

        Returns:
            Dict with news_items, summary, total_matches, keywords_matched, sources
        """
        query = input_data.get("query", "")
        keywords = input_data.get("keywords", [])
        entities = input_data.get("entities", [])
        context = input_data.get("context", {})

        if not query and not keywords and not entities:
            raise ValueError("At least one of query, keywords, or entities is required")

        # Build the user message
        user_message = "Please search for and analyze news related to:"
        if query:
            user_message += f"\nQuery: {query}"
        if keywords:
            user_message += f"\nKeywords to monitor: {', '.join(keywords)}"
        if entities:
            user_message += f"\nEntities to track: {', '.join(entities)}"
        if context:
            user_message += f"\n\nAdditional context: {context}"

        # Check for API key
        if not self.settings.anthropic_api_key:
            logger.warning("No Anthropic API key configured, using mock response")
            return self._generate_mock_response(query, keywords, entities)

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
                return self._generate_mock_response(query, keywords, entities)
            raise

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse Claude's response into structured output.

        Args:
            response_text: Raw text response from Claude

        Returns:
            Structured dict with news data
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
                    "news_items": [],
                    "total_matches": 0,
                    "keywords_matched": [],
                    "sources": ["Claude AI analysis"]
                }

        try:
            data = json.loads(json_str)

            # Ensure all expected fields exist
            output = {
                "summary": data.get("summary", ""),
                "news_items": data.get("news_items", []),
                "total_matches": data.get("total_matches", len(data.get("news_items", []))),
                "keywords_matched": data.get("keywords_matched", []),
                "sources": data.get("sources", ["Claude AI analysis"])
            }

            return output

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            return {
                "summary": response_text[:500],
                "news_items": [],
                "total_matches": 0,
                "keywords_matched": [],
                "sources": ["Claude AI analysis"]
            }

    def _generate_mock_response(self, query: str, keywords: list, entities: list) -> dict:
        """
        Generate a mock response when API is not available.

        Args:
            query: The search query
            keywords: List of keywords
            entities: List of entities

        Returns:
            Mock structured response
        """
        search_terms = query or ", ".join(keywords) or ", ".join(entities)
        return {
            "summary": f"News monitoring for: {search_terms}. This is a mock response - configure ANTHROPIC_API_KEY for real news analysis.",
            "news_items": [
                {
                    "headline": "Sample News Article 1",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "source": "Mock News Source",
                    "url": "https://example.com/news/1",
                    "snippet": "This is a mock news item. Configure ANTHROPIC_API_KEY for real news monitoring.",
                    "relevance_score": 0.85,
                    "sentiment": "neutral",
                    "keywords_matched": keywords[:2] if keywords else ["sample"],
                    "entities_mentioned": entities[:2] if entities else ["Sample Entity"]
                },
                {
                    "headline": "Sample News Article 2",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "source": "Mock Financial Times",
                    "url": "https://example.com/news/2",
                    "snippet": "Another mock news item demonstrating the alert system capabilities.",
                    "relevance_score": 0.72,
                    "sentiment": "positive",
                    "keywords_matched": keywords[1:3] if len(keywords) > 1 else ["demo"],
                    "entities_mentioned": entities[:1] if entities else ["Demo Corp"]
                }
            ],
            "total_matches": 2,
            "keywords_matched": keywords if keywords else ["sample", "demo"],
            "sources": [
                "Mock data - API key not configured",
                "Configure ANTHROPIC_API_KEY for real news monitoring"
            ]
        }
