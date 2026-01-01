"""Tests for state management."""

import json
from pathlib import Path

import pytest

from lib.state import StateManager, RunManifest, Gap, GapType, BuildResult
from lib.logging import EventLogger, Event


class TestStateManager:
    """Tests for StateManager."""

    def test_create_run_generates_unique_id(self, tmp_path: Path) -> None:
        """Each run should have a unique ID."""
        manager = StateManager(state_dir=tmp_path)
        run1 = manager.create_run(artifact_limit=5)
        run2 = manager.create_run(artifact_limit=5)
        assert run1.run_id != run2.run_id

    def test_create_run_creates_directory(self, tmp_path: Path) -> None:
        """Run directory should be created on disk."""
        manager = StateManager(state_dir=tmp_path)
        run = manager.create_run(artifact_limit=5)
        run_dir = tmp_path / run.run_id
        assert run_dir.exists()
        assert (run_dir / "manifest.json").exists()

    def test_load_run_restores_state(self, tmp_path: Path) -> None:
        """Loading a run should restore its manifest."""
        manager = StateManager(state_dir=tmp_path)
        run = manager.create_run(artifact_limit=10)
        run.budget.artifacts.used = 3
        run.save()

        loaded = manager.load_run(run.run_id)
        assert loaded.budget.artifacts.used == 3

    def test_current_symlink_points_to_active_run(self, tmp_path: Path) -> None:
        """Current symlink should point to most recent run."""
        manager = StateManager(state_dir=tmp_path)
        run = manager.create_run(artifact_limit=5)

        current = tmp_path / "current"
        assert current.is_symlink()
        assert current.resolve() == (tmp_path / run.run_id).resolve()


class TestEventLogger:
    """Tests for EventLogger."""

    def test_log_event_appends_to_file(self, tmp_path: Path) -> None:
        """Events should be appended to log.jsonl."""
        log_file = tmp_path / "log.jsonl"
        logger = EventLogger(log_file)

        logger.log("run_started", {"artifact_limit": 5})
        logger.log("gap_found", {"gap_id": "gap-001"})

        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2

        event1 = json.loads(lines[0])
        assert event1["type"] == "run_started"
        assert event1["data"]["artifact_limit"] == 5
        assert "timestamp" in event1

    def test_read_events_returns_all(self, tmp_path: Path) -> None:
        """Reading should return all logged events."""
        log_file = tmp_path / "log.jsonl"
        logger = EventLogger(log_file)

        logger.log("event1", {})
        logger.log("event2", {})

        events = logger.read_all()
        assert len(events) == 2
        assert events[0].type == "event1"
        assert events[1].type == "event2"


class TestGap:
    """Tests for Gap dataclass."""

    def test_gap_creation(self) -> None:
        """Gap should store all required fields."""
        gap = Gap(
            gap_id="gap-001",
            gap_type=GapType.MISSING_SKILL,
            title="TDD workflow for Go projects",
            description="No skill exists for Go-specific TDD workflow",
            source_agent="workflow-analyzer",
            confidence=0.8,
            priority=1,
        )
        assert gap.gap_id == "gap-001"
        assert gap.gap_type == GapType.MISSING_SKILL
        assert gap.confidence == 0.8

    def test_gap_to_dict(self) -> None:
        """Gap should serialize to dict."""
        gap = Gap(
            gap_id="gap-002",
            gap_type=GapType.INCOMPLETE_ARTIFACT,
            title="Missing tests for handoff skill",
            description="handoff skill has no test coverage",
            source_agent="quality-scorer",
            confidence=0.9,
            priority=2,
        )
        data = gap.to_dict()
        assert data["gap_id"] == "gap-002"
        assert data["gap_type"] == "incomplete_artifact"
        assert data["source_agent"] == "quality-scorer"

    def test_gap_from_dict(self) -> None:
        """Gap should deserialize from dict."""
        data = {
            "gap_id": "gap-003",
            "gap_type": "workflow_hole",
            "title": "No pre-commit validation",
            "description": "Common workflow has no hook",
            "source_agent": "workflow-analyzer",
            "confidence": 0.7,
            "priority": 3,
        }
        gap = Gap.from_dict(data)
        assert gap.gap_type == GapType.WORKFLOW_HOLE
        assert gap.title == "No pre-commit validation"


class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_success_result(self) -> None:
        """Successful build has content and no error."""
        result = BuildResult(
            name="test-skill",
            content="---\nname: test\n---\n# Test",
            gap_id="gap-123",
        )

        assert result.success is True
        assert result.name == "test-skill"
        assert result.error is None

    def test_failure_result(self) -> None:
        """Failed build has error and no content."""
        result = BuildResult(
            name="test-skill",
            content=None,
            gap_id="gap-123",
            error="Generation failed",
        )

        assert result.success is False
        assert result.content is None
        assert result.error == "Generation failed"

    def test_to_dict_serialization(self) -> None:
        """BuildResult should serialize to dict."""
        result = BuildResult(
            name="test-skill",
            content="# Content",
            gap_id="gap-123",
            method="direct",
        )
        data = result.to_dict()

        assert data["name"] == "test-skill"
        assert data["method"] == "direct"
