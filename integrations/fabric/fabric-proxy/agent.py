"""Claude Agent SDK integration for Fabric pattern execution using OAuth token."""

import os
import asyncio
from typing import AsyncIterator

try:
    from claude_agent_sdk import query, ClaudeAgentOptions
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False
    print("WARNING: claude-agent-sdk not available. Install with: pip install claude-agent-sdk")


class ClaudeAgentProxy:
    """Proxy for executing Fabric patterns via Claude Agent SDK with OAuth token."""

    def __init__(self):
        """Initialize the agent proxy."""
        if not CLAUDE_SDK_AVAILABLE:
            raise ImportError(
                "claude-agent-sdk not installed. Install with: pip install claude-agent-sdk"
            )

        # Default model
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

    async def execute_pattern(self, pattern_content: str, user_input: str) -> str:
        """
        Execute a Fabric pattern with user input.

        Args:
            pattern_content: The pattern's system prompt
            user_input: User's input to process

        Returns:
            Pattern execution result as string
        """
        try:
            # Build options with system prompt
            options = ClaudeAgentOptions(
                system_prompt=pattern_content,
                max_turns=1,
                model=self.model
            )

            # Collect response
            result_text = ""
            async for message in query(prompt=user_input, options=options):
                # Extract text from assistant messages
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            result_text += block.text

            return result_text

        except Exception as e:
            raise RuntimeError(f"Pattern execution failed: {str(e)}")

    async def execute_pattern_stream(
        self, pattern_content: str, user_input: str
    ) -> AsyncIterator[str]:
        """
        Execute a Fabric pattern with streaming output.

        Args:
            pattern_content: The pattern's system prompt
            user_input: User's input to process

        Yields:
            Chunks of pattern execution result
        """
        try:
            options = ClaudeAgentOptions(
                system_prompt=pattern_content,
                max_turns=1,
                model=self.model
            )

            async for message in query(prompt=user_input, options=options):
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            yield block.text

        except Exception as e:
            yield f"Error: {str(e)}"


# Synchronous wrapper for non-async contexts
class SyncClaudeAgentProxy:
    """Synchronous wrapper for ClaudeAgentProxy."""

    def __init__(self):
        """Initialize sync agent proxy."""
        self.proxy = ClaudeAgentProxy()

    def execute_pattern(self, pattern_content: str, user_input: str) -> str:
        """
        Execute pattern synchronously.

        Args:
            pattern_content: The pattern's system prompt
            user_input: User's input to process

        Returns:
            Pattern execution result
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.proxy.execute_pattern(pattern_content, user_input)
            )
        finally:
            loop.close()
