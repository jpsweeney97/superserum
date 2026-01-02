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
