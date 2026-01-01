"""Tests for state management."""

import json
from pathlib import Path

import pytest

from lib.state import StateManager, RunManifest


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
