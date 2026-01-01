#!/usr/bin/env python3
"""Manual test runner for ecosystem-builder when pytest unavailable."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))


def test_state_manager():
    """Test StateManager functionality."""
    from lib.state import StateManager

    print("Testing StateManager...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manager = StateManager(state_dir=tmp_path)

        # Test unique IDs
        run1 = manager.create_run(artifact_limit=5)
        run2 = manager.create_run(artifact_limit=5)
        assert run1.run_id != run2.run_id, "Run IDs should be unique"
        print("  ✓ create_run generates unique IDs")

        # Test directory creation
        run = manager.create_run(artifact_limit=5)
        run_dir = tmp_path / run.run_id
        assert run_dir.exists(), "Run directory should exist"
        assert (run_dir / "manifest.json").exists(), "Manifest should exist"
        print("  ✓ create_run creates directory structure")

        # Test load/save
        run = manager.create_run(artifact_limit=10)
        run.budget.artifacts.used = 3
        run.save()
        loaded = manager.load_run(run.run_id)
        assert loaded.budget.artifacts.used == 3, "State should persist"
        print("  ✓ load_run restores state correctly")

        # Test current symlink
        run = manager.create_run(artifact_limit=5)
        current = tmp_path / "current"
        assert current.is_symlink(), "Current should be symlink"
        print("  ✓ current symlink works")

    return 4  # tests passed


def test_event_logger():
    """Test EventLogger functionality."""
    from lib.logging import EventLogger

    print("\nTesting EventLogger...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        log_file = tmp_path / "log.jsonl"
        logger = EventLogger(log_file)

        # Test logging
        logger.log("run_started", {"artifact_limit": 5})
        logger.log("gap_found", {"gap_id": "gap-001"})

        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2, "Should have 2 log entries"
        event1 = json.loads(lines[0])
        assert event1["type"] == "run_started"
        print("  ✓ log_event appends to file")

        # Test reading
        events = logger.read_all()
        assert len(events) == 2, "Should read all events"
        assert events[0].type == "run_started"
        print("  ✓ read_events returns all events")

    return 2  # tests passed


def test_staging_manager():
    """Test StagingManager functionality."""
    from lib.staging import StagingManager

    print("\nTesting StagingManager...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manager = StagingManager(staging_dir=tmp_path)

        # Test staging
        artifact = manager.stage_skill(
            name="my-skill",
            content="# My Skill\n\nContent here.",
            run_id="run-2026-01-01-abc123",
            gap_id="gap-001",
        )

        skill_dir = tmp_path / "skills" / "my-skill"
        assert skill_dir.exists(), "Skill dir should exist"
        assert (skill_dir / "SKILL.md").exists(), "SKILL.md should exist"
        print("  ✓ stage_skill creates directory")

        # Test listing
        manager.stage_skill("skill-2", "content", "run-1", "gap-2")
        staged = manager.list_staged()
        assert len(staged) == 2, "Should list all staged"
        print("  ✓ list_staged returns all artifacts")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Test accept
        staging = tmp_path / "staging"
        production = tmp_path / "production"
        manager = StagingManager(staging_dir=staging, production_dir=production)
        artifact = manager.stage_skill("accept-skill", "content", "run-1", "gap-1")
        manager.accept(artifact.name)
        assert not (staging / "skills" / "accept-skill").exists()
        assert (production / "accept-skill" / "SKILL.md").exists()
        print("  ✓ accept moves to production")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Test reject
        staging = tmp_path / "staging"
        rejected = tmp_path / "rejected"
        manager = StagingManager(staging_dir=staging, rejected_dir=rejected)
        artifact = manager.stage_skill("reject-skill", "content", "run-1", "gap-1")
        manager.reject(artifact.name, reason="Not useful")
        assert not (staging / "skills" / "reject-skill").exists()
        assert (rejected / "run-1" / "reject-skill").exists()
        print("  ✓ reject moves to rejected")

    return 4  # tests passed


def test_orchestrator():
    """Test Orchestrator functionality."""
    from lib.orchestrator import Orchestrator
    from lib.state import StateManager

    print("\nTesting Orchestrator...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        state_manager = StateManager(state_dir=tmp_path / "state")
        manifest = state_manager.create_run(artifact_limit=2)

        builds = []
        def mock_build(gap):
            builds.append(gap)
            return {"name": f"skill-{len(builds)}", "content": "content"}

        gaps = [{"gap_id": f"gap-{i}"} for i in range(5)]

        orchestrator = Orchestrator(
            manifest=manifest,
            staging_dir=tmp_path / "staging",
        )
        orchestrator._analyze = Mock(return_value=gaps)
        orchestrator._build = mock_build
        orchestrator._validate = Mock(return_value=True)

        orchestrator.run()

        assert len(builds) == 2, f"Should build exactly 2, got {len(builds)}"
        assert manifest.status == "complete", "Status should be complete"
        assert manifest.budget.artifacts.used == 2
        print("  ✓ run stops when budget exhausted")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
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

        log_file = manifest.run_dir / "log.jsonl"
        log_content = log_file.read_text()
        assert "run_started" in log_content
        assert "run_complete" in log_content
        print("  ✓ run logs events correctly")

    return 2  # tests passed


def main():
    """Run all tests."""
    print("=" * 60)
    print("Ecosystem Builder - Test Suite")
    print("=" * 60)

    total = 0
    try:
        total += test_state_manager()
        total += test_event_logger()
        total += test_staging_manager()
        total += test_orchestrator()

        print("\n" + "=" * 60)
        print(f"ALL TESTS PASSED: {total}/{total}")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
