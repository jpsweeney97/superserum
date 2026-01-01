"""Tests for SkillGeneratorAgent."""

from lib.skill_generator import SkillGeneratorAgent, GenerationResult
from lib.state import Gap, GapType


class TestSkillGeneratorAgent:
    """Tests for SkillGeneratorAgent interface."""

    def test_generation_result_success(self) -> None:
        """GenerationResult tracks success state."""
        result = GenerationResult(
            name="test-skill",
            content="---\nname: test\n---\n# Test",
            gap_id="gap-123",
        )

        assert result.success is True
        assert result.error is None

    def test_generation_result_failure(self) -> None:
        """GenerationResult tracks failure state."""
        result = GenerationResult(
            name="test-skill",
            content=None,
            gap_id="gap-123",
            error="Generation failed: timeout",
        )

        assert result.success is False
        assert "timeout" in result.error

    def test_agent_accepts_gap_dict(self) -> None:
        """Agent.generate() accepts gap as dict."""
        agent = SkillGeneratorAgent()
        gap = Gap(
            gap_id="gap-1",
            gap_type=GapType.WORKFLOW_HOLE,
            title="ci-cd-integration",
            description="Complex CI/CD workflow integration",
            source_agent="workflow",
            confidence=0.5,
            priority=1,
        )

        # Should not raise
        result = agent.generate(gap.to_dict())

        assert isinstance(result, GenerationResult)
        assert result.gap_id == "gap-1"
