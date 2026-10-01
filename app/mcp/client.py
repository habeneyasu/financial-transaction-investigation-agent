import asyncio
import json
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx2
from mcp import Client, MCPError
from mcp.client.stdio import StdioServerParameters
from mcp.client.streamable_http import streamable_http_client
from mcp.server.mcpserver import MCPServer

from app.config.settings import settings
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
        max_retries: int | None = None,
        retry_delay_seconds: float | None = None,
        on_retry: Callable[[str, int, int], None] | None = None,
    ):
        self._read_timeout_seconds = (
            settings.mcp_read_timeout_seconds
            if read_timeout_seconds is None
            else read_timeout_seconds
        )

        self._max_retries = (
            settings.mcp_max_retries
            if max_retries is None
            else max_retries
        )

        self._retry_delay_seconds = (
            settings.mcp_retry_delay_seconds
            if retry_delay_seconds is None
            else retry_delay_seconds
        )

        self._on_retry = on_retry

        if server is None:
            if settings.mcp_transport == "gateway":
                if settings.mcp_gateway_url is None or settings.mcp_gateway_password is None:
                    raise McpClientError("MCP gateway URL and credentials are required")
                server = _gateway_transport(
                    str(settings.mcp_gateway_url),
                    settings.mcp_gateway_username,
                    settings.mcp_gateway_password.get_secret_value(),
                    self._read_timeout_seconds,
                )
            else:
                server = create_mcp_server()

        self._client = Client(
            server,
            read_timeout_seconds=self._read_timeout_seconds,
        )

        self._entered = False

    async def __aenter__(self):
        await self._client.__aenter__()
        self._entered = True
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self._client.__aexit__(
            exc_type,
            exc_value,
            traceback,
        )
        self._entered = False

    def _check_context(self):
        if not self._entered:
            raise McpClientError(
                "McpClient must be used with 'async with'."
            )
    def set_retry_callback(
        self,
        callback: Callable[[str, int, int], None] | None,
    ) -> None:
        """Set the callback invoked when a genuine MCP retry occurs."""
        self._on_retry = callback

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

        for attempt in range(self._max_retries + 1):
            try:
                result = await self._client.call_tool(
                    name,
                    arguments,
                )

                # A tool-level error is deterministic and should not
                # be retried by the client.
                if result.is_error:
                    raise McpClientRequestError(
                        f"Tool {name!r} failed: "
                        f"{_extract_text(result)}"
                    )

                if result.structured_content is not None:
                    return _unwrap(
                        result.structured_content
                    )

                texts = _extract_text_blocks(
                    result.content
                )

                if not texts:
                    raise McpClientUnexpectedResultError(
                        f"Tool {name!r} returned no content."
                    )

                return (
                    _parse_json(texts[0], name)
                    if len(texts) == 1
                    else [
                        _parse_json(text, name)
                        for text in texts
                    ]
                )

            except McpClientRequestError:
                # Deterministic MCP tool/application error.
                # Retrying is not useful.
                raise

            except McpClientUnexpectedResultError:
                # The MCP call completed, but the result was invalid.
                # This is not a transient transport failure.
                raise

            except MCPError as exc:
                raise McpClientRequestError(
                    f"Tool {name!r} rejected by MCP server (code {exc.code})."
                ) from exc

            except Exception as exc:
                # Actual underlying MCP/client failure.
                # Retry only while retry attempts remain.
                if attempt >= self._max_retries:
                    raise McpClientRequestError(
                        f"Tool {name!r} failed after "
                        f"{self._max_retries + 1} attempts: {exc}"
                    ) from exc

                retry_number = attempt + 1

                # Record a retry only when a real retry is occurring.
                if self._on_retry is not None:
                    self._on_retry(
                        name,
                        retry_number,
                        self._max_retries,
                    )

                print(
                    f"MCP tool {name!r} failed "
                    f"(attempt {attempt + 1}/"
                    f"{self._max_retries + 1}). "
                    f"Retrying "
                    f"({retry_number}/"
                    f"{self._max_retries})..."
                )

                if self._retry_delay_seconds > 0:
                    await asyncio.sleep(
                        self._retry_delay_seconds
                    )

    async def get_customer(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        return await self.call_tool(
            "get_customer",
            {"customer_id": customer_id},
        )

    async def get_account(
        self,
        account_id: str,
    ) -> dict[str, Any]:
        return await self.call_tool(
            "get_account",
            {"account_id": account_id},
        )

    async def get_transactions(
        self,
        account_id: str,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]:
        return await self.call_tool(
            "get_transactions",
            _evidence_arguments(account_id, as_of),
        )

    async def get_ledger_entries(
        self,
        account_id: str,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]:
        return await self.call_tool(
            "get_ledger_entries",
            _evidence_arguments(account_id, as_of),
        )

    async def compare_account_balance(
        self,
        account_id: str,
        as_of: datetime | None = None,
    ) -> dict[str, Any]:
        return await self.call_tool(
            "compare_account_balance",
            _evidence_arguments(account_id, as_of),
        )


@asynccontextmanager
async def _gateway_transport(url: str, username: str, password: str, timeout: float):
    async with httpx2.AsyncClient(
        auth=httpx2.BasicAuth(username, password),
        timeout=httpx2.Timeout(timeout),
        trust_env=False,
    ) as http_client:
        async with streamable_http_client(url, http_client=http_client) as streams:
            yield streams


def _evidence_arguments(
    account_id: str,
    as_of: datetime | None,
) -> dict[str, Any]:
    arguments: dict[str, Any] = {"account_id": account_id}
    if as_of is not None:
        arguments["as_of"] = as_of.isoformat()
    return arguments


def _extract_text(result: Any) -> str:
    return " ".join(
        _extract_text_blocks(result.content)
    )


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


def _parse_json(
    payload: str,
    tool_name: str,
) -> Any:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise McpClientUnexpectedResultError(
            f"Tool {tool_name!r} returned invalid JSON."
        ) from exc
