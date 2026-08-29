import pytest
from datetime import datetime
from decimal import Decimal

from app.core.exceptions import TransactionNotFoundError, DatabaseError
from app.models.transaction import Transaction
from app.services.transaction_service import TransactionService


@pytest.fixture
def sample_transaction():
    return Transaction(
        transaction_id="TXN-001",
        from_account_id="ACC-001",
        to_account_id="ACC-002",
        amount=Decimal("5000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2024, 5, 1, 10, 30, 0),
        status="COMPLETED",
        reference="REF-001",
        created_at=datetime(2024, 5, 1, 10, 30, 0),
        completed_at=datetime(2024, 5, 1, 10, 30, 5),
    )


class TestTransactionService:
    def test_get_transaction_returns_transaction_when_found(self, sample_transaction):
        database = type("DB", (), {"get_transaction": lambda self, tid: sample_transaction})()
        service = TransactionService(database)

        result = service.get_transaction("TXN-001")

        assert result is sample_transaction

    def test_get_transaction_raises_transaction_not_found(self):
        database = type("DB", (), {"get_transaction": lambda self, tid: None})()
        service = TransactionService(database)

        with pytest.raises(TransactionNotFoundError):
            service.get_transaction("TXN-999")

    def test_get_transaction_raises_database_error_on_exception(self):
        def raise_error(tid):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_transaction": raise_error})()
        service = TransactionService(database)

        with pytest.raises(DatabaseError):
            service.get_transaction("TXN-001")

    def test_get_transaction_propagates_transaction_not_found_from_database(self, sample_transaction):
        def not_found(self, tid):
            raise TransactionNotFoundError("Transaction with ID x not found")

        database = type("DB", (), {"get_transaction": not_found})()
        service = TransactionService(database)

        with pytest.raises(TransactionNotFoundError):
            service.get_transaction("TXN-001")

    def test_get_transactions_for_account_returns_transactions(self, sample_transaction):
        database = type(
            "DB",
            (),
            {"get_transactions": lambda self, account_id: [sample_transaction]},
        )()
        service = TransactionService(database)

        result = service.get_transactions_for_account("ACC-001")

        assert result == [sample_transaction]

    def test_get_transactions_for_account_returns_empty_list(self):
        database = type("DB", (), {"get_transactions": lambda self, account_id: []})()
        service = TransactionService(database)

        result = service.get_transactions_for_account("ACC-999")

        assert result == []

    def test_get_transactions_for_account_raises_database_error(self):
        def raise_error(self, account_id):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_transactions": raise_error})()
        service = TransactionService(database)

        with pytest.raises(DatabaseError):
            service.get_transactions_for_account("ACC-001")
