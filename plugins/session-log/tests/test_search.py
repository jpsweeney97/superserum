"""Tests for search module."""

import tempfile
from pathlib import Path

import pytest


def test_get_collection_creates_persistent_storage():
    """ChromaDB collection is created with persistent storage."""
    from session_log.search import get_collection

    with tempfile.TemporaryDirectory() as tmpdir:
        collection = get_collection(db_path=Path(tmpdir))

        assert collection is not None
        assert collection.name == "sessions"


def test_embed_session_stores_document():
    """embed_session stores session content in ChromaDB."""
    from session_log.search import embed_session, get_collection

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir)

        success = embed_session(
            session_id="2026-01-02_10-30-00_test-session",
            content="Fixed authentication bug in login flow",
            metadata={"project": "myapp", "branch": "fix/auth"},
            db_path=db_path,
        )

        assert success is True

        # Verify it was stored
        collection = get_collection(db_path)
        assert collection.count() == 1
