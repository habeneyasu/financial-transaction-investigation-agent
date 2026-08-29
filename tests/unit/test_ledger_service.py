import pytest
from datetime import datetime
from decimal import Decimal

from app.core.exceptions import DatabaseError
from app.models.ledger_entry import LedgerEntry, LedgerEntryType, LedgerEntryStatus
from app.services.ledger_service import LedgerService


@pytest.fixture
def sample_ledger_entries():
    return [
        LedgerEntry(
            ledger_entry_id="LEDGER-001",
            transaction_id="TXN-001",
            account_id="ACC-001",
            entry_type=LedgerEntryType.DEBIT,
            amount=Decimal("5000"),
            currency="ETB",
            balance_before=Decimal("20000"),
            balance_after=Decimal("15000"),
            created_at=datetime(2024, 5, 1, 10, 30, 0),
            status=LedgerEntryStatus.POSTED,
        ),
        LedgerEntry(
            ledger_entry_id="LEDGER-002",
            transaction_id="TXN-002",
            account_id="ACC-001",
            entry_type=LedgerEntryType.CREDIT,
            amount=Decimal("2000"),
            currency="ETB",
            balance_before=Decimal("15000"),
            balance_after=Decimal("17000"),
            created_at=datetime(2024, 5, 2, 9, 0, 0),
            status=LedgerEntryStatus.POSTED,
        ),
    ]


class TestLedgerService:
    def test_get_ledger_entries_returns_entries(self, sample_ledger_entries):
        database = type(
            "DB", (), {"get_ledger_entries": lambda self, aid: sample_ledger_entries}
        )()
        service = LedgerService(database)

        result = service.get_ledger_entries("ACC-001")

        assert result == sample_ledger_entries

    def test_get_ledger_entries_returns_empty_list_when_none(self):
        database = type("DB", (), {"get_ledger_entries": lambda self, aid: []})()
        service = LedgerService(database)

        result = service.get_ledger_entries("ACC-999")

        assert result == []

    def test_get_ledger_entries_raises_database_error_on_exception(self):
        def raise_error(aid):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_ledger_entries": raise_error})()
        service = LedgerService(database)

        with pytest.raises(DatabaseError):
            service.get_ledger_entries("ACC-001")
