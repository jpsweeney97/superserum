"""Tests for agent panel."""

from pathlib import Path

import pytest

from lib.agents import AgentPanel, AgentResult
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


class TestAgentPanel:
    """Tests for AgentPanel."""

    def test_panel_initialization(self, tmp_path: Path) -> None:
        """AgentPanel should initialize with ecosystem paths."""
        panel = AgentPanel(
            user_skills_dir=tmp_path / "skills",
            plugins_dir=tmp_path / "plugins",
        )
        assert panel.user_skills_dir == tmp_path / "skills"
        assert panel.plugins_dir == tmp_path / "plugins"

    def test_panel_run_all_agents_returns_results(self, tmp_path: Path) -> None:
        """run_all_agents should return results from all agents."""
        # Setup minimal skill structure
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test-skill\n---\n# Test")

        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        panel = AgentPanel(
            user_skills_dir=skills_dir,
            plugins_dir=plugins_dir,
        )
        results = panel.run_all_agents()

        assert len(results) == 3  # catalog, workflow, quality
        agent_names = {r.agent_name for r in results}
        assert agent_names == {"catalog", "workflow-analyzer", "quality-scorer"}

    def test_panel_merge_gaps_deduplicates(self, tmp_path: Path) -> None:
        """merge_gaps should deduplicate by gap_id."""
        panel = AgentPanel(
            user_skills_dir=tmp_path / "skills",
            plugins_dir=tmp_path / "plugins",
        )

        gap1 = Gap(
            gap_id="gap-001",
            gap_type=GapType.MISSING_SKILL,
            title="Missing skill A",
            description="Desc",
            source_agent="catalog",
            confidence=0.8,
            priority=1,
        )
        gap2 = Gap(
            gap_id="gap-001",  # duplicate
            gap_type=GapType.MISSING_SKILL,
            title="Missing skill A",
            description="Desc",
            source_agent="workflow-analyzer",
            confidence=0.9,
            priority=2,
        )
        gap3 = Gap(
            gap_id="gap-002",
            gap_type=GapType.QUALITY_ISSUE,
            title="Quality issue B",
            description="Desc",
            source_agent="quality-scorer",
            confidence=0.7,
            priority=3,
        )

        results = [
            AgentResult(agent_name="catalog", gaps=[gap1], artifacts_scanned=5),
            AgentResult(agent_name="workflow-analyzer", gaps=[gap2], artifacts_scanned=3),
            AgentResult(agent_name="quality-scorer", gaps=[gap3], artifacts_scanned=5),
        ]

        merged = panel.merge_gaps(results)

        assert len(merged) == 2
        # Higher confidence version should be kept
        gap_001 = next(g for g in merged if g.gap_id == "gap-001")
        assert gap_001.confidence == 0.9
