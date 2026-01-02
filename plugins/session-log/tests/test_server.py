"""Tests for MCP server security utilities."""

import pytest
from pathlib import Path


class TestGetSessionPathValidation:
    """Test path traversal prevention in get_session."""

    def test_valid_path_within_claude_dir(self, tmp_path):
        """Test that valid paths within .claude are allowed."""
        from security import validate_summary_path

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
        from security import validate_summary_path

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Attempt to traverse outside .claude
        malicious_path = str(claude_dir / ".." / "etc" / "passwd")

        result = validate_summary_path(malicious_path, claude_dir)
        assert result is None

    def test_nonexistent_path_returns_none(self, tmp_path):
        """Test that nonexistent paths return None."""
        from security import validate_summary_path

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        result = validate_summary_path(str(claude_dir / "nonexistent.md"), claude_dir)
        assert result is None

    def test_symlink_escape_blocked(self, tmp_path):
        """Test that symlinks escaping .claude are blocked."""
        from security import validate_summary_path

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
