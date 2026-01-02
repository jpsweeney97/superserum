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
    """Get directory for session state files.

    Returns:
        Path to state directory (~/.claude/session-log/state/).
    """
    return Path.home() / ".claude" / "session-log" / "state"


def load_session_state(state_dir: Path | None = None) -> dict | None:
    """Load session state from SessionStart hook.

    Args:
        state_dir: Optional override for state directory (for testing).

    Returns:
        Dict with session state, or None if state file doesn't exist.
    """
    if state_dir is None:
        state_dir = get_state_dir()

    state_file = state_dir / "session_state.json"
    if not state_file.exists():
        return None

    return json.loads(state_file.read_text())


def get_git_info(cwd: str) -> tuple[str | None, int]:
    """Get current HEAD commit and count of new commits.

    Args:
        cwd: Working directory to run git commands in.

    Returns:
        Tuple of (commit hash, commits made count).
    """
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
    """Ensure .claude/sessions/ directory exists.

    Args:
        cwd: Project working directory.

    Returns:
        Path to sessions directory.
    """
    sessions_dir = Path(cwd) / ".claude" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


def handle_session_end(input_data: dict, state_dir: Path | None = None) -> dict:
    """Handle SessionEnd event.

    Args:
        input_data: Hook input data containing transcript_path, etc.
        state_dir: Optional override for state directory (for testing).

    Returns:
        Dict with 'success' key indicating operation result.
    """
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
