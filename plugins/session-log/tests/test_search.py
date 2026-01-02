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
