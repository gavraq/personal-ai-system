"""
Risk Agents Claude Client
Wrapper around Anthropic's Claude SDK for Skills Framework integration
"""

from anthropic import Anthropic
from typing import Iterator, Dict, Any, List, Optional
from pathlib import Path
import os


class RiskAgentClient:
    """
    Claude Agent Client with Skills Framework integration

    This class wraps the Anthropic SDK and provides a Skills-aware interface
    for executing queries with progressive disclosure of skill information.
    """

    def __init__(self, skills_dir: Path):
        """
        Initialize the Risk Agent Client

        Args:
            skills_dir: Path to .claude/skills directory
        """
        self.skills_dir = skills_dir
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Model configuration
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet 4.5 (May 2025)
        self.max_tokens = 8192  # Sonnet 4.5 supports up to 8K output tokens

    def query(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Execute a query with Skills Framework context

        Args:
            user_message: The user's question or request
            context: Optional context dictionary (session data, captured info, etc.)
            system_prompt: Optional custom system prompt (uses default if not provided)

        Returns:
            Claude's response as a string
        """
        # Build system prompt with Skills Framework awareness
        final_system_prompt = system_prompt or self._build_system_prompt()

        # Add context to system prompt if provided
        if context:
            context_text = self._format_context(context)
            final_system_prompt += f"\n\n{context_text}"

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=final_system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extract text from response
        return response.content[0].text

    def query_stream(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> Iterator[str]:
        """
        Execute a streaming query with Skills Framework context

        Args:
            user_message: The user's question or request
            context: Optional context dictionary
            system_prompt: Optional custom system prompt

        Yields:
            Text chunks as they arrive from Claude
        """
        # Build system prompt
        final_system_prompt = system_prompt or self._build_system_prompt()

        # Add context if provided
        if context:
            context_text = self._format_context(context)
            final_system_prompt += f"\n\n{context_text}"

        # Stream response from Claude
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=final_system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _build_system_prompt(self) -> str:
        """
        Build system prompt with Skills Framework awareness

        Returns:
            System prompt string explaining the agent's capabilities
        """
        return """You are Risk Agents, a specialized AI assistant for project management and risk analysis.

You have access to a Skills Framework organized in a .claude/skills directory structure.
Each skill follows progressive disclosure - you can load metadata, instructions, and resources as needed.

## Available Skill Domains

### Change Agent (Project Management)
Skills organized by category:
- **Meeting Management**: meeting-minutes-capture, action-item-tracking, follow-up-generator
- **Project Setup**: project-charter-generator, stakeholder-analysis, project-plan-template
- **Requirements Gathering**: business-requirements-capture, requirement-validation, use-case-generator
- **Project Artifacts**: raci-matrix-generator, communication-plan, risk-register-setup
- **Status Tracking**: status-report-generator, milestone-tracker, issue-log-manager

## How to Use Skills

When a user asks for help:
1. Identify which skill(s) are relevant to their request
2. Load the skill metadata to understand its purpose and parameters
3. If needed, load detailed instructions from the skill's instructions/ directory
4. Execute the skill with the provided information
5. Format the output according to the skill's specification

## Knowledge Layer

You also have access to a Knowledge Layer with documentation organized by taxonomy:
- Meeting Management best practices
- Project Management methodologies
- Requirements Gathering techniques
- Project Artifacts templates
- Status Tracking approaches

## Your Role

- Help users with project management tasks
- Capture and structure meeting information
- Generate project artifacts and documentation
- Track action items and project status
- Apply risk management best practices

Always be clear, concise, and actionable in your responses."""

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary into a readable string for the system prompt

        Args:
            context: Dictionary of context information

        Returns:
            Formatted context string
        """
        context_lines = ["## Session Context"]

        for key, value in context.items():
            if value:
                context_lines.append(f"**{key.replace('_', ' ').title()}**: {value}")

        return "\n".join(context_lines)

    def get_available_skills(self) -> List[str]:
        """
        Get list of available skills by scanning the skills directory

        Returns:
            List of skill names in format "domain/skill-name"
        """
        skills = []

        if not self.skills_dir.exists():
            return skills

        # Scan domain directories
        for domain_dir in self.skills_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                # Scan skill directories within domain
                for skill_dir in domain_dir.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skills.append(f"{domain_dir.name}/{skill_dir.name}")

        return skills

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Claude API

        Returns:
            Dictionary with connection status
        """
        try:
            response = self.query("Hello! Please respond with 'Connection successful'")
            return {
                "status": "connected",
                "model": self.model,
                "response": response[:100],  # First 100 chars
                "skills_available": len(self.get_available_skills())
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
