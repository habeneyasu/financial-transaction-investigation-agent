
import pytest
from types import SimpleNamespace

from app.data.database import Database
from app.mcp.client import (
    McpClient,
    McpClientError,
    McpClientRequestError,
)
from app.mcp.server import create_mcp_server


@pytest.fixture
def database(tmp_path):
    db = Database(str(tmp_path / "test_client.db"))
    db.initialize_schema()
    db.seed_data()
    yield db
    db.close()


@pytest.mark.asyncio
class TestMcpClient:

    async def test_lists_all_tools(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            tools = await client.list_tools()

        assert {tool["name"] for tool in tools} == {
            "get_customer",
            "get_account",
            "compare_account_balance",
            "get_transactions",
            "get_ledger_entries",
        }

    async def test_get_account_returns_dict(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            account = await client.get_account("ACC-1001")

        assert isinstance(account, dict)
        assert account["account_id"] == "ACC-1001"

    async def test_get_customer_returns_dict(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            customer = await client.get_customer("CUST-001")

        assert isinstance(customer, dict)
        assert customer["customer_id"] == "CUST-001"

    async def test_get_transactions_returns_list(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            transactions = await client.get_transactions("ACC-1001")

        assert isinstance(transactions, list)
        assert transactions

        assert all(
            txn["to_account_id"] == "ACC-1001"
            or txn["from_account_id"] == "ACC-1001"
            for txn in transactions
        )

    async def test_get_ledger_entries_returns_list(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            entries = await client.get_ledger_entries("ACC-1001")

        assert isinstance(entries, list)
        assert entries[0]["account_id"] == "ACC-1001"

    async def test_compare_account_balance_returns_dict(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            balance = await client.compare_account_balance("ACC-1001")

        assert isinstance(balance, dict)
        assert "expected_balance" in balance
        assert "reported_balance" in balance
        assert "consistent" in balance
        assert "difference" in balance

    async def test_missing_account_raises_request_error(self, database):
        server = create_mcp_server(database)

        async with McpClient(server) as client:
            with pytest.raises(McpClientRequestError):
                await client.get_account("ACC-MISSING")

    async def test_cannot_use_outside_context_manager(self, database):
        server = create_mcp_server(database)
        client = McpClient(server)

        with pytest.raises(McpClientError):
            await client.list_tools()

    async def test_retries_after_transient_mcp_failure(self, database):
        server = create_mcp_server(database)

        async with McpClient(
            server,
            max_retries=2,
            retry_delay_seconds=0,
        ) as client:

            successful_result = SimpleNamespace(
                is_error=False,
                structured_content={
                    "result": {
                        "account_id": "ACC-1001",
                        "status": "ACTIVE",
                    }
                },
                content=[],
            )

            call_count = 0

            async def transient_failure_then_success(
                name,
                arguments,
            ):
                nonlocal call_count
                call_count += 1

                if call_count == 1:
                    raise RuntimeError("Temporary MCP connection failure")

                return successful_result

            client._client.call_tool = transient_failure_then_success

            result = await client.get_account("ACC-1001")

        assert result == {
            "account_id": "ACC-1001",
            "status": "ACTIVE",
        }

        # One initial attempt + one genuine retry.
        assert call_count == 2

