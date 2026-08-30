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
                "transaction_id": "TX-0",
            })()
        ]
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: entries}
        )()
        transaction_service = type(
            "S", (), {"get_transactions_for_account": lambda self, aid: []}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service, transaction_service)

        result = await tool("ACC-001")

        # expected = opening(25000) - debit(5000) = 20000 == reported
        assert result["reported_balance"] == "20000"
        assert result["expected_balance"] == "20000"
        assert result["difference"] == "0"
        assert result["consistent"] is True
        assert result["suspected_duplicate_debit"] is None

    async def test_inconsistent_when_balances_differ(self, sample_account, sample_ledger_entries):
        account = sample_account
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: sample_ledger_entries}
        )()
        transaction_service = type(
            "S", (), {"get_transactions_for_account": lambda self, aid: []}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service, transaction_service)

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
                "transaction_id": "TX-0",
            })()
        ]
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: entries}
        )()
        transaction_service = type(
            "S", (), {"get_transactions_for_account": lambda self, aid: []}
        )()
        tool = compare_account_balance_tool(account_service, ledger_service, transaction_service)

        result = await tool("ACC-001")

        # reversed entries are excluded -> expected stays at opening 25000
        assert result["expected_balance"] == "25000"
        assert result["posted_ledger_entries"] == 0
        assert result["consistent"] is False

    async def test_detects_suspected_duplicate_debit_with_raw_difference(self, sample_account):
        account = sample_account
        account_service = type(
            "S", (), {"get_account": lambda self, aid: account}
        )()

        class Tx:
            def __init__(self, tx_id, to_account_id, amount):
                self.transaction_id = tx_id
                self.to_account_id = to_account_id
                self.amount = amount

        # Two duplicate 5000 debits plus an unrelated 3000 debit. The duplicate
        # detection should flag the 5000 pair, while `difference` remains the raw
        # arithmetic (reported - expected), not the duplicate amount.
        debits = [
            type("E", (), {
                "status": "POSTED", "entry_type": "DEBIT",
                "amount": Decimal("5000"), "transaction_id": "TX-1",
            })(),
            type("E", (), {
                "status": "POSTED", "entry_type": "DEBIT",
                "amount": Decimal("5000"), "transaction_id": "TX-2",
            })(),
            type("E", (), {
                "status": "POSTED", "entry_type": "DEBIT",
                "amount": Decimal("3000"), "transaction_id": "TX-3",
            })(),
        ]
        ledger_service = type(
            "S", (), {"get_ledger_entries": lambda self, aid: debits}
        )()
        transaction_service = type(
            "S",
            (),
            {
                "get_transactions_for_account": lambda self, aid: [
                    Tx("TX-1", "ACC-002", Decimal("5000")),
                    Tx("TX-2", "ACC-002", Decimal("5000")),
                    Tx("TX-3", "ACC-003", Decimal("3000")),
                ]
            },
        )()
        tool = compare_account_balance_tool(account_service, ledger_service, transaction_service)

        result = await tool("ACC-001")

        duplicate = result["suspected_duplicate_debit"]
        assert duplicate is not None
        assert duplicate["amount"] == "5000"
        assert duplicate["recipient_account_id"] == "ACC-002"
        assert duplicate["duplicate_count"] == 2
        assert set(duplicate["transaction_ids"]) == {"TX-1", "TX-2"}
        # difference stays the raw balance discrepancy, decoupled from the duplicate
        # expected = opening(25000) - 5000 - 5000 - 3000 = 12000; reported = 20000
        assert result["expected_balance"] == "12000"
        assert result["difference"] == "8000"
        assert result["consistent"] is False
