# Session-Log Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a plugin that auto-generates session summaries at session end, stores them in markdown + SQLite + ChromaDB, and provides MCP tools for querying session history.

**Architecture:** SessionEnd hook parses transcript JSONL, generates rich summaries, stores in project-local markdown with global SQLite index and ChromaDB embeddings. MCP server exposes query tools that Claude uses autonomously via slash commands.

**Tech Stack:** Python 3.12+, mcp>=1.0.0, chromadb, sqlite3 (stdlib), uv for dependency management

---

## Phase 1: Core Infrastructure

### Task 1.1: Create Plugin Directory Structure

**Files:**
- Create: `plugins/session-log/.claude-plugin/plugin.json`
- Create: `plugins/session-log/.gitignore`
- Create: `plugins/session-log/README.md`

**Step 1: Create directory structure**

```bash
mkdir -p plugins/session-log/.claude-plugin
mkdir -p plugins/session-log/mcp
mkdir -p plugins/session-log/hooks
mkdir -p plugins/session-log/commands
mkdir -p plugins/session-log/scripts
mkdir -p plugins/session-log/tests
```

**Step 2: Write plugin manifest**

Create `plugins/session-log/.claude-plugin/plugin.json`:
```json
{
  "name": "session-log",
  "version": "0.1.0",
  "description": "Captures session summaries for historical record and work pattern reflection",
  "author": {
    "name": "JP"
  },
  "commands": "./commands/"
}
```

**Step 3: Write .gitignore**

Create `plugins/session-log/.gitignore`:
```
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
```

**Step 4: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): initialize plugin structure"
```

---

### Task 1.2: Create MCP Server Scaffold

**Files:**
- Create: `plugins/session-log/mcp/pyproject.toml`
- Create: `plugins/session-log/mcp/__main__.py`
- Create: `plugins/session-log/mcp/server.py`
- Create: `plugins/session-log/.mcp.json`

**Step 1: Write pyproject.toml**

Create `plugins/session-log/mcp/pyproject.toml`:
```toml
[project]
name = "session-log-mcp"
version = "0.1.0"
description = "MCP server for session-log plugin"
requires-python = ">=3.12"
dependencies = [
    "mcp>=1.0.0",
    "chromadb>=0.4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["."]
```

**Step 2: Write __main__.py**

Create `plugins/session-log/mcp/__main__.py`:
```python
from server import main

if __name__ == "__main__":
    main()
```

**Step 3: Write minimal server**

Create `plugins/session-log/mcp/server.py`:
```python
"""Session-log MCP server."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("session-log")


@server.list_tools()
async def list_tools():
    """List available tools."""
    return []


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

**Step 4: Write .mcp.json**

Create `plugins/session-log/.mcp.json`:
```json
{
  "mcpServers": {
    "session-log": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "${CLAUDE_PLUGIN_ROOT}/mcp",
        "python",
        "-m",
        "server"
      ],
      "env": {}
    }
  }
}
```

**Step 5: Verify dependencies install**

```bash
cd plugins/session-log/mcp && uv sync
```

Expected: Dependencies installed successfully.

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add MCP server scaffold"
```

---

### Task 1.3: Create SQLite Schema

**Files:**
- Create: `plugins/session-log/mcp/storage.py`
- Create: `plugins/session-log/tests/test_storage.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_storage.py`:
```python
"""Tests for storage module."""

import tempfile
from pathlib import Path

import pytest


def test_init_db_creates_tables():
    """Database initialization creates required tables."""
    from session_log.storage import init_db

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = init_db(db_path)

        # Check sessions table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        )
        assert cursor.fetchone() is not None

        conn.close()


def test_init_db_creates_indexes():
    """Database initialization creates required indexes."""
    from session_log.storage import init_db

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = init_db(db_path)

        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        assert "idx_sessions_date" in indexes
        assert "idx_sessions_project" in indexes

        conn.close()
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_storage.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write storage module**

Create `plugins/session-log/mcp/session_log/__init__.py`:
```python
"""Session-log MCP server package."""
```

Create `plugins/session-log/mcp/session_log/storage.py`:
```python
"""SQLite storage for session metadata."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    filename TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    project TEXT NOT NULL,
    branch TEXT,
    duration_minutes INTEGER,
    commits_made INTEGER,
    files_touched INTEGER,
    commands_run INTEGER,
    title TEXT,
    summary_path TEXT NOT NULL,
    indexed_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project);
"""


def get_db_path() -> Path:
    """Get the path to the SQLite database."""
    db_dir = Path.home() / ".claude" / "session-log"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "index.db"


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize the database and return a connection."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
```

**Step 4: Update pyproject.toml for package structure**

Edit `plugins/session-log/mcp/pyproject.toml` to add:
```toml
[tool.hatch.build.targets.wheel]
packages = ["session_log"]
```

**Step 5: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_storage.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add SQLite storage schema"
```

---

### Task 1.4: Create SessionStart Hook

**Files:**
- Create: `plugins/session-log/scripts/session_start.py`
- Create: `plugins/session-log/hooks/hooks.json`
- Create: `plugins/session-log/tests/test_session_start.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_session_start.py`:
```python
"""Tests for session_start hook script."""

import json
import tempfile
from pathlib import Path

import pytest


def test_session_start_records_timestamp():
    """SessionStart hook records start timestamp."""
    from scripts.session_start import handle_session_start

    with tempfile.TemporaryDirectory() as tmpdir:
        input_data = {
            "session_id": "test-123",
            "cwd": tmpdir,
            "hook_event_name": "SessionStart",
        }

        result = handle_session_start(input_data, state_dir=Path(tmpdir))

        assert result["success"] is True

        # Check state file was created
        state_file = Path(tmpdir) / "session_state.json"
        assert state_file.exists()

        state = json.loads(state_file.read_text())
        assert "start_time" in state
        assert state["session_id"] == "test-123"
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_session_start.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write session_start script**

Create `plugins/session-log/scripts/session_start.py`:
```python
#!/usr/bin/env python3
"""SessionStart hook: Records start time and initial git state."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


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
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"branch": None, "commit": None}


def get_state_dir() -> Path:
    """Get directory for session state files."""
    state_dir = Path.home() / ".claude" / "session-log" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


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
    state_file.write_text(json.dumps(state, indent=2))

    return {"success": True}


def main():
    """Entry point for hook."""
    try:
        input_data = json.load(sys.stdin)
        result = handle_session_start(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(f"SessionStart hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Make script executable**

```bash
chmod +x plugins/session-log/scripts/session_start.py
```

**Step 5: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_session_start.py -v
```

Expected: PASS

**Step 6: Write hooks.json**

Create `plugins/session-log/hooks/hooks.json`:
```json
{
  "description": "Session logging hooks for capturing session history",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_start.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Step 7: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add SessionStart hook"
```

---

### Task 1.5: Create SessionEnd Hook Scaffold

**Files:**
- Create: `plugins/session-log/scripts/session_end.py`
- Modify: `plugins/session-log/hooks/hooks.json`
- Create: `plugins/session-log/tests/test_session_end.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_session_end.py`:
```python
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
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_session_end.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write session_end scaffold**

Create `plugins/session-log/scripts/session_end.py`:
```python
#!/usr/bin/env python3
"""SessionEnd hook: Generates session summary from transcript."""

import json
import sys
from pathlib import Path


def get_state_dir() -> Path:
    """Get directory for session state files."""
    return Path.home() / ".claude" / "session-log" / "state"


def load_session_state(state_dir: Path | None = None) -> dict | None:
    """Load session state from SessionStart hook."""
    if state_dir is None:
        state_dir = get_state_dir()

    state_file = state_dir / "session_state.json"
    if not state_file.exists():
        return None

    return json.loads(state_file.read_text())


def handle_session_end(input_data: dict) -> dict:
    """Handle SessionEnd event."""
    session_state = load_session_state()

    if session_state is None:
        return {"success": False, "reason": "No session state found"}

    transcript_path = input_data.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        return {"success": False, "reason": "Transcript not found"}

    # TODO: Parse transcript and generate summary
    # This will be implemented in Phase 2

    return {"success": True, "message": "Summary generation not yet implemented"}


def main():
    """Entry point for hook."""
    try:
        input_data = json.load(sys.stdin)
        result = handle_session_end(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(f"SessionEnd hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Make script executable**

```bash
chmod +x plugins/session-log/scripts/session_end.py
```

**Step 5: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_session_end.py -v
```

Expected: PASS

**Step 6: Update hooks.json**

Edit `plugins/session-log/hooks/hooks.json`:
```json
{
  "description": "Session logging hooks for capturing session history",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_start.py",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_end.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

**Step 7: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add SessionEnd hook scaffold"
```

---

## Phase 2: Summary Generation

### Task 2.1: Create Transcript Parser

**Files:**
- Create: `plugins/session-log/mcp/session_log/transcript.py`
- Create: `plugins/session-log/tests/test_transcript.py`
- Create: `plugins/session-log/tests/fixtures/sample_transcript.jsonl`

**Step 1: Create sample transcript fixture**

Create `plugins/session-log/tests/fixtures/sample_transcript.jsonl`:
```jsonl
{"type":"user","message":{"content":"Help me fix the auth bug"}}
{"type":"assistant","message":{"content":[{"type":"thinking","thinking":"Let me look at the auth code"},{"type":"tool_use","name":"Read","input":{"file_path":"src/auth.py"}},{"type":"text","text":"I found the issue in the auth module."}]}}
{"type":"user","message":{"content":"Great, please fix it"}}
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Edit","input":{"file_path":"src/auth.py","old_string":"bug","new_string":"fix"}},{"type":"text","text":"I've fixed the authentication bug."}]}}
```

**Step 2: Write the failing test**

Create `plugins/session-log/tests/test_transcript.py`:
```python
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
```

**Step 3: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_transcript.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 4: Write transcript parser**

Create `plugins/session-log/mcp/session_log/transcript.py`:
```python
"""Transcript parser for extracting session data."""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TranscriptData:
    """Parsed data from a session transcript."""

    tool_calls: list[dict] = field(default_factory=list)
    files_touched: set[str] = field(default_factory=set)
    user_message_count: int = 0
    assistant_message_count: int = 0
    assistant_text: str = ""
    commands_run: list[str] = field(default_factory=list)


def extract_files_from_tool(name: str, input_data: dict) -> set[str]:
    """Extract file paths from tool input."""
    files = set()

    if name in ("Read", "Write", "Edit"):
        if path := input_data.get("file_path"):
            files.add(path)
    elif name == "Glob":
        # Glob doesn't touch specific files, skip
        pass

    return files


def parse_transcript(path: Path) -> TranscriptData:
    """Parse a transcript JSONL file and extract session data."""
    result = TranscriptData()
    text_parts = []

    with open(path) as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)
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

**Step 5: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_transcript.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add transcript parser"
```

---

### Task 2.2: Create Summary Generator

**Files:**
- Create: `plugins/session-log/mcp/session_log/summarizer.py`
- Create: `plugins/session-log/tests/test_summarizer.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_summarizer.py`:
```python
"""Tests for summary generator."""

from datetime import datetime, timezone

import pytest

from session_log.transcript import TranscriptData


@pytest.fixture
def sample_transcript_data():
    """Create sample parsed transcript data."""
    return TranscriptData(
        tool_calls=[
            {"name": "Read", "input": {"file_path": "src/auth.py"}},
            {"name": "Edit", "input": {"file_path": "src/auth.py"}},
            {"name": "Bash", "input": {"command": "pytest tests/"}},
        ],
        files_touched={"src/auth.py"},
        user_message_count=3,
        assistant_message_count=3,
        assistant_text="I found the bug in the auth module. Fixed the issue.",
        commands_run=["pytest tests/"],
    )


@pytest.fixture
def session_state():
    """Create sample session state."""
    return {
        "session_id": "test-123",
        "start_time": "2026-01-01T10:00:00+00:00",
        "cwd": "/home/user/project",
        "branch": "feat/auth-fix",
        "commit_start": "abc1234",
    }


def test_generate_summary_creates_frontmatter(sample_transcript_data, session_state):
    """Summary generator creates valid YAML frontmatter."""
    from session_log.summarizer import generate_summary

    summary = generate_summary(
        transcript_data=sample_transcript_data,
        session_state=session_state,
        commit_end="def5678",
        commits_made=2,
    )

    assert summary.startswith("---\n")
    assert "date:" in summary
    assert "project:" in summary
    assert "branch: feat/auth-fix" in summary


def test_generate_summary_includes_files(sample_transcript_data, session_state):
    """Summary includes files touched section."""
    from session_log.summarizer import generate_summary

    summary = generate_summary(
        transcript_data=sample_transcript_data,
        session_state=session_state,
    )

    assert "## Files" in summary
    assert "src/auth.py" in summary


def test_generate_summary_creates_title(sample_transcript_data, session_state):
    """Summary generates a title from session content."""
    from session_log.summarizer import generate_summary

    summary = generate_summary(
        transcript_data=sample_transcript_data,
        session_state=session_state,
    )

    # Title should be in the markdown
    assert "# Session:" in summary
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_summarizer.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write summary generator**

Create `plugins/session-log/mcp/session_log/summarizer.py`:
```python
"""Summary generation from parsed transcript data."""

from datetime import datetime, timezone
from pathlib import Path

from .transcript import TranscriptData


def generate_title(transcript_data: TranscriptData, branch: str | None) -> str:
    """Generate a session title from content."""
    # Use branch name as hint if available
    if branch and branch not in ("main", "master"):
        # Convert branch name to title
        # feat/auth-fix -> auth fix
        parts = branch.split("/")[-1].replace("-", " ").replace("_", " ")
        return parts.title()

    # Fall back to first file touched
    if transcript_data.files_touched:
        first_file = sorted(transcript_data.files_touched)[0]
        return Path(first_file).stem.replace("_", " ").title()

    return "Session"


def generate_slug(title: str) -> str:
    """Generate a filename slug from title."""
    return title.lower().replace(" ", "-")[:30]


def calculate_duration_minutes(start_time: str, end_time: datetime) -> int:
    """Calculate session duration in minutes."""
    start = datetime.fromisoformat(start_time)
    delta = end_time - start
    return max(1, int(delta.total_seconds() / 60))


def generate_summary(
    transcript_data: TranscriptData,
    session_state: dict,
    commit_end: str | None = None,
    commits_made: int = 0,
    end_time: datetime | None = None,
) -> str:
    """Generate a session summary markdown document."""
    if end_time is None:
        end_time = datetime.now(timezone.utc)

    start_time = session_state.get("start_time", end_time.isoformat())
    branch = session_state.get("branch")
    project = Path(session_state.get("cwd", ".")).name

    title = generate_title(transcript_data, branch)
    duration = calculate_duration_minutes(start_time, end_time)

    # Build frontmatter
    frontmatter_lines = [
        "---",
        f"date: {start_time}",
        f"duration_minutes: {duration}",
        f"project: {project}",
    ]

    if branch:
        frontmatter_lines.append(f"branch: {branch}")
    if session_state.get("commit_start"):
        frontmatter_lines.append(f"commit_start: {session_state['commit_start']}")
    if commit_end:
        frontmatter_lines.append(f"commit_end: {commit_end}")
    if commits_made:
        frontmatter_lines.append(f"commits_made: {commits_made}")

    frontmatter_lines.extend([
        f"files_touched: {len(transcript_data.files_touched)}",
        f"commands_run: {len(transcript_data.commands_run)}",
        "---",
    ])

    # Build content
    content_lines = [
        "",
        f"# Session: {title}",
        "",
        "## Accomplished",
        "",
        "- Session summary pending analysis",
        "",
        "## Files",
        "",
    ]

    if transcript_data.files_touched:
        files = sorted(transcript_data.files_touched)
        if len(files) <= 5:
            content_lines.append(", ".join(files))
        else:
            content_lines.append(", ".join(files[:5]) + f" (+{len(files) - 5})")
    else:
        content_lines.append("No files modified")

    content_lines.append("")

    return "\n".join(frontmatter_lines + content_lines)


def get_summary_filename(session_state: dict, title: str) -> str:
    """Generate the summary filename."""
    start_time = session_state.get("start_time", datetime.now(timezone.utc).isoformat())
    dt = datetime.fromisoformat(start_time)
    date_str = dt.strftime("%Y-%m-%d_%H-%M-%S")
    slug = generate_slug(title)
    return f"{date_str}_{slug}.md"
```

**Step 4: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_summarizer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add summary generator"
```

---

### Task 2.3: Wire Summary Generation into SessionEnd Hook

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py`
- Create: `plugins/session-log/tests/test_session_end_integration.py`

**Step 1: Write the failing integration test**

Create `plugins/session-log/tests/test_session_end_integration.py`:
```python
"""Integration tests for SessionEnd hook."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def session_setup(tmp_path):
    """Set up session state and transcript."""
    # Create state file
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state = {
        "session_id": "test-123",
        "start_time": "2026-01-01T10:00:00+00:00",
        "cwd": str(tmp_path / "project"),
        "branch": "feat/test",
        "commit_start": "abc1234",
    }
    (state_dir / "session_state.json").write_text(json.dumps(state))

    # Create project dir
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".claude").mkdir()
    (project_dir / ".claude" / "sessions").mkdir()

    # Create transcript
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        '{"type":"user","message":{"content":"Fix the bug"}}\n'
        '{"type":"assistant","message":{"content":[{"type":"text","text":"Done!"}]}}\n'
    )

    return {
        "state_dir": state_dir,
        "project_dir": project_dir,
        "transcript": transcript,
        "state": state,
    }


def test_session_end_creates_summary_file(session_setup):
    """SessionEnd creates a summary markdown file."""
    from scripts.session_end import handle_session_end, load_session_state

    input_data = {
        "session_id": "test-123",
        "transcript_path": str(session_setup["transcript"]),
        "cwd": str(session_setup["project_dir"]),
        "reason": "exit",
    }

    result = handle_session_end(
        input_data,
        state_dir=session_setup["state_dir"],
    )

    assert result["success"] is True

    # Check summary file was created
    sessions_dir = session_setup["project_dir"] / ".claude" / "sessions"
    summaries = list(sessions_dir.glob("*.md"))
    assert len(summaries) == 1
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_session_end_integration.py -v
```

Expected: FAIL (handle_session_end doesn't create files yet)

**Step 3: Update session_end.py**

Edit `plugins/session-log/scripts/session_end.py`:
```python
#!/usr/bin/env python3
"""SessionEnd hook: Generates session summary from transcript."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add mcp directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))

from session_log.transcript import parse_transcript
from session_log.summarizer import generate_summary, generate_title, get_summary_filename


def get_state_dir() -> Path:
    """Get directory for session state files."""
    return Path.home() / ".claude" / "session-log" / "state"


def load_session_state(state_dir: Path | None = None) -> dict | None:
    """Load session state from SessionStart hook."""
    if state_dir is None:
        state_dir = get_state_dir()

    state_file = state_dir / "session_state.json"
    if not state_file.exists():
        return None

    return json.loads(state_file.read_text())


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

        # Count commits (simplified - would need start commit for accurate count)
        return commit_hash, 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None, 0


def ensure_sessions_dir(cwd: str) -> Path:
    """Ensure .claude/sessions/ directory exists."""
    sessions_dir = Path(cwd) / ".claude" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


def handle_session_end(input_data: dict, state_dir: Path | None = None) -> dict:
    """Handle SessionEnd event."""
    session_state = load_session_state(state_dir)

    if session_state is None:
        return {"success": False, "reason": "No session state found"}

    transcript_path = input_data.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        return {"success": False, "reason": "Transcript not found"}

    cwd = input_data.get("cwd", session_state.get("cwd", "."))

    # Parse transcript
    transcript_data = parse_transcript(Path(transcript_path))

    # Skip empty sessions
    if transcript_data.user_message_count < 2:
        return {"success": True, "reason": "Session too short, skipping"}

    # Get git info
    commit_end, commits_made = get_git_info(cwd)

    # Generate summary
    summary = generate_summary(
        transcript_data=transcript_data,
        session_state=session_state,
        commit_end=commit_end,
        commits_made=commits_made,
    )

    # Write summary file
    title = generate_title(transcript_data, session_state.get("branch"))
    filename = get_summary_filename(session_state, title)

    sessions_dir = ensure_sessions_dir(cwd)
    summary_path = sessions_dir / filename
    summary_path.write_text(summary)

    return {
        "success": True,
        "summary_path": str(summary_path),
    }


def main():
    """Entry point for hook."""
    try:
        input_data = json.load(sys.stdin)
        result = handle_session_end(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(f"SessionEnd hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_session_end_integration.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): wire summary generation into SessionEnd hook"
```

---

## Phase 3: MCP Server Tools

### Task 3.1: Add list_sessions Tool

**Files:**
- Modify: `plugins/session-log/mcp/server.py`
- Create: `plugins/session-log/mcp/session_log/queries.py`
- Create: `plugins/session-log/tests/test_queries.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_queries.py`:
```python
"""Tests for query functions."""

import json
import sqlite3
import tempfile
from datetime import datetime
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
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_queries.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write queries module**

Create `plugins/session-log/mcp/session_log/queries.py`:
```python
"""Query functions for session data."""

import sqlite3
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
    """List sessions with optional filtering."""
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
    """Get a single session by filename."""
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

```bash
cd plugins/session-log && uv run pytest tests/test_queries.py -v
```

Expected: PASS

**Step 5: Update MCP server with tools**

Edit `plugins/session-log/mcp/server.py`:
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

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add list_sessions and get_session MCP tools"
```

---

### Task 3.2: Add list-sessions Command

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
- Duration
- Title

If a specific session is mentioned, use `get_session` to show its full content.
```

**Step 2: Commit**

```bash
git add plugins/session-log/commands/
git commit -m "feat(session-log): add /list-sessions command"
```

---

### Task 3.3: Index Sessions in SQLite on Write

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py`
- Modify: `plugins/session-log/mcp/session_log/storage.py`
- Create: `plugins/session-log/tests/test_indexing.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_indexing.py`:
```python
"""Tests for session indexing."""

import json
import tempfile
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
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_indexing.py -v
```

Expected: FAIL with "ImportError"

**Step 3: Add index_session function to storage.py**

Edit `plugins/session-log/mcp/session_log/storage.py` to add:
```python
def index_session(metadata: dict, db_path: Path | None = None) -> None:
    """Index a session in SQLite."""
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

```bash
cd plugins/session-log && uv run pytest tests/test_indexing.py -v
```

Expected: PASS

**Step 5: Wire indexing into session_end.py**

Edit `plugins/session-log/scripts/session_end.py` to call `index_session` after writing the summary file. Add this import and call after writing the summary:

```python
from session_log.storage import index_session

# After summary_path.write_text(summary):
metadata = {
    "filename": filename,
    "date": session_state.get("start_time"),
    "project": Path(cwd).name,
    "branch": session_state.get("branch"),
    "duration_minutes": calculate_duration_minutes(
        session_state.get("start_time"), datetime.now(timezone.utc)
    ),
    "commits_made": commits_made,
    "files_touched": len(transcript_data.files_touched),
    "commands_run": len(transcript_data.commands_run),
    "title": title,
    "summary_path": str(summary_path),
}
index_session(metadata)
```

**Step 6: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): index sessions in SQLite on write"
```

---

## Phase 4: Semantic Search (ChromaDB)

### Task 4.1: Add ChromaDB Embedding Storage

**Files:**
- Create: `plugins/session-log/mcp/session_log/search.py`
- Create: `plugins/session-log/tests/test_search.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_search.py`:
```python
"""Tests for semantic search."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def chroma_dir(tmp_path):
    """Temporary ChromaDB directory."""
    return tmp_path / "embeddings"


def test_embed_session_stores_document(chroma_dir):
    """embed_session stores document in ChromaDB."""
    from session_log.search import embed_session, get_collection

    embed_session(
        filename="test-session.md",
        content="Implemented JWT authentication with RS256 signing",
        project="my-project",
        date="2026-01-01",
        chroma_dir=chroma_dir,
    )

    collection = get_collection(chroma_dir)
    results = collection.get(ids=["test-session.md"])

    assert len(results["ids"]) == 1


def test_search_sessions_finds_similar(chroma_dir):
    """search_sessions finds semantically similar sessions."""
    from session_log.search import embed_session, search_sessions

    # Add some sessions
    embed_session("auth.md", "Implemented JWT authentication", "proj", "2026-01-01", chroma_dir)
    embed_session("api.md", "Built REST API endpoints", "proj", "2026-01-02", chroma_dir)
    embed_session("docs.md", "Updated README documentation", "proj", "2026-01-03", chroma_dir)

    # Search for auth-related content
    results = search_sessions("authentication security login", chroma_dir=chroma_dir)

    assert len(results) > 0
    # Auth session should be most relevant
    assert results[0]["filename"] == "auth.md"
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_search.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write search module**

Create `plugins/session-log/mcp/session_log/search.py`:
```python
"""Semantic search using ChromaDB."""

from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings


def get_chroma_dir() -> Path:
    """Get ChromaDB storage directory."""
    chroma_dir = Path.home() / ".claude" / "session-log" / "embeddings"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chroma_dir


def get_client(chroma_dir: Path | None = None) -> chromadb.Client:
    """Get ChromaDB client."""
    if chroma_dir is None:
        chroma_dir = get_chroma_dir()

    return chromadb.PersistentClient(
        path=str(chroma_dir),
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection(chroma_dir: Path | None = None):
    """Get or create the session-log collection."""
    client = get_client(chroma_dir)
    return client.get_or_create_collection(
        name="session-log",
        metadata={"description": "Session summaries for semantic search"},
    )


def embed_session(
    filename: str,
    content: str,
    project: str,
    date: str,
    chroma_dir: Path | None = None,
) -> None:
    """Add a session to the ChromaDB collection."""
    collection = get_collection(chroma_dir)

    collection.upsert(
        ids=[filename],
        documents=[content],
        metadatas=[{"project": project, "date": date}],
    )


def search_sessions(
    query: str,
    limit: int = 10,
    chroma_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Search for sessions similar to query."""
    collection = get_collection(chroma_dir)

    results = collection.query(
        query_texts=[query],
        n_results=limit,
    )

    sessions = []
    if results["ids"] and results["ids"][0]:
        for i, filename in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            sessions.append({
                "filename": filename,
                "project": metadata.get("project"),
                "date": metadata.get("date"),
                "distance": results["distances"][0][i] if results["distances"] else None,
            })

    return sessions
```

**Step 4: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_search.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add ChromaDB semantic search"
```

---

### Task 4.2: Add search_sessions MCP Tool

**Files:**
- Modify: `plugins/session-log/mcp/server.py`

**Step 1: Add tool to server**

Edit `plugins/session-log/mcp/server.py` to add the search tool to `list_tools()`:
```python
Tool(
    name="search_sessions",
    description="Semantically search session summaries",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results (default: 10)",
                "default": 10,
            },
        },
        "required": ["query"],
    },
),
```

And add the handler to `call_tool()`:
```python
elif name == "search_sessions":
    from session_log.search import search_sessions as do_search

    query = arguments.get("query", "")
    limit = arguments.get("limit", 10)

    results = do_search(query, limit=limit)
    return [TextContent(type="text", text=json.dumps(results, indent=2))]
```

**Step 2: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add search_sessions MCP tool"
```

---

### Task 4.3: Wire Embedding into SessionEnd

**Files:**
- Modify: `plugins/session-log/scripts/session_end.py`

**Step 1: Add embedding call after indexing**

Edit `plugins/session-log/scripts/session_end.py` to add:
```python
from session_log.search import embed_session

# After index_session(metadata):
embed_content = f"{title}\n\n{transcript_data.assistant_text}"
embed_session(
    filename=filename,
    content=embed_content,
    project=Path(cwd).name,
    date=session_state.get("start_time", ""),
)
```

**Step 2: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): embed sessions in ChromaDB on write"
```

---

## Phase 5: Digest & Reflection

### Task 5.1: Add Weekly Digest Generator

**Files:**
- Create: `plugins/session-log/mcp/session_log/digest.py`
- Create: `plugins/session-log/tests/test_digest.py`

**Step 1: Write the failing test**

Create `plugins/session-log/tests/test_digest.py`:
```python
"""Tests for digest generation."""

from datetime import date

import pytest


def test_get_week_range():
    """get_week_range returns correct start and end dates."""
    from session_log.digest import get_week_range

    # Test with specific date
    start, end = get_week_range(date(2026, 1, 1))

    # Week containing Jan 1, 2026 (Thursday)
    assert start <= date(2026, 1, 1) <= end
    assert (end - start).days == 6


def test_generate_digest_creates_markdown(tmp_path):
    """generate_digest creates markdown with frontmatter."""
    from session_log.digest import generate_digest
    from session_log.storage import init_db

    # Set up test database
    db_path = tmp_path / "test.db"
    init_db(db_path)

    digest = generate_digest(week="2026-W01", db_path=db_path)

    assert digest.startswith("---\n")
    assert "week: 2026-W01" in digest
    assert "# Weekly Digest" in digest
```

**Step 2: Run test to verify it fails**

```bash
cd plugins/session-log && uv run pytest tests/test_digest.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write digest module**

Create `plugins/session-log/mcp/session_log/digest.py`:
```python
"""Weekly digest generation."""

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .queries import list_sessions
from .storage import get_db_path


def get_week_range(d: date | None = None) -> tuple[date, date]:
    """Get start (Monday) and end (Sunday) of the week containing date."""
    if d is None:
        d = date.today()

    # Monday = 0, Sunday = 6
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)

    return start, end


def parse_week(week_str: str) -> tuple[date, date]:
    """Parse ISO week string (e.g., '2026-W01') to date range."""
    year, week = week_str.split("-W")
    # Get first day of year
    jan1 = date(int(year), 1, 1)
    # Find first Monday
    first_monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)
    if jan1.weekday() <= 3:  # Thursday or earlier
        first_monday = jan1 - timedelta(days=jan1.weekday())

    start = first_monday + timedelta(weeks=int(week) - 1)
    end = start + timedelta(days=6)

    return start, end


def get_digest_dir() -> Path:
    """Get directory for digest files."""
    digest_dir = Path.home() / ".claude" / "session-log" / "digests"
    digest_dir.mkdir(parents=True, exist_ok=True)
    return digest_dir


def generate_digest(
    week: str | None = None,
    db_path: Path | None = None,
) -> str:
    """Generate a weekly digest."""
    if db_path is None:
        db_path = get_db_path()

    if week is None:
        today = date.today()
        week = f"{today.year}-W{today.isocalendar()[1]:02d}"

    start, end = parse_week(week)

    sessions = list_sessions(
        after=start.isoformat(),
        before=end.isoformat(),
        limit=1000,
        db_path=db_path,
    )

    # Calculate stats
    total_duration = sum(s.get("duration_minutes", 0) or 0 for s in sessions)
    projects = {}
    for s in sessions:
        proj = s.get("project", "unknown")
        projects[proj] = projects.get(proj, 0) + 1

    # Build frontmatter
    lines = [
        "---",
        f"week: {week}",
        f"generated: {datetime.now(timezone.utc).isoformat()}",
        f"sessions: {len(sessions)}",
        f"total_duration_hours: {total_duration / 60:.1f}",
        "---",
        "",
        f"# Weekly Digest: {start.strftime('%b %d')} - {end.strftime('%b %d')}",
        "",
        "## Summary",
        "",
        f"{len(sessions)} sessions across {len(projects)} projects. {total_duration / 60:.1f} hours total.",
        "",
        "## Projects",
        "",
    ]

    for proj, count in sorted(projects.items(), key=lambda x: -x[1]):
        lines.append(f"- {proj} ({count} sessions)")

    if not projects:
        lines.append("No sessions this week.")

    lines.append("")

    return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

```bash
cd plugins/session-log && uv run pytest tests/test_digest.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add weekly digest generator"
```

---

### Task 5.2: Add get_digest MCP Tool and /digest Command

**Files:**
- Modify: `plugins/session-log/mcp/server.py`
- Create: `plugins/session-log/commands/digest.md`

**Step 1: Add tool to server**

Edit `plugins/session-log/mcp/server.py` to add the tool and handler.

**Step 2: Create command**

Create `plugins/session-log/commands/digest.md`:
```markdown
---
description: View or generate weekly session digest
argument-hint: "[week|last|setup]"
allowed-tools:
  - Read
  - Write
---

Generate or view weekly digest for: $ARGUMENTS

Use the session-log MCP `get_digest` tool.

- No argument: Current week
- `last`: Previous week
- `2026-W01`: Specific week
- `setup`: Show launchd/cron setup instructions

Display the digest content or provide setup instructions.
```

**Step 3: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add /digest command and get_digest tool"
```

---

### Task 5.3: Add analyze_patterns MCP Tool and /reflect Command

**Files:**
- Create: `plugins/session-log/mcp/session_log/patterns.py`
- Modify: `plugins/session-log/mcp/server.py`
- Create: `plugins/session-log/commands/reflect.md`

**Step 1: Write patterns module**

Create `plugins/session-log/mcp/session_log/patterns.py`:
```python
"""Pattern analysis across sessions."""

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from .queries import list_sessions
from .storage import get_db_path


def analyze_patterns(
    project: str | None = None,
    days: int = 30,
    db_path: Path | None = None,
) -> dict:
    """Analyze patterns across sessions."""
    if db_path is None:
        db_path = get_db_path()

    after = (date.today() - timedelta(days=days)).isoformat()
    sessions = list_sessions(project=project, after=after, limit=1000, db_path=db_path)

    if not sessions:
        return {"message": "No sessions found in the specified period."}

    # Time patterns
    total_duration = sum(s.get("duration_minutes", 0) or 0 for s in sessions)
    avg_duration = total_duration / len(sessions) if sessions else 0

    # Project distribution
    projects = Counter(s.get("project", "unknown") for s in sessions)

    # Branch patterns
    branches = Counter(s.get("branch", "unknown") for s in sessions)

    return {
        "period_days": days,
        "session_count": len(sessions),
        "total_hours": round(total_duration / 60, 1),
        "avg_session_minutes": round(avg_duration, 1),
        "projects": dict(projects.most_common(10)),
        "branches": dict(branches.most_common(10)),
        "files_touched_total": sum(s.get("files_touched", 0) or 0 for s in sessions),
        "commands_run_total": sum(s.get("commands_run", 0) or 0 for s in sessions),
    }
```

**Step 2: Add tool to server and create command**

Create `plugins/session-log/commands/reflect.md`:
```markdown
---
description: Analyze patterns across your session history
argument-hint: "[days] [project]"
allowed-tools:
  - Read
---

Analyze work patterns for: $ARGUMENTS

Use the session-log MCP `analyze_patterns` tool.

Default: Last 30 days across all projects.

Provide conversational insights about:
- Time patterns (session frequency, duration)
- Project distribution
- Topic clusters from branch names
- Productivity trends
```

**Step 3: Commit**

```bash
git add plugins/session-log/
git commit -m "feat(session-log): add pattern analysis and /reflect command"
```

---

## Phase 6: Polish

### Task 6.1: Add README Documentation

**Files:**
- Create: `plugins/session-log/README.md`

**Step 1: Write comprehensive README**

(Content would detail installation, configuration, commands, MCP tools, and examples)

**Step 2: Commit**

```bash
git add plugins/session-log/README.md
git commit -m "docs(session-log): add comprehensive README"
```

---

### Task 6.2: Run Full Test Suite

**Step 1: Run all tests**

```bash
cd plugins/session-log && uv run pytest tests/ -v --tb=short
```

Expected: All tests pass

**Step 2: Fix any failures**

Address any failing tests before proceeding.

---

### Task 6.3: Test Plugin Installation

**Step 1: Test plugin loading**

```bash
claude --plugin-dir ./plugins/session-log --debug
```

**Step 2: Verify hooks and MCP tools load**

Check that SessionStart/SessionEnd hooks fire and MCP tools are available.

---

### Task 6.4: Final Commit and Branch Cleanup

**Step 1: Ensure all changes committed**

```bash
git status
```

**Step 2: Merge to feature branch**

The implementation branch `impl/session-log` can be merged back to `feat/session-log` when complete.

---

## Execution Notes

**Working directory:** `/Users/jp/Projects/active/claude-code-plugin-development/.worktrees/session-log`

**Test command:** `uv run pytest tests/ -v`

**Key dependencies:**
- mcp>=1.0.0
- chromadb>=0.4.0
- Python 3.12+

**Total tasks:** ~20 discrete implementation tasks across 6 phases
