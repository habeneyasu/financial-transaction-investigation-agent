"""MCP server for the financial transaction investigation agent.

Builds an :class:`MCPServer`, registers the controlled read-only investigation
tools, and provides entry points to run over stdio or streamable HTTP.
"""

from mcp.server import MCPServer

from app.config.settings import settings
from app.data.database import Database, db
from app.mcp.tools import register_tools


def create_mcp_server(database: Database | None = None) -> MCPServer:
    """Create and configure the MCP server with the investigation tools."""
    server = MCPServer(
        name="financial-transaction-investigation",
        title="Financial Transaction Investigation Agent",
        version="0.1.0",
        description=(
            "Controlled read-only tools for investigating customer transaction "
            "disputes against core banking data."
        ),
    )
    register_tools(server, database=database)
    return server


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    arguments = parser.parse_args()
    server = create_mcp_server(db)
    if arguments.transport == "streamable-http":
        server.run(
            transport="streamable-http",
            host=settings.mcp_server_host,
            port=settings.mcp_server_port,
        )
    else:
        server.run(transport="stdio")
