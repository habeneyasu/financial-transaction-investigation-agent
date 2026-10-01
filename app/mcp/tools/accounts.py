"""MCP tools: retrieve account information and compare account balance."""

from collections import defaultdict
from decimal import Decimal
from typing import Optional

from app.mcp.tools._serialization import jsonable, parse_optional_datetime
from app.models.ledger_entry import LedgerEntryStatus, LedgerEntryType
from app.models.transaction import Transaction
from app.services.account_service import AccountService
from app.services.ledger_service import LedgerService
from app.services.transaction_service import TransactionService


def get_account_tool(account_service: AccountService):
    """Build the get_account MCP tool bound to the given service."""

    async def get_account(account_id: str) -> dict:
        """Retrieve account information by account ID."""
        account = account_service.get_account(account_id)
        return jsonable(account)

    return get_account


def _detect_suspected_duplicate_debit(
    posted_debits: list,
    transaction_lookup: dict[str, Transaction],
) -> Optional[dict]:
    """Detect a suspected duplicate debit among posted debit entries.

    A debit is suspected to be duplicated when the account has two or more
    posted debit entries with the same amount to the same recipient account.
    Returns a description of the duplicate or ``None`` when none is found.
    """
    groups: dict[tuple, list] = defaultdict(list)
    for entry in posted_debits:
        transaction = transaction_lookup.get(entry.transaction_id)
        recipient = transaction.to_account_id if transaction else None
        groups[(entry.amount, recipient)].append(entry)

    for (amount, recipient), entries in groups.items():
        if len(entries) >= 2:
            return {
                "amount": jsonable(amount),
                "recipient_account_id": recipient,
                "duplicate_count": len(entries),
                "transaction_ids": [entry.transaction_id for entry in entries],
            }

    return None


def compare_account_balance_tool(
    account_service: AccountService,
    ledger_service: LedgerService,
    transaction_service: TransactionService,
):
    """Build the compare_account_balance MCP tool.

    Deterministically compares the account's reported balance against the
    expected balance derived from its posted ledger entries. A suspected
    duplicate debit is reported as advisory evidence for the agent to reason
    over; it does not alter the balance comparison itself.
    """

    async def compare_account_balance(
        account_id: str,
        as_of: str | None = None,
    ) -> dict:
        """Compare reported account balance with the ledger-derived expected balance."""
        cutoff = parse_optional_datetime(as_of)
        account = account_service.get_account(account_id)
        entries = (
            ledger_service.get_ledger_entries(account_id)
            if cutoff is None
            else ledger_service.get_ledger_entries(account_id, cutoff)
        )
        transactions = (
            transaction_service.get_transactions_for_account(account_id)
            if cutoff is None
            else transaction_service.get_transactions_for_account(
                account_id,
                cutoff,
            )
        )
        transaction_lookup = {
            transaction.transaction_id: transaction
            for transaction in transactions
        }

        posted_entries = [
            entry
            for entry in entries
            if entry.status == LedgerEntryStatus.POSTED
        ]
        posted_debits = [
            entry
            for entry in posted_entries
            if entry.entry_type == LedgerEntryType.DEBIT
        ]

        expected_balance: Decimal = account.opening_balance
        for entry in posted_entries:
            if entry.entry_type == LedgerEntryType.CREDIT:
                expected_balance += entry.amount
            elif entry.entry_type == LedgerEntryType.DEBIT:
                expected_balance -= entry.amount

        reported_balance: Decimal = account.current_balance
        balance_source = "account_current_balance"
        if cutoff is not None:
            latest_posted_entry = max(
                posted_entries,
                key=lambda entry: entry.created_at,
                default=None,
            )
            reported_balance = (
                latest_posted_entry.balance_after
                if latest_posted_entry is not None
                else account.opening_balance
            )
            balance_source = "latest_posted_ledger_balance"
        difference: Decimal = reported_balance - expected_balance

        suspected_duplicate = _detect_suspected_duplicate_debit(
            posted_debits,
            transaction_lookup,
        )

        return jsonable(
            {
                "account_id": account_id,
                "as_of": cutoff,
                "reported_balance": reported_balance,
                "reported_balance_source": balance_source,
                "expected_balance": expected_balance,
                "difference": difference,
                "consistent": difference == 0,
                "posted_ledger_entries": len(posted_entries),
                "total_ledger_entries": len(entries),
                "suspected_duplicate_debit": suspected_duplicate,
            }
        )

    return compare_account_balance
