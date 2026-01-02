"""Tests for transcript parser."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_transcript(tmp_path):
    """Create a sample transcript file."""
    transcript = tmp_path / "transcript.jsonl"
    content = '''{"type":"user","message":{"content":"Help me fix the auth bug"}}
{"type":"assistant","message":{"content":[{"type":"thinking","thinking":"Let me look"},{"type":"tool_use","name":"Read","input":{"file_path":"src/auth.py"}},{"type":"text","text":"Found the issue."}]}}
{"type":"user","message":{"content":"Fix it"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"src/auth.py","old_string":"bug","new_string":"fix"}},{"type":"text","text":"Fixed!"}]}}
'''
    transcript.write_text(content)
    return transcript


def test_parse_transcript_extracts_tool_calls(sample_transcript):
    """Parser extracts tool calls from transcript."""
    from session_log.transcript import parse_transcript

    result = parse_transcript(sample_transcript)

    assert len(result.tool_calls) == 2
    assert result.tool_calls[0]["name"] == "Read"
    assert result.tool_calls[1]["name"] == "Edit"


def test_parse_transcript_extracts_files_touched(sample_transcript):
    """Parser extracts unique files touched."""
    from session_log.transcript import parse_transcript

    result = parse_transcript(sample_transcript)

    assert "src/auth.py" in result.files_touched


def test_parse_transcript_counts_messages(sample_transcript):
    """Parser counts user and assistant messages."""
    from session_log.transcript import parse_transcript

    result = parse_transcript(sample_transcript)

    assert result.user_message_count == 2
    assert result.assistant_message_count == 2


def test_parse_transcript_extracts_text_content(sample_transcript):
    """Parser extracts text content from assistant messages."""
    from session_log.transcript import parse_transcript

    result = parse_transcript(sample_transcript)

    assert "Found the issue" in result.assistant_text
    assert "Fixed!" in result.assistant_text
