"""Tests for session_end hook script."""

import json
import tempfile
from pathlib import Path

import pytest


def test_session_end_reads_state():
    """SessionEnd hook reads session state from SessionStart."""
    from scripts.session_end import load_session_state

    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir)
        state = {
            "session_id": "test-123",
            "start_time": "2026-01-01T10:00:00+00:00",
            "cwd": "/project",
            "branch": "main",
            "commit_start": "abc1234",
        }
        (state_dir / "session_state.json").write_text(json.dumps(state))

        loaded = load_session_state(state_dir)

        assert loaded["session_id"] == "test-123"
        assert loaded["branch"] == "main"


def test_session_end_handles_missing_state():
    """SessionEnd hook handles missing state gracefully."""
    from scripts.session_end import load_session_state

    with tempfile.TemporaryDirectory() as tmpdir:
        loaded = load_session_state(Path(tmpdir))

        assert loaded is None


def test_session_end_uses_default_state_dir():
    """SessionEnd hook uses default state directory when not specified."""
    from scripts.session_end import get_state_dir

    state_dir = get_state_dir()
    expected = Path.home() / ".claude" / "session-log" / "state"
    assert state_dir == expected


def test_session_end_handles_no_state():
    """SessionEnd returns error when no session state found."""
    from scripts.session_end import handle_session_end

    with tempfile.TemporaryDirectory() as tmpdir:
        result = handle_session_end({}, state_dir=Path(tmpdir))

        assert result["success"] is False
        assert "No session state found" in result["reason"]


def test_session_end_handles_missing_transcript():
    """SessionEnd returns error when transcript path is missing."""
    from scripts.session_end import handle_session_end

    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir)
        state = {
            "session_id": "test-123",
            "start_time": "2026-01-01T10:00:00+00:00",
            "cwd": "/project",
            "branch": "main",
            "commit_start": "abc1234",
        }
        (state_dir / "session_state.json").write_text(json.dumps(state))

        result = handle_session_end({}, state_dir=state_dir)

        assert result["success"] is False
        assert "Transcript not found" in result["reason"]


def test_session_end_handles_nonexistent_transcript():
    """SessionEnd returns error when transcript path doesn't exist."""
    from scripts.session_end import handle_session_end

    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir)
        state = {
            "session_id": "test-123",
            "start_time": "2026-01-01T10:00:00+00:00",
            "cwd": "/project",
            "branch": "main",
            "commit_start": "abc1234",
        }
        (state_dir / "session_state.json").write_text(json.dumps(state))

        result = handle_session_end(
            {"transcript_path": "/nonexistent/transcript.jsonl"},
            state_dir=state_dir,
        )

        assert result["success"] is False
        assert "Transcript not found" in result["reason"]


def test_session_end_skips_minimal_transcript():
    """SessionEnd skips transcripts with fewer than 2 user messages."""
    from scripts.session_end import handle_session_end

    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir)
        state = {
            "session_id": "test-123",
            "start_time": "2026-01-01T10:00:00+00:00",
            "cwd": tmpdir,
            "branch": "main",
            "commit_start": "abc1234",
        }
        (state_dir / "session_state.json").write_text(json.dumps(state))

        # Create a minimal transcript with only 1 user message
        transcript_file = Path(tmpdir) / "transcript.jsonl"
        transcript_file.write_text(
            '{"type": "user", "message": {"content": "Hi"}}\n'
            '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Hello!"}]}}\n'
        )

        result = handle_session_end(
            {"transcript_path": str(transcript_file)},
            state_dir=state_dir,
        )

        assert result["success"] is True
        assert "too short" in result["reason"]
