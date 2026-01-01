"""Adapter for Claude Code Task tool invocation.

This module provides the interface between ecosystem-builder
and Claude Code's Task tool for subagent-based skill generation.

In production, this would be invoked by Claude Code itself.
The adapter pattern allows testing with mocks while maintaining
the same interface for production use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class SubagentConfig:
    """Configuration for subagent invocation."""

    subagent_type: str = "general-purpose"
    model: str = "sonnet"
    timeout_ms: int = 60000
    description: str = "Generate skill from gap"


def create_subagent_callable(
    config: SubagentConfig | None = None,
) -> Callable[[str], str]:
    """Create a callable that invokes the Task tool.

    In production, this would be wired to Claude Code's Task tool.
    For testing, use mock callables directly on SkillBuilder.

    Returns:
        A callable that takes a prompt string and returns generated content.
        In test environments, this returns a placeholder.
    """
    if config is None:
        config = SubagentConfig()

    def invoke_task(prompt: str) -> str:
        """Invoke Task tool with the given prompt.

        This is a placeholder implementation. In production,
        Claude Code provides the actual Task tool invocation.
        """
        # Production implementation would be:
        # - Claude Code intercepts this call
        # - Invokes Task tool with subagent_type, prompt, model
        # - Returns the agent's response

        # For now, return error indicating production wiring needed
        raise RuntimeError(
            "Task tool not available. "
            "This function should be overridden in production "
            "with Claude Code's Task tool adapter."
        )

    return invoke_task


def create_mock_callable(response: str) -> Callable[[str], str]:
    """Create a mock callable for testing.

    Args:
        response: The skill content to return.

    Returns:
        A callable that returns the given response.
    """

    def mock_invoke(prompt: str) -> str:
        return response

    return mock_invoke
