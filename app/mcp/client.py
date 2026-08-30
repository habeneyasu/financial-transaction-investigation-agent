import json
from typing import Any

from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.server.mcpserver import MCPServer

from app.mcp.server import create_mcp_server


class McpClientError(Exception):
    """Base MCP client error."""


class McpClientRequestError(McpClientError):
    """MCP tool request failed."""


class McpClientUnexpectedResultError(McpClientError):
    """MCP tool returned an unexpected result."""


class McpClient:
    """Client for the financial investigation MCP server."""

    def __init__(
        self,
        server: MCPServer | str | StdioServerParameters | None = None,
        *,
        read_timeout_seconds: float | None = None,
    ):
        self._client = Client(
            server or create_mcp_server(),
            read_timeout_seconds=read_timeout_seconds,
        )
        self._entered = False

    async def __aenter__(self):
        await self._client.__aenter__()
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.__aexit__(exc_type, exc_value, traceback)
        self._entered = False

    def _check_context(self):
        if not self._entered:
            raise McpClientError(
                "McpClient must be used with 'async with'."
            )

    async def list_tools(self) -> list[dict[str, Any]]:
        self._check_context()

        result = await self._client.list_tools()

        return [
            {
                "name": tool.name,
                "title": tool.title,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
            }
            for tool in result.tools
        ]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        self._check_context()

        result = await self._client.call_tool(name, arguments)

        if result.is_error:
            raise McpClientRequestError(
                f"Tool {name!r} failed: {_extract_text(result)}"
            )

        if result.structured_content is not None:
            return _unwrap(result.structured_content)

        texts = _extract_text_blocks(result.content)

        if not texts:
            raise McpClientUnexpectedResultError(
                f"Tool {name!r} returned no content."
            )

        return (
            _parse_json(texts[0], name)
            if len(texts) == 1
            else [_parse_json(text, name) for text in texts]
        )

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        return await self.call_tool(
            "get_customer",
            {"customer_id": customer_id},
        )

    async def get_account(self, account_id: str) -> dict[str, Any]:
        return await self.call_tool(
            "get_account",
            {"account_id": account_id},
        )

    async def get_transactions(self, account_id: str) -> list[dict[str, Any]]:
        return await self.call_tool(
            "get_transactions",
            {"account_id": account_id},
        )

    async def get_ledger_entries(
        self,
        account_id: str,
    ) -> list[dict[str, Any]]:
        return await self.call_tool(
            "get_ledger_entries",
            {"account_id": account_id},
        )

    async def compare_account_balance(
        self,
        account_id: str,
    ) -> dict[str, Any]:
        return await self.call_tool(
            "compare_account_balance",
            {"account_id": account_id},
        )


def _extract_text(result: Any) -> str:
    return " ".join(_extract_text_blocks(result.content))


def _extract_text_blocks(content: Any) -> list[str]:
    return [
        block.text
        for block in content or []
        if getattr(block, "text", None) is not None
    ]


def _unwrap(value: Any) -> Any:
    if isinstance(value, dict) and set(value) == {"result"}:
        return value["result"]
    return value


def _parse_json(payload: str, tool_name: str) -> Any:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise McpClientUnexpectedResultError(
            f"Tool {tool_name!r} returned invalid JSON."
        ) from exc