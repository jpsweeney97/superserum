#!/usr/bin/env python3
"""SessionEnd hook: Generates session summary from transcript."""

import json
import sys
from pathlib import Path


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
