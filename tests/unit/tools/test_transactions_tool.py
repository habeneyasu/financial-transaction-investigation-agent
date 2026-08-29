import pytest

from app.mcp.tools.transactions import get_transactions_tool


@pytest.mark.asyncio
class TestGetTransactionsTool:
    async def test_returns_transactions_for_account(self, sample_transactions):
        service = type(
            "S",
            (),
            {"get_transactions_for_account": lambda self, account_id: sample_transactions},
        )()
        tool = get_transactions_tool(service)

        result = await tool("ACC-001")

        assert len(result) == 1
        assert result[0]["transaction_id"] == "TX-001"
        assert result[0]["amount"] == "5000"
        assert result[0]["currency"] == "ETB"
        assert result[0]["status"] == "SUCCESS"

    async def test_returns_empty_list_when_no_transactions(self):
        service = type(
            "S",
            (),
            {"get_transactions_for_account": lambda self, account_id: []},
        )()
        tool = get_transactions_tool(service)

        result = await tool("ACC-999")

        assert result == []
