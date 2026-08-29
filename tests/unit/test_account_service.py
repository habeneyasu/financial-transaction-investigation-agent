import pytest
from datetime import date
from decimal import Decimal

from app.core.exceptions import AccountNotFoundError, DatabaseError
from app.models.account import Account
from app.services.account_service import AccountService


@pytest.fixture
def sample_account():
    return Account(
        account_id="ACC-001",
        customer_id="CUST-001",
        account_number="100200300400",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("0"),
        current_balance=Decimal("15000"),
        opened_at=date(2021, 3, 15),
        status="ACTIVE",
    )


class TestAccountService:
    def test_get_account_returns_account_when_found(self, sample_account):
        database = type("DB", (), {"get_account": lambda self, aid: sample_account})()
        service = AccountService(database)

        result = service.get_account("ACC-001")

        assert result is sample_account

    def test_get_account_raises_account_not_found(self):
        database = type("DB", (), {"get_account": lambda self, aid: None})()
        service = AccountService(database)

        with pytest.raises(AccountNotFoundError):
            service.get_account("ACC-999")

    def test_get_account_raises_database_error_on_exception(self):
        def raise_error(aid):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_account": raise_error})()
        service = AccountService(database)

        with pytest.raises(DatabaseError):
            service.get_account("ACC-001")

    def test_get_account_propagates_account_not_found_from_database(self, sample_account):
        def not_found(self, aid):
            raise AccountNotFoundError("Account with ID x not found")

        database = type("DB", (), {"get_account": not_found})()
        service = AccountService(database)

        with pytest.raises(AccountNotFoundError):
            service.get_account("ACC-001")
