import pytest

from app.mcp.tools import register_tools


@pytest.mark.parametrize("method,path", [("GET", "/mcp/tools"), ("POST", "/mcp/call")])
def test_rest_tool_routes_are_disabled_in_gateway_mode(monkeypatch, method, path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.routes.mcp import router
    from app.config.settings import settings

    monkeypatch.setattr(settings, "mcp_transport", "gateway")
    application = FastAPI()
    application.include_router(router)
    with TestClient(application) as client:
        response = client.request(method, path, json={"name": "get_account", "arguments": {}})
    assert response.status_code == 404


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
