"""Tests for session indexing."""

import json
from pathlib import Path

import pytest


def test_index_session_stores_metadata(tmp_path):
    """index_session stores session metadata in SQLite."""
    from session_log.storage import init_db, index_session

    db_path = tmp_path / "test.db"
    init_db(db_path)

    metadata = {
        "filename": "2026-01-01_10-00-00_test.md",
        "date": "2026-01-01T10:00:00",
        "project": "test-project",
        "branch": "main",
        "duration_minutes": 30,
        "commits_made": 2,
        "files_touched": 5,
        "commands_run": 10,
        "title": "Test Session",
        "summary_path": "/path/to/summary.md",
    }

    index_session(metadata, db_path=db_path)

    # Verify it was stored
    from session_log.queries import get_session
    stored = get_session("2026-01-01_10-00-00_test.md", db_path=db_path)

    assert stored is not None
    assert stored["project"] == "test-project"
    assert stored["duration_minutes"] == 30


def test_index_session_updates_existing(tmp_path):
    """index_session updates existing session (upsert)."""
    from session_log.storage import init_db, index_session
    from session_log.queries import get_session

    db_path = tmp_path / "test.db"
    init_db(db_path)

    metadata = {
        "filename": "2026-01-01_10-00-00_test.md",
        "date": "2026-01-01T10:00:00",
        "project": "test-project",
        "branch": "main",
        "duration_minutes": 30,
        "commits_made": 2,
        "files_touched": 5,
        "commands_run": 10,
        "title": "Test Session",
        "summary_path": "/path/to/summary.md",
    }

    # Index once
    index_session(metadata, db_path=db_path)

    # Update and re-index
    metadata["duration_minutes"] = 45
    index_session(metadata, db_path=db_path)

    stored = get_session("2026-01-01_10-00-00_test.md", db_path=db_path)

    assert stored["duration_minutes"] == 45
