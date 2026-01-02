---
date: 2026-01-02T01:30:00
version: 1
git_commit: 6cdf8e0
branch: impl/session-log
repository: superserum
tags: ["plugin", "session-log", "phase3-complete", "pr-review", "fixes-needed"]
---

# Handoff: session-log PR Review Complete, Fixes Needed

## Goal
Address all issues found in PR review before merging

## Status
- **Phase 3:** Complete (34 tests passing)
- **PR:** https://github.com/jpsweeney97/superserum/pull/6
- **Review:** Complete - issues identified

## Resume Instructions

1. `/resume` to load this handoff
2. Use `superpowers:writing-plans` skill to create fix plan
3. Execute plan to address all issues below

## Issues to Address

### Critical (Must Fix)

| # | Issue | File | Lines |
|---|-------|------|-------|
| 1 | Timezone-naive datetime comparison will crash | `summarizer.py` | 31-35 |
| 2 | `__main__.py` wrong import path | `__main__.py` | 1 |
| 3 | Path traversal vulnerability in `get_session` | `server.py` | 84-88 |

### High Priority

| # | Issue | File | Lines |
|---|-------|------|-------|
| 4 | Database connection not closed on exception | `queries.py` | 34-61, 81-95 |
| 5 | Silent JSON parse failures in transcript | `transcript.py` | 39-44 |
| 6 | No database error handling in `index_session` | `storage.py` | 44-84 |
| 7 | Database failure silently ignored | `session_end.py` | 149 |
| 8 | File write failures unhandled | `session_start.py:81`, `session_end.py:131` |
| 9 | No MCP server tests | `server.py` | - |

### Medium Priority

| # | Issue | File | Lines |
|---|-------|------|-------|
| 10 | Inline import inside function | `storage.py` | 59-60 |
| 11 | No logging for git timeout | `session_start.py` | 39-40 |
| 12 | `load_session_state` doesn't handle malformed JSON | `session_end.py` | 27-43 |
| 13 | `datetime.fromisoformat()` unhandled | `summarizer.py` | 33, 109 |
| 14 | Malformed JSON transcript handling untested | `transcript.py` | - |
| 15 | Bash command extraction untested | `transcript.py` | - |

## Suggested Fixes (from reviewers)

### Issue 1: Timezone handling
```python
start = datetime.fromisoformat(start_time)
if start.tzinfo is None:
    start = start.replace(tzinfo=timezone.utc)
```

### Issue 2: __main__.py
Either change to `from .server import main` or remove file (unused by .mcp.json)

### Issue 3: Path traversal
```python
path = Path(summary_path).resolve()
expected_base = Path.home() / ".claude"
if path.is_relative_to(expected_base) and path.exists():
    content = path.read_text()
```

### Issue 4: Connection cleanup
```python
conn = init_db(db_path)
try:
    # ... execute queries ...
finally:
    conn.close()
```

### Issue 5: JSON parse errors
```python
try:
    entry = json.loads(line)
except json.JSONDecodeError as e:
    print(f"Warning: Skipping malformed JSON at line {line_num}: {e}", file=sys.stderr)
    continue
```

### Issue 6-7: Database error handling
Return bool from `index_session()`, check in `session_end.py`, warn if indexing failed

## Working Directory

```bash
cd /Users/jp/Projects/active/superserum/.worktrees/session-log/plugins/session-log
```

## Test Command

```bash
./scripts/run_tests.sh -v
```

## Key Files

```
plugins/session-log/
├── mcp/
│   ├── __main__.py              # Issue 2
│   ├── server.py                # Issues 3, 9
│   └── session_log/
│       ├── queries.py           # Issue 4
│       ├── storage.py           # Issues 6, 10
│       ├── summarizer.py        # Issues 1, 13
│       └── transcript.py        # Issues 5, 14, 15
├── scripts/
│   ├── session_start.py         # Issues 8, 11
│   └── session_end.py           # Issues 7, 8, 12
└── tests/
    └── test_server.py           # Issue 9 (create new)
```
