import pytest

from app.mcp.tools.ledger import get_ledger_entries_tool


@pytest.mark.asyncio
class TestGetLedgerEntriesTool:
    async def test_returns_ledger_entries_for_account(self, sample_ledger_entries):
        service = type(
            "S",
            (),
            {"get_ledger_entries": lambda self, account_id: sample_ledger_entries},
        )()
        tool = get_ledger_entries_tool(service)

        result = await tool("ACC-001")

        assert len(result) == 1
        assert result[0]["ledger_entry_id"] == "LED-001"
        assert result[0]["entry_type"] == "DEBIT"
        assert result[0]["balance_after"] == "20000"

    async def test_returns_empty_list_when_no_entries(self):
        service = type(
            "S",
            (),
            {"get_ledger_entries": lambda self, account_id: []},
        )()
        tool = get_ledger_entries_tool(service)

        result = await tool("ACC-999")

        assert result == []
