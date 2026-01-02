"""Tests for tool_handlers module."""

import json
import tempfile
from pathlib import Path


def test_handle_search_sessions_returns_results():
    """handle_search_sessions returns semantic search results."""
    from tool_handlers import handle_search_sessions
    from session_log.search import embed_session

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir)

        embed_session("s1", "Fixed login authentication", {"project": "app"}, db_path)
        embed_session("s2", "Added user profile page", {"project": "app"}, db_path)

        results = handle_search_sessions(
            {"query": "authentication", "limit": 5},
            chroma_path=db_path,
        )

        assert len(results) == 1
        assert results[0].type == "text"

        data = json.loads(results[0].text)
        assert len(data) >= 1
        assert data[0]["id"] == "s1"
