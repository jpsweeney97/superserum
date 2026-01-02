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
