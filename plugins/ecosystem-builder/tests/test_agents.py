"""Tests for agent panel."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lib.agents import AgentResult
from lib.state import Gap, GapType


class TestAgentResult:
    """Tests for AgentResult."""

    def test_agent_result_creation(self) -> None:
        """AgentResult should store gaps and metadata."""
        gaps = [
            Gap(
                gap_id="gap-001",
                gap_type=GapType.MISSING_SKILL,
                title="Test gap",
                description="Description",
                source_agent="catalog",
                confidence=0.8,
                priority=1,
            )
        ]
        result = AgentResult(
            agent_name="catalog",
            gaps=gaps,
            artifacts_scanned=15,
            error=None,
        )
        assert result.agent_name == "catalog"
        assert len(result.gaps) == 1
        assert result.artifacts_scanned == 15
        assert result.success is True

    def test_agent_result_with_error(self) -> None:
        """AgentResult should track errors."""
        result = AgentResult(
            agent_name="catalog",
            gaps=[],
            artifacts_scanned=0,
            error="Failed to scan skills directory",
        )
        assert result.success is False
        assert result.error == "Failed to scan skills directory"
