# Session-Log Phase 3: MCP Server Tools

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add MCP tools for querying session history, wire SQLite indexing into SessionEnd hook, and create a `/list-sessions` command.

**Architecture:** The MCP server exposes `list_sessions` and `get_session` tools that query the SQLite index. The SessionEnd hook indexes each session after writing the summary. A `/list-sessions` command provides a user-friendly interface.

**Tech Stack:** Python 3.12+, mcp>=1.0.0, sqlite3 (stdlib)

**Prior Work:** Phase 1-2 complete with 25 tests passing. Core infrastructure (hooks, storage schema, transcript parser, summary generator) in place.

**Test Command:** `./scripts/run_tests.sh` (workaround for uv sandbox issue)

---

## Task 3.1: Add Queries Module

**Files:**
- Create: `plugins/session-log/mcp/session_log/queries.py`
- Create: `plugins/session-log/tests/test_queries.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_queries.py`:
```python
"""Tests for query functions."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def db_with_sessions(tmp_path):
    """Create a database with sample sessions."""
    from session_log.storage import init_db

    db_path = tmp_path / "test.db"
    conn = init_db(db_path)

    sessions = [
        ("2026-01-01_10-00-00_auth.md", "2026-01-01T10:00:00", "project-a", "feat/auth", 30, 2, 5, 10, "Auth work", "/path/a.md", "2026-01-01T11:00:00"),
        ("2026-01-01_14-00-00_api.md", "2026-01-01T14:00:00", "project-a", "main", 45, 3, 8, 15, "API work", "/path/b.md", "2026-01-01T15:00:00"),
        ("2026-01-02_09-00-00_docs.md", "2026-01-02T09:00:00", "project-b", "main", 20, 1, 2, 5, "Docs update", "/path/c.md", "2026-01-02T09:30:00"),
    ]

    conn.executemany(
        """INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        sessions,
    )
    conn.commit()

    return db_path


def test_list_sessions_returns_all(db_with_sessions):
    """list_sessions returns all sessions by default."""
    from session_log.queries import list_sessions

    result = list_sessions(db_path=db_with_sessions)

    assert len(result) == 3


def test_list_sessions_filters_by_project(db_with_sessions):
    """list_sessions filters by project."""
    from session_log.queries import list_sessions

    result = list_sessions(project="project-a", db_path=db_with_sessions)

    assert len(result) == 2
    assert all(s["project"] == "project-a" for s in result)


def test_list_sessions_filters_by_date(db_with_sessions):
    """list_sessions filters by date range."""
    from session_log.queries import list_sessions

    result = list_sessions(
        after="2026-01-02",
        db_path=db_with_sessions,
    )

    assert len(result) == 1
    assert result[0]["project"] == "project-b"


def test_list_sessions_respects_limit(db_with_sessions):
    """list_sessions respects limit parameter."""
    from session_log.queries import list_sessions

    result = list_sessions(limit=2, db_path=db_with_sessions)

    assert len(result) == 2


def test_get_session_returns_session(db_with_sessions):
    """get_session returns a single session by filename."""
    from session_log.queries import get_session

    result = get_session("2026-01-01_10-00-00_auth.md", db_path=db_with_sessions)

    assert result is not None
    assert result["title"] == "Auth work"
    assert result["project"] == "project-a"


def test_get_session_returns_none_for_missing(db_with_sessions):
    """get_session returns None for non-existent session."""
    from session_log.queries import get_session

    result = get_session("nonexistent.md", db_path=db_with_sessions)

    assert result is None
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_queries.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'session_log.queries'"

**Step 3: Write queries module**

Create `plugins/session-log/mcp/session_log/queries.py`:
```python
"""Query functions for session data."""

from pathlib import Path
from typing import Any

from .storage import get_db_path, init_db


def list_sessions(
    project: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = 50,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    """List sessions with optional filtering.

    Args:
        project: Filter by project name.
        after: Filter sessions on or after this date (YYYY-MM-DD or ISO).
        before: Filter sessions on or before this date.
        limit: Maximum number of results.
        db_path: Optional override for database path (for testing).

    Returns:
        List of session dictionaries ordered by date descending.
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return []

    conn = init_db(db_path)

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

    conn.close()
    return results


def get_session(filename: str, db_path: Path | None = None) -> dict[str, Any] | None:
    """Get a single session by filename.

    Args:
        filename: The session filename (primary key).
        db_path: Optional override for database path (for testing).

    Returns:
        Session dictionary or None if not found.
    """
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return None

    conn = init_db(db_path)

    cursor = conn.execute(
        "SELECT * FROM sessions WHERE filename = ?",
        (filename,),
    )
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return dict(zip(columns, row))
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_queries.py -v`

Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add queries module for session lookups"
```

---

## Task 3.2: Add index_session Function

**Files:**
- Modify: `plugins/session-log/mcp/session_log/storage.py`
- Create: `plugins/session-log/tests/test_indexing.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_indexing.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_indexing.py -v`

Expected: FAIL with "ImportError: cannot import name 'index_session' from 'session_log.storage'"

**Step 3: Add index_session to storage.py**

Read current `plugins/session-log/mcp/session_log/storage.py` and add the function at the end:

```python
def index_session(metadata: dict, db_path: Path | None = None) -> None:
    """Index a session in SQLite.

    Args:
        metadata: Session metadata dictionary with required keys:
            - filename, date, project, summary_path
            Optional: branch, duration_minutes, commits_made,
                      files_touched, commands_run, title
        db_path: Optional override for database path (for testing).
    """
    if db_path is None:
        db_path = get_db_path()

    conn = init_db(db_path)

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
    conn.close()
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_indexing.py -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add index_session function for SQLite indexing"
```

---

## Task 3.3: Wire Indexing into SessionEnd Hook

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py`
- Modify: `plugins/session-log/tests/test_session_end_integration.py`

**Step 1: Write the failing test**

Add to `plugins/session-log/tests/test_session_end_integration.py`:
```python
def test_session_end_indexes_session(session_setup, tmp_path):
    """SessionEnd indexes the session in SQLite."""
    from scripts.session_end import handle_session_end
    from session_log.queries import list_sessions

    # Use a temporary database for this test
    db_path = tmp_path / "test_index.db"

    input_data = {
        "session_id": "test-123",
        "transcript_path": str(session_setup["transcript"]),
        "cwd": str(session_setup["project_dir"]),
        "reason": "exit",
    }

    result = handle_session_end(
        input_data,
        state_dir=session_setup["state_dir"],
        db_path=db_path,
    )

    assert result["success"] is True

    # Check session was indexed
    sessions = list_sessions(db_path=db_path)
    assert len(sessions) == 1
    assert sessions[0]["project"] == "project"
    assert sessions[0]["branch"] == "feat/test"
```

**Step 2: Run test to verify it fails**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_session_end_integration.py::test_session_end_indexes_session -v`

Expected: FAIL (handle_session_end doesn't accept db_path parameter)

**Step 3: Update session_end.py to accept db_path and call index_session**

Modify `plugins/session-log/scripts/session_end.py`:

1. Add import:
```python
from session_log.storage import index_session
from session_log.summarizer import calculate_duration_minutes
```

2. Update function signature:
```python
def handle_session_end(input_data: dict, state_dir: Path | None = None, db_path: Path | None = None) -> dict:
```

3. After writing summary file, add indexing call:
```python
    # Index in SQLite
    from datetime import datetime, timezone
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
    index_session(metadata, db_path=db_path)
```

**Step 4: Run test to verify it passes**

Run: `cd plugins/session-log && ./scripts/run_tests.sh tests/test_session_end_integration.py -v`

Expected: PASS (4 tests)

**Step 5: Run all tests**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All tests pass

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): wire SQLite indexing into SessionEnd hook"
```

---

## Task 3.4: Add MCP Server Tools

**Files:**
- Modify: `plugins/session-log/mcp/server.py`

**Step 1: Read current server.py**

Read `plugins/session-log/mcp/server.py` to understand current structure.

**Step 2: Update server.py with list_sessions and get_session tools**

Replace `plugins/session-log/mcp/server.py` with:
```python
"""Session-log MCP server."""

import asyncio
import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from session_log.queries import list_sessions, get_session

server = Server("session-log")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="list_sessions",
            description="List session summaries with optional filtering by project and date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Filter by project name",
                    },
                    "after": {
                        "type": "string",
                        "description": "Filter sessions after this date (YYYY-MM-DD)",
                    },
                    "before": {
                        "type": "string",
                        "description": "Filter sessions before this date (YYYY-MM-DD)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50)",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="get_session",
            description="Get the full content of a specific session by filename",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The session filename",
                    },
                },
                "required": ["filename"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "list_sessions":
        results = list_sessions(
            project=arguments.get("project"),
            after=arguments.get("after"),
            before=arguments.get("before"),
            limit=arguments.get("limit", 50),
        )
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "get_session":
        filename = arguments.get("filename")
        if not filename:
            return [TextContent(type="text", text="Error: filename required")]

        session = get_session(filename)
        if session is None:
            return [TextContent(type="text", text=f"Session not found: {filename}")]

        # Read the actual markdown content
        summary_path = session.get("summary_path")
        if summary_path and Path(summary_path).exists():
            content = Path(summary_path).read_text()
            return [TextContent(type="text", text=content)]

        return [TextContent(type="text", text=json.dumps(session, indent=2))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
```

**Step 3: Run all tests to ensure nothing broke**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All tests pass

**Step 4: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add list_sessions and get_session MCP tools"
```

---

## Task 3.5: Add /list-sessions Command

**Files:**
- Create: `plugins/session-log/commands/list-sessions.md`

**Step 1: Create the command**

Create `plugins/session-log/commands/list-sessions.md`:
```markdown
---
description: Browse and search session history
argument-hint: "[project] [--after DATE] [--before DATE]"
allowed-tools:
  - Read
---

Browse session history for: $ARGUMENTS

Use the session-log MCP `list_sessions` tool to find matching sessions.

Display results in a table format showing:
- Date
- Project
- Branch
- Duration (minutes)
- Title

If a specific session is mentioned, use `get_session` to show its full content.
```

**Step 2: Commit**

```bash
git add plugins/session-log/commands/
git commit -m "feat(session-log): add /list-sessions command"
```

---

## Verification

**Step 1: Run full test suite**

Run: `cd plugins/session-log && ./scripts/run_tests.sh -v`

Expected: All tests pass (should be ~33+ tests)

**Step 2: Verify git log**

Run: `git log --oneline -5`

Expected: 5 commits from this phase

---

## Summary

| Task | Description | Tests Added |
|------|-------------|-------------|
| 3.1 | Queries module | 6 |
| 3.2 | index_session function | 2 |
| 3.3 | Wire indexing into SessionEnd | 1 |
| 3.4 | MCP server tools | 0 (server code) |
| 3.5 | /list-sessions command | 0 (command) |

**Total new tests:** 9
