"""MCP tool testing routes — list available tools and call them directly."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.mcp.client import McpClient, McpClientRequestError
from app.config.settings import settings


def require_tool_testing_mode():
    if settings.mcp_transport == "gateway":
        raise HTTPException(status_code=404, detail="Tool-testing routes are disabled")


router = APIRouter(
    prefix="/mcp", tags=["mcp"], dependencies=[Depends(require_tool_testing_mode)]
)


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


@router.get("/tools", summary="List all available MCP tools")
async def list_tools() -> list[dict[str, Any]]:
    """Return the name, description, and input/output schema for every registered MCP tool."""
    async with McpClient() as client:
        return await client.list_tools()


@router.post("/call", summary="Call an MCP tool by name")
async def call_tool(request: ToolCallRequest) -> Any:
    """Invoke a named MCP tool with the supplied arguments and return the result."""
    try:
        async with McpClient() as client:
            return await client.call_tool(request.name, request.arguments)
    except McpClientRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
