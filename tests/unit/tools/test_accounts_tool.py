import pytest
from decimal import Decimal

from app.mcp.tools.accounts import (
    compare_account_balance_tool,
    get_account_tool,
)


@pytest.mark.asyncio
class TestGetAccountTool:
    async def test_returns_account_as_jsonable_dict(self, sample_account):
        service = type(
            "S", (), {"get_account": lambda self, account_id: sample_account}
        )()
        tool = get_account_tool(service)

        result = await tool("ACC-001")

        assert result["account_id"] == "ACC-001"
        assert result["current_balance"] == "20000"
        assert result["opened_at"] == "2022-03-20"


@pytest.mark.asyncio
class TestCompareAccountBalanceTool:
    async def test_consistent_when_balances_match(self, sample_account):
        account = sample_account
        entries = [
            type("E", (), {
                "status": "POSTED",
                "entry_type": "DEBIT",
                "amount": Decimal("5000"),
            })()
        ]
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: entries}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service)

        result = await tool("ACC-001")

        # expected = opening(25000) - debit(5000) = 20000 == reported
        assert result["reported_balance"] == "20000"
        assert result["expected_balance"] == "20000"
        assert result["difference"] == "0"
        assert result["consistent"] is True

    async def test_inconsistent_when_balances_differ(self, sample_account, sample_ledger_entries):
        account = sample_account
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: sample_ledger_entries}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service)

        result = await tool("ACC-001")

        # expected = opening(25000) - debit(5000) = 20000 == reported
        assert result["expected_balance"] == "20000"
        assert result["reported_balance"] == "20000"
        assert result["consistent"] is True

    async def test_ignores_reversed_entries(self, sample_account):
        account = sample_account
        entries = [
            type("E", (), {
                "status": "REVERSED",
                "entry_type": "DEBIT",
                "amount": Decimal("5000"),
            })()
        ]
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: entries}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service)

        result = await tool("ACC-001")

        # reversed entries are excluded -> expected stays at opening 25000
        assert result["expected_balance"] == "25000"
        assert result["posted_ledger_entries"] == 0
        assert result["consistent"] is False
