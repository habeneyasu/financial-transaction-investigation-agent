import pytest

from app.mcp.tools import register_tools


@pytest.mark.asyncio
async def test_register_tools_registers_all_investigation_tools():
    from app.mcp.server import create_mcp_server

    server = create_mcp_server()

    tools = await server.list_tools()
    names = {tool.name for tool in tools}

    assert names == {
        "get_customer",
        "get_account",
        "compare_account_balance",
        "get_transactions",
        "get_ledger_entries",
    }
