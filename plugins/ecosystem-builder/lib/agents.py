"""Multi-agent panel for ecosystem gap analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lib.state import Gap


@dataclass
class AgentResult:
    """Result from a single agent's analysis."""

    agent_name: str
    gaps: list[Gap]
    artifacts_scanned: int
    error: str | None = None

    @property
    def success(self) -> bool:
        """True if agent completed without error."""
        return self.error is None


@dataclass
class AgentPanel:
    """Coordinates multiple analysis agents."""

    user_skills_dir: Path
    plugins_dir: Path

    def run_all_agents(self) -> list[AgentResult]:
        """Run all agents and collect results."""
        return [
            self._run_catalog_agent(),
            self._run_workflow_agent(),
            self._run_quality_agent(),
        ]

    def merge_gaps(self, results: list[AgentResult]) -> list[Gap]:
        """Merge and deduplicate gaps from all agents."""
        gaps_by_id: dict[str, Gap] = {}

        for result in results:
            for gap in result.gaps:
                if gap.gap_id not in gaps_by_id:
                    gaps_by_id[gap.gap_id] = gap
                elif gap.confidence > gaps_by_id[gap.gap_id].confidence:
                    # Keep higher confidence version
                    gaps_by_id[gap.gap_id] = gap

        # Sort by priority (lower = higher priority)
        return sorted(gaps_by_id.values(), key=lambda g: g.priority)

    def _run_catalog_agent(self) -> AgentResult:
        """Catalog existing artifacts and find missing skills."""
        # Phase 2.1: Placeholder - returns empty
        return AgentResult(
            agent_name="catalog",
            gaps=[],
            artifacts_scanned=0,
        )

    def _run_workflow_agent(self) -> AgentResult:
        """Analyze workflows for holes."""
        # Phase 2.2: Placeholder - returns empty
        return AgentResult(
            agent_name="workflow-analyzer",
            gaps=[],
            artifacts_scanned=0,
        )

    def _run_quality_agent(self) -> AgentResult:
        """Score artifact quality and flag issues."""
        # Phase 2.3: Placeholder - returns empty
        return AgentResult(
            agent_name="quality-scorer",
            gaps=[],
            artifacts_scanned=0,
        )
