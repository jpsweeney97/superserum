"""Tests for state management."""

import json
from pathlib import Path

import pytest

from lib.state import StateManager, RunManifest
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
