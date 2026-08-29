"""MCP tools: retrieve account information and compare account balance."""

from decimal import Decimal

from app.mcp.tools._serialization import jsonable
from app.models.ledger_entry import LedgerEntryStatus, LedgerEntryType
from app.services.account_service import AccountService
from app.services.ledger_service import LedgerService


def get_account_tool(account_service: AccountService):
    """Build the get_account MCP tool bound to the given service."""

    async def get_account(account_id: str) -> dict:
        """Retrieve account information by account ID."""
        account = account_service.get_account(account_id)
        return jsonable(account)

    return get_account


def compare_account_balance_tool(
    account_service: AccountService,
    ledger_service: LedgerService,
):
    """Build the compare_account_balance MCP tool.

    Deterministically compares the account's reported balance against the
    expected balance derived from its posted ledger entries.
    """

    async def compare_account_balance(account_id: str) -> dict:
        """Compare reported account balance with the ledger-derived expected balance."""
        account = account_service.get_account(account_id)
        entries = ledger_service.get_ledger_entries(account_id)

        posted_entries = [
            entry
            for entry in entries
            if entry.status == LedgerEntryStatus.POSTED
        ]

        expected_balance: Decimal = account.opening_balance
        for entry in posted_entries:
            if entry.entry_type == LedgerEntryType.CREDIT:
                expected_balance += entry.amount
            elif entry.entry_type == LedgerEntryType.DEBIT:
                expected_balance -= entry.amount

        reported_balance: Decimal = account.current_balance
        difference: Decimal = reported_balance - expected_balance

        return jsonable(
            {
                "account_id": account_id,
                "reported_balance": reported_balance,
                "expected_balance": expected_balance,
                "difference": difference,
                "consistent": difference == 0,
                "posted_ledger_entries": len(posted_entries),
                "total_ledger_entries": len(entries),
            }
        )

    return compare_account_balance
