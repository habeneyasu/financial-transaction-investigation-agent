import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.account import Account
from app.models.customer import Customer
from app.models.ledger_entry import LedgerEntry, LedgerEntryStatus, LedgerEntryType
from app.models.transaction import Transaction


@pytest.fixture
def sample_customer():
    return Customer(
        customer_id="CUST-001",
        first_name="Abebe",
        last_name="Kebede",
        phone_number="+251911000001",
        email="abebe.kebede@example.com",
        customer_since=date(2021, 3, 15),
        country="ET",
        status="ACTIVE",
    )


@pytest.fixture
def sample_account():
    return Account(
        account_id="ACC-001",
        customer_id="CUST-001",
        account_number="100200300400",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("25000"),
        current_balance=Decimal("20000"),
        opened_at=date(2022, 3, 20),
        status="ACTIVE",
    )


@pytest.fixture
def sample_transactions():
    return [
        Transaction(
            transaction_id="TX-001",
            from_account_id="ACC-001",
            to_account_id="ACC-002",
            amount=Decimal("5000"),
            currency="ETB",
            transaction_type="TRANSFER",
            transaction_date=datetime(2026, 8, 27, 9, 15, 0),
            status="SUCCESS",
            reference="REF-001",
            created_at=datetime(2026, 8, 27, 9, 15, 0),
            completed_at=datetime(2026, 8, 27, 9, 15, 5),
        )
    ]


@pytest.fixture
def sample_ledger_entries():
    return [
        LedgerEntry(
            ledger_entry_id="LED-001",
            transaction_id="TX-001",
            account_id="ACC-001",
            entry_type=LedgerEntryType.DEBIT,
            amount=Decimal("5000"),
            currency="ETB",
            balance_before=Decimal("25000"),
            balance_after=Decimal("20000"),
            created_at=datetime(2026, 8, 27, 9, 15, 0),
            status=LedgerEntryStatus.POSTED,
        )
    ]
