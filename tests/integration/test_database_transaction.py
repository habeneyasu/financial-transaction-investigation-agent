import pytest
from datetime import datetime
from decimal import Decimal

from app.data.database import Database


@pytest.fixture
def database():
    db = Database(db_path=":memory:")
    db.initialize_schema()
    db.seed_data(force=True)
    yield db
    db.close()


class TestDatabaseTransactionLookup:
    def test_get_transaction_returns_seeded_transaction(self, database):
        transaction = database.get_transaction("TX-1001")

        assert transaction is not None
        assert transaction.transaction_id == "TX-1001"
        assert transaction.from_account_id == "ACC-1001"
        assert transaction.to_account_id == "ACC-1002"
        assert transaction.amount == Decimal("5000")
        assert transaction.status == "SUCCESS"

    def test_get_transaction_returns_none_when_missing(self, database):
        assert database.get_transaction("TX-9999") is None

    def test_get_transaction_matches_account_transactions(self, database):
        account_tx = {t.transaction_id for t in database.get_transactions("ACC-1001")}
        assert "TX-1001" in account_tx
        assert database.get_transaction("TX-1001").transaction_id in account_tx

    def test_account_evidence_can_be_limited_to_case_time(self, database):
        cutoff = datetime.fromisoformat("2026-08-28 09:00:00")

        transaction_ids = {
            transaction.transaction_id
            for transaction in database.get_transactions("ACC-1001", cutoff)
        }
        ledger_ids = {
            entry.ledger_entry_id
            for entry in database.get_ledger_entries("ACC-1001", cutoff)
        }

        assert "TX-1006" not in transaction_ids
        assert "LED-009" not in ledger_ids
