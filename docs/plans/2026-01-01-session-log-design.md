# Session-Log Plugin Design

**Date:** 2026-01-01
**Status:** Draft
**Branch:** `feat/session-log`

---

## Overview

**session-log** captures session summaries for historical record and reflection.

### Problem

Sessions end and context disappears. Handoff solves resumption but not history. Users cannot answer "What did I work on last week?" or identify patterns in their work.

### Solution

A plugin that:
1. Auto-generates summaries at session end (SessionEnd hook)
2. Provides query tools via MCP (list, search, filter)
3. Enables reflection through digests and pattern analysis

### Key Differentiators from Handoff

| Aspect | Handoff | Session-log |
|--------|---------|-------------|
| Purpose | Resume work | Review history |
| Content | Next steps, blockers | Accomplishments, metrics |
| Query | Latest only | Search, filter, browse |
| Reflection | None | Patterns, digests |

### Non-Goals

- Team sharing / collaboration
- Real-time logging during sessions
- External service integration
- Custom summary templates
- Mobile/web access

---

## Architecture

### Plugin Structure

```
plugins/session-log/
├── .claude-plugin/plugin.json     # Plugin manifest
├── hooks/hooks.json               # SessionStart + SessionEnd hooks
├── .mcp.json                      # MCP server config
├── src/session_log/
│   ├── __init__.py
│   ├── server.py                  # MCP server (query tools)
│   ├── summarizer.py              # Summary generation from transcript
│   ├── storage.py                 # Markdown file I/O
│   ├── index.py                   # SQLite metadata
│   ├── search.py                  # ChromaDB semantic search
│   └── digest.py                  # Weekly rollup generation
├── commands/
│   ├── summarize.md               # Manual summary trigger
│   ├── list-sessions.md           # Browse/query sessions
│   ├── reflect.md                 # Pattern analysis
│   └── digest.md                  # Generate/view digest
├── scripts/
│   ├── session_start.py           # SessionStart hook script
│   ├── auto_summarize.py          # SessionEnd hook script
│   └── weekly_digest.py           # Standalone for scheduler
├── pyproject.toml
└── tests/
```

### Component Responsibilities

| Component | Role |
|-----------|------|
| SessionStart hook | Records start time + initial git state |
| SessionEnd hook | Parses transcript, generates summary |
| MCP server | Exposes query tools Claude can call |
| Slash commands | User entry points (prompts to Claude) |
| SQLite index | Fast metadata queries |
| ChromaDB | Semantic search |

### Data Flow

**Write path:**
1. SessionStart → record start time to temp file
2. Session runs...
3. SessionEnd → read transcript, generate summary → markdown + SQLite + ChromaDB

**Read path:**
1. User runs `/list-sessions` or asks Claude
2. Claude calls MCP tools
3. MCP queries SQLite/ChromaDB
4. Results returned to user

---

## Data Model

### Storage Locations

| Data | Location |
|------|----------|
| Session summaries | `<project>/.claude/sessions/*.md` |
| SQLite index | `~/.claude/session-log/index.db` |
| ChromaDB embeddings | `~/.claude/session-log/embeddings/` |
| Symlinks | `~/.claude/session-log/sessions/` |
| Weekly digests | `~/.claude/session-log/digests/` |

### Session Summary (Markdown)

**Filename:** `{date}_{time}_{slug}.md` (e.g., `2026-01-01_14-30-00_jwt-auth.md`)

```yaml
---
date: 2026-01-01T14:30:00
duration_minutes: 45
project: my-project
branch: feat/auth
commit_start: abc1234
commit_end: def5678
commits_made: 3
files_touched: 7
commands_run: 23
tags: [auth, security]
---
```

```markdown
# Session: JWT authentication middleware

## Accomplished
- Implemented token generation with RS256 signing
- Added middleware for request authentication
- Fixed edge case in token refresh

## Decisions
- RS256 over HS256: public key verification avoids sharing secrets

## Learnings
- PyJWT requires `cryptography` package for RS256

## Files
src/auth/jwt.py, src/auth/middleware.py, tests/test_auth.py (+4)

## Insight
Security infrastructure session. Pattern: auth work clusters in multi-session bursts.
```

### SQLite Schema

```sql
CREATE TABLE sessions (
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

CREATE INDEX idx_sessions_date ON sessions(date);
CREATE INDEX idx_sessions_project ON sessions(project);
```

### ChromaDB

- **Collection:** `session-log`
- **Embedding source:** title + Accomplished + Decisions + Learnings (concatenated)
- **Metadata:** filename, date, project

### Retention Policy

| Data | Retention |
|------|-----------|
| Session summaries | Forever (source of truth) |
| SQLite index | Forever |
| ChromaDB embeddings | 1 year (regenerable from markdown) |
| Digests | Forever |

---

## Commands & MCP Interface

### Slash Commands

| Command | Purpose | Allowed Tools |
|---------|---------|---------------|
| `/summarize` | Generate summary for current session | Read, Bash, Write |
| `/list-sessions` | Browse/query sessions | Read |
| `/reflect` | Analyze patterns across sessions | Read |
| `/digest` | View or generate weekly digest | Read, Write |

Commands are prompts that guide Claude. Claude autonomously decides to use MCP tools.

**Example command (`list-sessions.md`):**

```markdown
---
description: Browse and search session history
argument-hint: [query]
---

Search session history for: $ARGUMENTS

Use the session-log MCP tools to find matching sessions.
Display results with date, project, and summary.
```

### MCP Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `list_sessions` | project?, after?, before?, limit? | Session metadata list |
| `search_sessions` | query, limit? | Semantic matches |
| `get_session` | filename | Full session content |
| `analyze_patterns` | project?, days? | Pattern analysis |
| `get_digest` | week? | Weekly digest (generates if missing) |

### MCP Configuration (`.mcp.json`)

```json
{
  "mcpServers": {
    "session-log": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/src/session_log/server.py"]
    }
  }
}
```

---

## Hooks

### SessionStart Hook

Records start time and initial git state.

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python ${CLAUDE_PLUGIN_ROOT}/scripts/session_start.py",
        "timeout": 5000
      }]
    }]
  }
}
```

**session_start.py:**
1. Read stdin JSON (session_id, cwd)
2. Record start timestamp
3. Capture initial git state (branch, HEAD commit)
4. Write to temp file for SessionEnd to read

### SessionEnd Hook

Generates session summary from transcript.

```json
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "python ${CLAUDE_PLUGIN_ROOT}/scripts/auto_summarize.py",
        "timeout": 60000
      }]
    }]
  }
}
```

**SessionEnd receives via stdin:**
```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/project/path",
  "reason": "exit"
}
```

**auto_summarize.py workflow:**

1. Read stdin JSON payload
2. Read session start data (from temp file)
3. Parse transcript JSONL:
   - Extract tool calls (Read, Write, Edit, Bash)
   - Extract text responses
   - Calculate timestamps for duration
4. Gather git metrics (commits since start)
5. Generate rich summary
6. Write markdown to `.claude/sessions/`
7. Index in SQLite + ChromaDB
8. Create symlink in global directory

### Transcript Format

The transcript is JSONL with entries:

| Entry Type | Content |
|------------|---------|
| `user` | `message.content` = string |
| `assistant` | `message.content` = array of content blocks |

**Assistant content blocks:**
- `type: "thinking"` — Claude's reasoning
- `type: "tool_use"` — Tool calls with `name`, `input`
- `type: "text"` — Response text

**Extractable data:**
- Files touched: from Read/Write/Edit tool calls
- Commands run: from Bash tool calls
- Duration: first/last timestamps
- Accomplishments: from text content + tool results

### Edge Cases

| Case | Handling |
|------|----------|
| Empty session (<2 messages) | Skip summarization |
| Missing transcript | Log warning, skip |
| Large transcript | Stream parse, don't load all in memory |
| Session end during write | Copy transcript first |

---

## Weekly Digest

### Generation

Digests are generated on-demand, with optional scheduled generation.

| Trigger | Method |
|---------|--------|
| Manual | `/digest` command |
| On-demand | `get_digest()` MCP tool generates if missing |
| Scheduled | User configures launchd/cron (documented) |

### Digest Format

```markdown
---
week: 2025-W52
generated: 2026-01-05T08:00:00
sessions: 12
total_duration_hours: 8.5
---

# Weekly Digest: Dec 30 - Jan 5

## Summary
12 sessions across 3 projects. 8.5 hours total.

## Projects
- my-app (7 sessions): Auth system, API endpoints
- docs (3 sessions): README updates
- scripts (2 sessions): Automation fixes

## Patterns
- Most active: Tuesday, Thursday
- Average session: 42 minutes
- Focus areas: authentication, testing

## Highlights
- Completed JWT auth middleware
- Fixed 3 critical bugs
- Added 15 new tests
```

### `/digest` Command Behavior

```
/digest           → Generate/show current week
/digest last      → Show last week (generate if missing)
/digest 2025-W52  → Show specific week (generate if missing)
/digest setup     → Show launchd/cron setup instructions
```

---

## Reflection

### `/reflect` Command

Triggers conversational pattern analysis via `analyze_patterns()` MCP tool.

**Default:** Analyze last 30 days across all projects.

**Output:** Conversational insights about:
- Work patterns (time of day, session length)
- Topic clusters
- Project distribution
- Recurring themes

### Distinction from `/digest`

| Command | Purpose | Output |
|---------|---------|--------|
| `/digest` | What happened (factual) | Structured markdown |
| `/reflect` | What patterns emerge (analytical) | Conversational |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `mcp` | MCP server SDK |
| `chromadb` | Vector embeddings |
| `sqlite3` | Metadata index (stdlib) |

No additional system dependencies.

---

## Constraints

| Constraint | Handling |
|------------|----------|
| Large transcripts | Stream parse JSONL |
| Slow ChromaDB init | Lazy initialization |
| Plugin portability | All paths use `${CLAUDE_PLUGIN_ROOT}` |
| No scheduled tasks in plugins | Document launchd/cron setup |

---

## Open Questions

None — design validated through brainstorming session.

---

## Implementation Sequence

1. **Phase 1:** Core infrastructure
   - Plugin manifest and structure
   - SQLite schema and basic storage
   - SessionStart/SessionEnd hooks (basic)

2. **Phase 2:** Summary generation
   - Transcript parser
   - Summary generator
   - Markdown writer

3. **Phase 3:** MCP server
   - `list_sessions`, `get_session`
   - Slash commands

4. **Phase 4:** Search
   - ChromaDB integration
   - `search_sessions` tool

5. **Phase 5:** Digest & reflection
   - `get_digest`, `analyze_patterns`
   - `/digest`, `/reflect` commands

6. **Phase 6:** Polish
   - Edge case handling
   - Tests
   - Documentation
