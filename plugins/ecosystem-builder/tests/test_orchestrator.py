"""Tests for orchestrator."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from lib.orchestrator import Orchestrator
from lib.state import StateManager


class TestOrchestrator:
    """Tests for Orchestrator."""

    def test_run_stops_when_budget_exhausted(self, tmp_path: Path) -> None:
        """Orchestrator should stop when artifact budget is exhausted."""
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=2)

        # Mock the build function to always succeed
        builds = []
        def mock_build(gap):
            builds.append(gap)
            return {"name": f"skill-{len(builds)}", "content": "content"}

        # Mock analysis to return 5 gaps (more than budget)
        gaps = [{"gap_id": f"gap-{i}"} for i in range(5)]

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )
        orchestrator._analyze = Mock(return_value=gaps)
        orchestrator._build = mock_build
        orchestrator._validate = Mock(return_value=True)

        orchestrator.run()

        # Should have built exactly 2 (the budget limit)
        assert len(builds) == 2
        assert manifest.status == "complete"
        assert manifest.budget.artifacts.used == 2

    def test_run_logs_events(self, tmp_path: Path) -> None:
        """Orchestrator should log events for each phase."""
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=1)

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )
        orchestrator._analyze = Mock(return_value=[{"gap_id": "gap-1"}])
        orchestrator._build = Mock(return_value={"name": "skill-1", "content": "c"})
        orchestrator._validate = Mock(return_value=True)

        orchestrator.run()

        # Check log file has events
        log_file = manifest.run_dir / "log.jsonl"
        log_content = log_file.read_text()
        assert "run_started" in log_content
        assert "gap_analyzed" in log_content
        assert "artifact_built" in log_content
        assert "run_complete" in log_content
