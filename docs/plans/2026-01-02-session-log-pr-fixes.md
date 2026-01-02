# Session Log PR Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Address all 15 issues identified in PR review for session-log plugin

**Architecture:** Systematic fixes grouped by concern: critical security/crashes first, then error handling, code quality, and tests

**Tech Stack:** Python 3.12+, pytest, SQLite, MCP SDK

---

## Task 1: Fix Timezone-Naive Datetime Comparison (Critical)

**Files:**
- Modify: `plugins/session-log/mcp/session_log/summarizer.py:31-35`
- Modify: `plugins/session-log/mcp/session_log/summarizer.py:109`
- Test: `plugins/session-log/tests/test_summarizer.py`

**Step 1: Write failing test for timezone handling**

Add to `tests/test_summarizer.py`:

```python
def test_calculate_duration_with_naive_datetime():
    """Test that naive datetime in start_time is handled correctly."""
    from datetime import datetime, timezone
    from session_log.summarizer import calculate_duration_minutes

    # Naive datetime string (no timezone)
    naive_start = "2025-01-01T10:00:00"
    end_time = datetime(2025, 1, 1, 10, 30, 0, tzinfo=timezone.utc)

    # Should not crash and should return reasonable duration
    duration = calculate_duration_minutes(naive_start, end_time)
    assert duration == 30


def test_calculate_duration_with_aware_datetime():
    """Test that aware datetime is handled correctly."""
    from datetime import datetime, timezone
    from session_log.summarizer import calculate_duration_minutes

    aware_start = "2025-01-01T10:00:00+00:00"
    end_time = datetime(2025, 1, 1, 10, 45, 0, tzinfo=timezone.utc)

    duration = calculate_duration_minutes(aware_start, end_time)
    assert duration == 45
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_calculate_duration_with"`

Expected: FAIL with `TypeError: can't subtract offset-naive and offset-aware datetimes`

**Step 3: Fix calculate_duration_minutes**

In `mcp/session_log/summarizer.py`, modify `calculate_duration_minutes`:

```python
def calculate_duration_minutes(start_time: str, end_time: datetime) -> int:
    """Calculate session duration in minutes."""
    start = datetime.fromisoformat(start_time)
    # Handle timezone-naive datetimes by assuming UTC
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    delta = end_time - start
    return max(1, int(delta.total_seconds() / 60))
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_calculate_duration_with"`

Expected: PASS

**Step 5: Write failing test for get_summary_filename**

Add to `tests/test_summarizer.py`:

```python
def test_get_summary_filename_with_naive_datetime():
    """Test that naive datetime in session state is handled correctly."""
    from session_log.summarizer import get_summary_filename

    session_state = {"start_time": "2025-01-01T10:00:00"}  # Naive
    filename = get_summary_filename(session_state, "Test Title")

    assert filename.startswith("2025-01-01")
    assert "test-title" in filename


def test_get_summary_filename_with_invalid_datetime():
    """Test that invalid datetime falls back gracefully."""
    from session_log.summarizer import get_summary_filename

    session_state = {"start_time": "not-a-date"}
    # Should not crash, should fall back to current time
    filename = get_summary_filename(session_state, "Test")
    assert filename.endswith(".md")
```

**Step 6: Run test to verify failure**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_get_summary_filename"`

Expected: Second test FAILs with `ValueError`

**Step 7: Fix get_summary_filename**

```python
def get_summary_filename(session_state: dict, title: str) -> str:
    """Generate the summary filename."""
    start_time = session_state.get("start_time", datetime.now(timezone.utc).isoformat())
    try:
        dt = datetime.fromisoformat(start_time)
    except ValueError:
        dt = datetime.now(timezone.utc)
    date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
    slug = generate_slug(title)
    return f"{date_str}_{slug}.md"
```

**Step 8: Run all tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 9: Commit**

```bash
git add plugins/session-log/mcp/session_log/summarizer.py plugins/session-log/tests/test_summarizer.py
git commit -m "fix(session-log): handle timezone-naive datetimes in summarizer

- Add UTC fallback for naive datetime strings
- Handle invalid datetime formats gracefully
- Add tests for edge cases"
```

---

## Task 2: Fix __main__.py Import Path (Critical)

**Files:**
- Modify: `plugins/session-log/mcp/__main__.py`

**Step 1: Fix the import**

Change from relative to package import:

```python
from .server import main

if __name__ == "__main__":
    main()
```

**Step 2: Verify server still starts**

Run: `cd plugins/session-log/mcp && python -c "from server import main; print('ok')"`

Expected: `ok`

**Step 3: Commit**

```bash
git add plugins/session-log/mcp/__main__.py
git commit -m "fix(session-log): correct import path in __main__.py"
```

---

## Task 3: Fix Path Traversal Vulnerability (Critical)

**Files:**
- Modify: `plugins/session-log/mcp/server.py:84-88`
- Test: `plugins/session-log/tests/test_server.py` (create)

**Step 1: Create test file for server**

Create `tests/test_server.py`:

```python
"""Tests for MCP server."""

import pytest
from pathlib import Path


class TestGetSessionPathValidation:
    """Test path traversal prevention in get_session."""

    def test_valid_path_within_claude_dir(self, tmp_path):
        """Test that valid paths within .claude are allowed."""
        from server import validate_summary_path

        # Create mock .claude structure
        claude_dir = tmp_path / ".claude"
        sessions_dir = claude_dir / "sessions"
        sessions_dir.mkdir(parents=True)
        summary_file = sessions_dir / "2025-01-01_test.md"
        summary_file.write_text("# Test")

        result = validate_summary_path(str(summary_file), claude_dir)
        assert result == str(summary_file)

    def test_path_traversal_blocked(self, tmp_path):
        """Test that path traversal attempts are blocked."""
        from server import validate_summary_path

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Attempt to traverse outside .claude
        malicious_path = str(claude_dir / ".." / "etc" / "passwd")

        result = validate_summary_path(malicious_path, claude_dir)
        assert result is None

    def test_nonexistent_path_returns_none(self, tmp_path):
        """Test that nonexistent paths return None."""
        from server import validate_summary_path

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        result = validate_summary_path(str(claude_dir / "nonexistent.md"), claude_dir)
        assert result is None

    def test_symlink_escape_blocked(self, tmp_path):
        """Test that symlinks escaping .claude are blocked."""
        from server import validate_summary_path

        claude_dir = tmp_path / ".claude"
        sessions_dir = claude_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        # Create a file outside .claude
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("secret data")

        # Create symlink inside .claude pointing outside
        symlink = sessions_dir / "escape.md"
        symlink.symlink_to(outside_file)

        result = validate_summary_path(str(symlink), claude_dir)
        assert result is None
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v tests/test_server.py`

Expected: FAIL with `ImportError` (function doesn't exist)

**Step 3: Add validate_summary_path function**

Add to `mcp/server.py` after imports:

```python
def validate_summary_path(summary_path: str, base_dir: Path | None = None) -> str | None:
    """Validate summary path is within expected directory.

    Prevents path traversal attacks by ensuring the resolved path
    stays within the expected base directory.

    Args:
        summary_path: Path to validate.
        base_dir: Base directory to restrict to (default: ~/.claude).

    Returns:
        Validated path string if safe, None otherwise.
    """
    if base_dir is None:
        base_dir = Path.home() / ".claude"

    try:
        path = Path(summary_path).resolve()
        base_resolved = base_dir.resolve()

        # Check path is within base directory
        if not path.is_relative_to(base_resolved):
            return None

        # Check file exists
        if not path.exists():
            return None

        return str(path)
    except (ValueError, OSError):
        return None
```

**Step 4: Run tests again**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v tests/test_server.py`

Expected: All PASS

**Step 5: Update call_tool to use validation**

Modify the `get_session` handler in `call_tool`:

```python
    elif name == "get_session":
        filename = arguments.get("filename")
        if not filename:
            return [TextContent(type="text", text="Error: filename required")]

        session = get_session(filename)
        if session is None:
            return [TextContent(type="text", text=f"Session not found: {filename}")]

        # Read the actual markdown content with path validation
        summary_path = session.get("summary_path")
        if summary_path:
            validated_path = validate_summary_path(summary_path)
            if validated_path:
                content = Path(validated_path).read_text()
                return [TextContent(type="text", text=content)]

        return [TextContent(type="text", text=json.dumps(session, indent=2))]
```

**Step 6: Run all tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 7: Commit**

```bash
git add plugins/session-log/mcp/server.py plugins/session-log/tests/test_server.py
git commit -m "fix(session-log): prevent path traversal in get_session

- Add validate_summary_path() with directory containment check
- Block symlink escapes via resolve()
- Add comprehensive tests for path validation"
```

---

## Task 4: Fix Database Connection Leaks (High)

**Files:**
- Modify: `plugins/session-log/mcp/session_log/queries.py:34-61, 81-95`
- Modify: `plugins/session-log/mcp/session_log/storage.py:44-84`
- Test: `plugins/session-log/tests/test_queries.py`

**Step 1: Write test for connection cleanup on error**

Add to `tests/test_queries.py`:

```python
def test_list_sessions_closes_connection_on_error(tmp_path):
    """Test that database connection is closed even when query fails."""
    from unittest.mock import patch, MagicMock
    from session_log.queries import list_sessions

    db_path = tmp_path / "test.db"

    mock_conn = MagicMock()
    mock_conn.execute.side_effect = Exception("Query failed")

    with patch("session_log.queries.init_db", return_value=mock_conn):
        with pytest.raises(Exception, match="Query failed"):
            list_sessions(db_path=db_path)

    # Connection should still be closed
    mock_conn.close.assert_called_once()
```

**Step 2: Run test to verify failure**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_list_sessions_closes"`

Expected: FAIL (close not called)

**Step 3: Fix list_sessions with try/finally**

```python
def list_sessions(
    project: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = 50,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    """List sessions with optional filtering."""
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return []

    conn = init_db(db_path)
    try:
        query = "SELECT * FROM sessions WHERE 1=1"
        params: list[Any] = []

        if project:
            query += " AND project = ?"
            params.append(project)

        if after:
            query += " AND date >= ?"
            params.append(after)

        if before:
            query += " AND date <= ?"
            params.append(before)

        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results
    finally:
        conn.close()
```

**Step 4: Similarly fix get_session**

```python
def get_session(filename: str, db_path: Path | None = None) -> dict[str, Any] | None:
    """Get a single session by filename."""
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return None

    conn = init_db(db_path)
    try:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE filename = ?",
            (filename,),
        )
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        if row is None:
            return None

        return dict(zip(columns, row))
    finally:
        conn.close()
```

**Step 5: Fix index_session with try/finally and return bool**

```python
def index_session(metadata: dict, db_path: Path | None = None) -> bool:
    """Index a session in SQLite.

    Returns:
        True if indexing succeeded, False otherwise.
    """
    if db_path is None:
        db_path = get_db_path()

    conn = init_db(db_path)
    try:
        from datetime import datetime, timezone
        indexed_at = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """
            INSERT OR REPLACE INTO sessions
            (filename, date, project, branch, duration_minutes, commits_made,
             files_touched, commands_run, title, summary_path, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["filename"],
                metadata["date"],
                metadata["project"],
                metadata.get("branch"),
                metadata.get("duration_minutes"),
                metadata.get("commits_made"),
                metadata.get("files_touched"),
                metadata.get("commands_run"),
                metadata.get("title"),
                metadata["summary_path"],
                indexed_at,
            ),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()
```

**Step 6: Run all tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 7: Commit**

```bash
git add plugins/session-log/mcp/session_log/queries.py plugins/session-log/mcp/session_log/storage.py plugins/session-log/tests/test_queries.py
git commit -m "fix(session-log): ensure database connections always closed

- Wrap all database operations in try/finally
- Return bool from index_session for error checking
- Add test for connection cleanup on error"
```

---

## Task 5: Handle Silent JSON Parse Failures (High)

**Files:**
- Modify: `plugins/session-log/mcp/session_log/transcript.py:39-44`
- Test: `plugins/session-log/tests/test_transcript.py`

**Step 1: Write test for malformed JSON handling**

Add to `tests/test_transcript.py`:

```python
def test_parse_transcript_handles_malformed_json(tmp_path):
    """Test that malformed JSON lines are skipped with warning."""
    from session_log.transcript import parse_transcript
    import sys
    from io import StringIO

    transcript = tmp_path / "test.jsonl"
    transcript.write_text(
        '{"type": "user", "message": {}}\n'
        'not valid json\n'
        '{"type": "assistant", "message": {"content": []}}\n'
    )

    # Capture stderr
    old_stderr = sys.stderr
    sys.stderr = StringIO()

    try:
        result = parse_transcript(transcript)
        stderr_output = sys.stderr.getvalue()
    finally:
        sys.stderr = old_stderr

    # Should process valid lines
    assert result.user_message_count == 1
    assert result.assistant_message_count == 1

    # Should warn about invalid line
    assert "malformed JSON" in stderr_output.lower() or "line 2" in stderr_output


def test_parse_transcript_handles_empty_lines(tmp_path):
    """Test that empty lines are skipped silently."""
    from session_log.transcript import parse_transcript

    transcript = tmp_path / "test.jsonl"
    transcript.write_text(
        '{"type": "user", "message": {}}\n'
        '\n'
        '   \n'
        '{"type": "user", "message": {}}\n'
    )

    result = parse_transcript(transcript)
    assert result.user_message_count == 2
```

**Step 2: Run test to verify failure**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_parse_transcript_handles_malformed"`

Expected: FAIL with `json.JSONDecodeError`

**Step 3: Fix parse_transcript**

```python
def parse_transcript(path: Path) -> TranscriptData:
    """Parse a transcript JSONL file and extract session data."""
    import sys

    result = TranscriptData()
    text_parts = []

    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed JSON at line {line_num}: {e}", file=sys.stderr)
                continue

            msg_type = entry.get("type")
            message = entry.get("message", {})

            if msg_type == "user":
                result.user_message_count += 1

            elif msg_type == "assistant":
                result.assistant_message_count += 1
                content = message.get("content", [])

                if isinstance(content, list):
                    for block in content:
                        block_type = block.get("type")

                        if block_type == "tool_use":
                            tool_name = block.get("name", "")
                            tool_input = block.get("input", {})

                            result.tool_calls.append({
                                "name": tool_name,
                                "input": tool_input,
                            })

                            result.files_touched.update(
                                extract_files_from_tool(tool_name, tool_input)
                            )

                            if tool_name == "Bash":
                                if cmd := tool_input.get("command"):
                                    result.commands_run.append(cmd)

                        elif block_type == "text":
                            if text := block.get("text"):
                                text_parts.append(text)

    result.assistant_text = "\n".join(text_parts)
    return result
```

**Step 4: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_parse_transcript"`

Expected: All PASS

**Step 5: Commit**

```bash
git add plugins/session-log/mcp/session_log/transcript.py plugins/session-log/tests/test_transcript.py
git commit -m "fix(session-log): handle malformed JSON in transcripts

- Catch JSONDecodeError and warn on stderr
- Continue processing remaining valid lines
- Add tests for malformed and empty line handling"
```

---

## Task 6: Handle Database Failure in session_end (High)

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py:149`
- Test: `plugins/session-log/tests/test_session_end.py`

**Step 1: Update index_session call to check result**

The `index_session` function now returns `bool`. Update `session_end.py`:

```python
    # Index in SQLite
    metadata = {
        "filename": filename,
        "date": session_state.get("start_time"),
        "project": Path(cwd).name,
        "branch": session_state.get("branch"),
        "duration_minutes": calculate_duration_minutes(
            session_state.get("start_time", datetime.now(timezone.utc).isoformat()),
            datetime.now(timezone.utc),
        ),
        "commits_made": commits_made,
        "files_touched": len(transcript_data.files_touched),
        "commands_run": len(transcript_data.commands_run),
        "title": title,
        "summary_path": str(summary_path),
    }
    indexed = index_session(metadata, db_path=db_path)

    if not indexed:
        print("Warning: Failed to index session in database", file=sys.stderr)

    return {
        "success": True,
        "summary_path": str(summary_path),
        "indexed": indexed,
    }
```

**Step 2: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v tests/test_session_end.py`

Expected: All PASS

**Step 3: Commit**

```bash
git add plugins/session-log/scripts/session_end.py
git commit -m "fix(session-log): warn when database indexing fails

- Check return value from index_session()
- Log warning to stderr if indexing fails
- Include indexed status in result"
```

---

## Task 7: Handle File Write Failures (High)

**Files:**
- Modify: `plugins/session-log/scripts/session_start.py:81`
- Modify: `plugins/session-log/scripts/session_end.py:131`

**Step 1: Add error handling to session_start**

```python
def handle_session_start(input_data: dict, state_dir: Path | None = None) -> dict:
    """Handle SessionStart event."""
    if state_dir is None:
        state_dir = get_state_dir()

    session_id = input_data.get("session_id", "unknown")
    cwd = input_data.get("cwd", ".")

    git_info = get_git_info(cwd)

    state = {
        "session_id": session_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "cwd": cwd,
        "branch": git_info["branch"],
        "commit_start": git_info["commit"],
    }

    state_file = state_dir / "session_state.json"
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except OSError as e:
        print(f"Warning: Failed to write session state: {e}", file=sys.stderr)
        return {"success": False, "reason": str(e)}

    return {"success": True}
```

**Step 2: Add error handling to session_end**

```python
    # Write summary file
    title = generate_title(transcript_data, session_state.get("branch"))
    filename = get_summary_filename(session_state, title)

    sessions_dir = ensure_sessions_dir(cwd)
    summary_path = sessions_dir / filename

    try:
        summary_path.write_text(summary)
    except OSError as e:
        print(f"Warning: Failed to write summary: {e}", file=sys.stderr)
        return {"success": False, "reason": f"Failed to write summary: {e}"}
```

**Step 3: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 4: Commit**

```bash
git add plugins/session-log/scripts/session_start.py plugins/session-log/scripts/session_end.py
git commit -m "fix(session-log): handle file write failures gracefully

- Catch OSError when writing state and summary files
- Return failure status with reason
- Log warnings to stderr"
```

---

## Task 8: Handle Malformed Session State JSON (Medium)

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py:27-43`
- Test: `plugins/session-log/tests/test_session_end.py`

**Step 1: Write failing test**

Add to `tests/test_session_end.py`:

```python
def test_load_session_state_handles_malformed_json(tmp_path):
    """Test that malformed JSON in state file returns None."""
    from session_end import load_session_state

    state_file = tmp_path / "session_state.json"
    state_file.write_text("not valid json {")

    result = load_session_state(state_dir=tmp_path)
    assert result is None
```

**Step 2: Run test**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_load_session_state_handles"`

Expected: FAIL with `json.JSONDecodeError`

**Step 3: Fix load_session_state**

```python
def load_session_state(state_dir: Path | None = None) -> dict | None:
    """Load session state from SessionStart hook."""
    if state_dir is None:
        state_dir = get_state_dir()

    state_file = state_dir / "session_state.json"
    if not state_file.exists():
        return None

    try:
        return json.loads(state_file.read_text())
    except json.JSONDecodeError as e:
        print(f"Warning: Malformed session state file: {e}", file=sys.stderr)
        return None
```

**Step 4: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_load_session_state"`

Expected: All PASS

**Step 5: Commit**

```bash
git add plugins/session-log/scripts/session_end.py plugins/session-log/tests/test_session_end.py
git commit -m "fix(session-log): handle malformed session state JSON

- Catch JSONDecodeError when loading state
- Return None and warn instead of crashing"
```

---

## Task 9: Move Inline Import to Top of File (Medium)

**Files:**
- Modify: `plugins/session-log/mcp/session_log/storage.py:59-60`

**Step 1: Move import to top**

The `from datetime import datetime, timezone` is inside `index_session()`. Move it to the top imports:

```python
"""SQLite storage for session metadata."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
```

Then remove the inline import from `index_session()`.

**Step 2: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 3: Commit**

```bash
git add plugins/session-log/mcp/session_log/storage.py
git commit -m "refactor(session-log): move inline import to module level"
```

---

## Task 10: Add Logging for Git Timeout (Medium)

**Files:**
- Modify: `plugins/session-log/scripts/session_start.py:39-40`

**Step 1: Add logging for timeout**

```python
def get_git_info(cwd: str) -> dict:
    """Get current git branch and HEAD commit."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return {
            "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "commit": commit.stdout.strip() if commit.returncode == 0 else None,
        }
    except subprocess.TimeoutExpired:
        print("Warning: Git command timed out", file=sys.stderr)
        return {"branch": None, "commit": None}
    except FileNotFoundError:
        # Git not installed - not worth logging
        return {"branch": None, "commit": None}
```

**Step 2: Similarly update session_end.py get_git_info**

```python
def get_git_info(cwd: str) -> tuple[str | None, int]:
    """Get current HEAD commit and count of new commits."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit_hash = commit.stdout.strip() if commit.returncode == 0 else None
        return commit_hash, 0
    except subprocess.TimeoutExpired:
        print("Warning: Git command timed out", file=sys.stderr)
        return None, 0
    except FileNotFoundError:
        return None, 0
```

**Step 3: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All PASS

**Step 4: Commit**

```bash
git add plugins/session-log/scripts/session_start.py plugins/session-log/scripts/session_end.py
git commit -m "fix(session-log): log warning on git command timeout"
```

---

## Task 11: Add Tests for Bash Command Extraction (Medium)

**Files:**
- Test: `plugins/session-log/tests/test_transcript.py`

**Step 1: Write comprehensive test**

Add to `tests/test_transcript.py`:

```python
def test_bash_command_extraction(tmp_path):
    """Test that Bash commands are extracted from tool calls."""
    from session_log.transcript import parse_transcript
    import json

    transcript = tmp_path / "test.jsonl"

    entries = [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls -la"}},
        ]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}},
        ]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/tmp/test.py"}},
        ]}},
    ]

    transcript.write_text("\n".join(json.dumps(e) for e in entries))

    result = parse_transcript(transcript)

    assert result.commands_run == ["ls -la", "git status"]
    assert len(result.tool_calls) == 3


def test_bash_command_with_missing_command_field(tmp_path):
    """Test that Bash tool calls without command field are handled."""
    from session_log.transcript import parse_transcript
    import json

    transcript = tmp_path / "test.jsonl"

    entries = [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {}},  # No command
        ]}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "echo test"}},
        ]}},
    ]

    transcript.write_text("\n".join(json.dumps(e) for e in entries))

    result = parse_transcript(transcript)

    # Should only include the one with a command
    assert result.commands_run == ["echo test"]
```

**Step 2: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v -k "test_bash"`

Expected: All PASS

**Step 3: Commit**

```bash
git add plugins/session-log/tests/test_transcript.py
git commit -m "test(session-log): add tests for Bash command extraction"
```

---

## Task 12: Add MCP Server Integration Tests (High)

**Files:**
- Test: `plugins/session-log/tests/test_server.py`

**Step 1: Add integration tests**

Extend `tests/test_server.py`:

```python
import json
import pytest
from pathlib import Path


class TestListTools:
    """Test the list_tools handler."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_expected_tools(self):
        """Test that list_tools returns both tools."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

        from server import list_tools

        tools = await list_tools()

        assert len(tools) == 2
        tool_names = {t.name for t in tools}
        assert tool_names == {"list_sessions", "get_session"}


class TestCallTool:
    """Test the call_tool handler."""

    @pytest.mark.asyncio
    async def test_list_sessions_empty_database(self, tmp_path):
        """Test list_sessions with no database."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

        from server import call_tool
        from unittest.mock import patch

        # Mock to return empty list
        with patch("server.list_sessions", return_value=[]):
            result = await call_tool("list_sessions", {})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "[]" in result[0].text

    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        """Test get_session with nonexistent session."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

        from server import call_tool
        from unittest.mock import patch

        with patch("server.get_session", return_value=None):
            result = await call_tool("get_session", {"filename": "nonexistent.md"})

        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_session_missing_filename(self):
        """Test get_session without filename parameter."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

        from server import call_tool

        result = await call_tool("get_session", {})

        assert "filename required" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

        from server import call_tool

        result = await call_tool("unknown_tool", {})

        assert "unknown tool" in result[0].text.lower()
```

**Step 2: Run tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v tests/test_server.py`

Expected: All PASS

**Step 3: Commit**

```bash
git add plugins/session-log/tests/test_server.py
git commit -m "test(session-log): add MCP server integration tests

- Test list_tools returns expected tools
- Test call_tool with various inputs
- Test error handling for unknown tools"
```

---

## Task 13: Final Verification

**Step 1: Run full test suite**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All tests PASS

**Step 2: Run type checking**

Run: `cd plugins/session-log && pyright mcp/ scripts/`

Expected: No errors

**Step 3: Run linting**

Run: `cd plugins/session-log && ruff check mcp/ scripts/`

Expected: No errors (or acceptable warnings)

**Step 4: Final commit if any cleanup needed**

```bash
git add -A
git commit -m "chore(session-log): final cleanup and type fixes"
```

---

## Summary

| Task | Issue | Priority | Files |
|------|-------|----------|-------|
| 1 | Timezone-naive datetime | Critical | summarizer.py |
| 2 | __main__.py import | Critical | __main__.py |
| 3 | Path traversal | Critical | server.py |
| 4 | DB connection leaks | High | queries.py, storage.py |
| 5 | Silent JSON failures | High | transcript.py |
| 6 | DB failure ignored | High | session_end.py |
| 7 | File write failures | High | session_start.py, session_end.py |
| 8 | Malformed state JSON | Medium | session_end.py |
| 9 | Inline import | Medium | storage.py |
| 10 | Git timeout logging | Medium | session_start.py, session_end.py |
| 11 | Bash extraction tests | Medium | test_transcript.py |
| 12 | MCP server tests | High | test_server.py |
| 13 | Final verification | - | - |

Total: 13 tasks, ~25 commits
