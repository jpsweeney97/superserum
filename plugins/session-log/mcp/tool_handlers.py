"""Tool handler logic for session-log MCP server.

This module contains the core tool logic without MCP dependencies,
making it testable with standard pytest without requiring the MCP package.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from session_log.queries import list_sessions as db_list_sessions
from session_log.queries import get_session as db_get_session
from security import validate_summary_path


@dataclass
class ToolResult:
    """Result from a tool call."""

    type: str
    text: str


# Tool definitions for list_tools
TOOL_DEFINITIONS = [
    {
        "name": "list_sessions",
        "description": "List session summaries with optional filtering by project and date range",
        "inputSchema": {
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
    },
    {
        "name": "get_session",
        "description": "Get the full content of a specific session by filename",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The session filename",
                },
            },
            "required": ["filename"],
        },
    },
]


def get_tool_definitions() -> list[dict]:
    """Return tool definitions."""
    return TOOL_DEFINITIONS


def handle_list_sessions(arguments: dict) -> list[ToolResult]:
    """Handle list_sessions tool call."""
    results = db_list_sessions(
        project=arguments.get("project"),
        after=arguments.get("after"),
        before=arguments.get("before"),
        limit=arguments.get("limit", 50),
    )
    return [ToolResult(type="text", text=json.dumps(results, indent=2))]


def handle_get_session(arguments: dict) -> list[ToolResult]:
    """Handle get_session tool call."""
    filename = arguments.get("filename")
    if not filename:
        return [ToolResult(type="text", text="Error: filename required")]

    session = db_get_session(filename)
    if session is None:
        return [ToolResult(type="text", text=f"Session not found: {filename}")]

    # Read the actual markdown content with path validation
    summary_path = session.get("summary_path")
    if summary_path:
        validated_path = validate_summary_path(summary_path)
        if validated_path:
            content = Path(validated_path).read_text()
            return [ToolResult(type="text", text=content)]

    return [ToolResult(type="text", text=json.dumps(session, indent=2))]


def handle_tool(name: str, arguments: dict) -> list[ToolResult]:
    """Route tool call to appropriate handler."""
    if name == "list_sessions":
        return handle_list_sessions(arguments)
    elif name == "get_session":
        return handle_get_session(arguments)
    return [ToolResult(type="text", text=f"Unknown tool: {name}")]
