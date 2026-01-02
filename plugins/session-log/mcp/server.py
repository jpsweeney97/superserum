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
