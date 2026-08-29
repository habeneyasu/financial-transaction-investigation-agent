from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class LedgerEntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class LedgerEntryStatus(str, Enum):
    POSTED = "POSTED"
    REVERSED = "REVERSED"


@dataclass
class LedgerEntry:

    ledger_entry_id: str

    transaction_id: str

    account_id: str

    entry_type: LedgerEntryType

    amount: Decimal

    currency: str

    balance_before: Decimal

    balance_after: Decimal

    created_at: datetime

    status: LedgerEntryStatus