from datetime import datetime, date
from decimal import Decimal

from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry, LedgerEntryType, LedgerEntryStatus
from app.models.investigation import InvestigationCase, InvestigationCaseStatus
from app.models.case_transactions import CaseTransaction, CaseTransactionRelevance


# Customers
CUSTOMERS = [
    Customer(
        customer_id="CUST-001",
        first_name="Abebe",
        last_name="Kebede",
        phone_number="+251900000001",
        email="abebe.kebede@example.com",
        customer_since=date(2022, 3, 15),
        country="ET",
        status="ACTIVE"
    ),
    Customer(
        customer_id="CUST-002",
        first_name="Hana",
        last_name="Tesfaye",
        phone_number="+251900000002",
        email="hana.tesfaye@example.com",
        customer_since=date(2023, 7, 10),
        country="ET",
        status="ACTIVE"
    ),
    Customer(
        customer_id="CUST-003",
        first_name="Dawit",
        last_name="Alemu",
        phone_number="+251900000003",
        email="dawit.alemu@example.com",
        customer_since=date(2021, 11, 20),
        country="ET",
        status="ACTIVE"
    ),
    Customer(
        customer_id="CUST-004",
        first_name="Sara",
        last_name="Mohammed",
        phone_number="+251900000004",
        email="sara.mohammed@example.com",
        customer_since=date(2024, 1, 12),
        country="ET",
        status="ACTIVE"
    ),
    Customer(
        customer_id="CUST-005",
        first_name="Yonas",
        last_name="Bekele",
        phone_number="+251900000005",
        email="yonas.bekele@example.com",
        customer_since=date(2020, 9, 5),
        country="ET",
        status="ACTIVE"
    ),
]

# Accounts
ACCOUNTS = [
    Account(
        account_id="ACC-1001",
        customer_id="CUST-001",
        account_number="100100000001",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("25000"),
        current_balance=Decimal("20000"),
        opened_at=date(2022, 3, 20),
        status="ACTIVE"
    ),
    Account(
        account_id="ACC-1002",
        customer_id="CUST-002",
        account_number="100100000002",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("8000"),
        current_balance=Decimal("13000"),
        opened_at=date(2023, 7, 15),
        status="ACTIVE"
    ),
    Account(
        account_id="ACC-1003",
        customer_id="CUST-003",
        account_number="100100000003",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("50000"),
        current_balance=Decimal("48500"),
        opened_at=date(2021, 11, 25),
        status="ACTIVE"
    ),
    Account(
        account_id="ACC-1004",
        customer_id="CUST-004",
        account_number="100100000004",
        account_type="CURRENT",
        currency="ETB",
        opening_balance=Decimal("30000"),
        current_balance=Decimal("28000"),
        opened_at=date(2024, 1, 15),
        status="ACTIVE"
    ),
    Account(
        account_id="ACC-1005",
        customer_id="CUST-005",
        account_number="100100000005",
        account_type="SAVINGS",
        currency="ETB",
        opening_balance=Decimal("15000"),
        current_balance=Decimal("15000"),
        opened_at=date(2020, 9, 10),
        status="ACTIVE"
    ),
]

# Transactions
TRANSACTIONS = [
    Transaction(
        transaction_id="TX-1001",
        from_account_id="ACC-1001",
        to_account_id="ACC-1002",
        amount=Decimal("5000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 27, 9, 15),
        status="SUCCESS",
        reference="REF-001",
        created_at=datetime(2026, 8, 27, 9, 15),
        completed_at=datetime(2026, 8, 27, 9, 15)
    ),
    Transaction(
        transaction_id="TX-1002",
        from_account_id="ACC-1001",
        to_account_id="ACC-1003",
        amount=Decimal("2000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 26, 14, 20),
        status="SUCCESS",
        reference="REF-002",
        created_at=datetime(2026, 8, 26, 14, 20),
        completed_at=datetime(2026, 8, 26, 14, 20)
    ),
    Transaction(
        transaction_id="TX-1003",
        from_account_id="ACC-1002",
        to_account_id="ACC-1001",
        amount=Decimal("1500"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 25, 11, 30),
        status="SUCCESS",
        reference="REF-003",
        created_at=datetime(2026, 8, 25, 11, 30),
        completed_at=datetime(2026, 8, 25, 11, 30)
    ),
    Transaction(
        transaction_id="TX-1004",
        from_account_id="ACC-1001",
        to_account_id="ACC-1002",
        amount=Decimal("5000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 27, 9, 17),
        status="SUCCESS",
        reference="REF-004",
        created_at=datetime(2026, 8, 27, 9, 17),
        completed_at=datetime(2026, 8, 27, 9, 17)
    ),
    Transaction(
        transaction_id="TX-1005",
        from_account_id="ACC-1003",
        to_account_id="ACC-1004",
        amount=Decimal("10000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 27, 16, 0),
        status="FAILED",
        reference="REF-005",
        created_at=datetime(2026, 8, 27, 16, 0),
        completed_at=datetime(2026, 8, 27, 16, 1)
    ),
    Transaction(
        transaction_id="TX-1006",
        from_account_id="ACC-1004",
        to_account_id="ACC-1001",
        amount=Decimal("2000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 28, 10, 10),
        status="SUCCESS",
        reference="REF-006",
        created_at=datetime(2026, 8, 28, 10, 10),
        completed_at=datetime(2026, 8, 28, 10, 10)
    ),
    Transaction(
        transaction_id="TX-1007",
        from_account_id="ACC-1002",
        to_account_id="ACC-1003",
        amount=Decimal("1000"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 28, 12, 0),
        status="REVERSED",
        reference="REF-007",
        created_at=datetime(2026, 8, 28, 12, 0),
        completed_at=datetime(2026, 8, 28, 12, 30)
    ),
    Transaction(
        transaction_id="TX-1008",
        from_account_id="ACC-1003",
        to_account_id="ACC-1002",
        amount=Decimal("2500"),
        currency="ETB",
        transaction_type="TRANSFER",
        transaction_date=datetime(2026, 8, 28, 13, 30),
        status="SUCCESS",
        reference="REF-008",
        created_at=datetime(2026, 8, 28, 13, 30),
        completed_at=datetime(2026, 8, 28, 13, 30)
    ),
]

# Ledger Entries
LEDGER_ENTRIES = [
    LedgerEntry(
        ledger_entry_id="LED-001",
        transaction_id="TX-1001",
        account_id="ACC-1001",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("5000"),
        currency="ETB",
        balance_before=Decimal("25000"),
        balance_after=Decimal("20000"),
        created_at=datetime(2026, 8, 27, 9, 15),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-002",
        transaction_id="TX-1001",
        account_id="ACC-1002",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("5000"),
        currency="ETB",
        balance_before=Decimal("8000"),
        balance_after=Decimal("13000"),
        created_at=datetime(2026, 8, 27, 9, 15),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-003",
        transaction_id="TX-1002",
        account_id="ACC-1001",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("2000"),
        currency="ETB",
        balance_before=Decimal("20000"),
        balance_after=Decimal("18000"),
        created_at=datetime(2026, 8, 26, 14, 20),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-004",
        transaction_id="TX-1002",
        account_id="ACC-1003",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("2000"),
        currency="ETB",
        balance_before=Decimal("48000"),
        balance_after=Decimal("50000"),
        created_at=datetime(2026, 8, 26, 14, 20),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-005",
        transaction_id="TX-1003",
        account_id="ACC-1002",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("1500"),
        currency="ETB",
        balance_before=Decimal("9500"),
        balance_after=Decimal("8000"),
        created_at=datetime(2026, 8, 25, 11, 30),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-006",
        transaction_id="TX-1003",
        account_id="ACC-1001",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("1500"),
        currency="ETB",
        balance_before=Decimal("18500"),
        balance_after=Decimal("20000"),
        created_at=datetime(2026, 8, 25, 11, 30),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-007",
        transaction_id="TX-1004",
        account_id="ACC-1001",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("5000"),
        currency="ETB",
        balance_before=Decimal("20000"),
        balance_after=Decimal("15000"),
        created_at=datetime(2026, 8, 27, 9, 17),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-008",
        transaction_id="TX-1006",
        account_id="ACC-1004",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("2000"),
        currency="ETB",
        balance_before=Decimal("30000"),
        balance_after=Decimal("28000"),
        created_at=datetime(2026, 8, 28, 10, 10),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-009",
        transaction_id="TX-1006",
        account_id="ACC-1001",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("2000"),
        currency="ETB",
        balance_before=Decimal("15000"),
        balance_after=Decimal("17000"),
        created_at=datetime(2026, 8, 28, 10, 10),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-010",
        transaction_id="TX-1007",
        account_id="ACC-1002",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("1000"),
        currency="ETB",
        balance_before=Decimal("13000"),
        balance_after=Decimal("12000"),
        created_at=datetime(2026, 8, 28, 12, 0),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-011",
        transaction_id="TX-1007",
        account_id="ACC-1003",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("1000"),
        currency="ETB",
        balance_before=Decimal("48000"),
        balance_after=Decimal("49000"),
        created_at=datetime(2026, 8, 28, 12, 0),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-012",
        transaction_id="TX-1007",
        account_id="ACC-1002",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("1000"),
        currency="ETB",
        balance_before=Decimal("12000"),
        balance_after=Decimal("13000"),
        created_at=datetime(2026, 8, 28, 12, 30),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-013",
        transaction_id="TX-1007",
        account_id="ACC-1003",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("1000"),
        currency="ETB",
        balance_before=Decimal("49000"),
        balance_after=Decimal("48000"),
        created_at=datetime(2026, 8, 28, 12, 30),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-014",
        transaction_id="TX-1008",
        account_id="ACC-1003",
        entry_type=LedgerEntryType.DEBIT,
        amount=Decimal("2500"),
        currency="ETB",
        balance_before=Decimal("48000"),
        balance_after=Decimal("45500"),
        created_at=datetime(2026, 8, 28, 13, 30),
        status=LedgerEntryStatus.POSTED
    ),
    LedgerEntry(
        ledger_entry_id="LED-015",
        transaction_id="TX-1008",
        account_id="ACC-1002",
        entry_type=LedgerEntryType.CREDIT,
        amount=Decimal("2500"),
        currency="ETB",
        balance_before=Decimal("13000"),
        balance_after=Decimal("15500"),
        created_at=datetime(2026, 8, 28, 13, 30),
        status=LedgerEntryStatus.POSTED
    ),
]

# Investigation Cases
INVESTIGATION_CASES = [
    InvestigationCase(
        case_id="CASE-001",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I transferred 5,000 ETB yesterday but my balance is wrong.",
        submitted_at=datetime(2026, 8, 28, 9, 0),
        status=InvestigationCaseStatus.OPEN
    ),
    InvestigationCase(
        case_id="CASE-002",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="My 10,000 ETB transfer failed. Please check if money was deducted.",
        submitted_at=datetime(2026, 8, 28, 17, 0),
        status=InvestigationCaseStatus.OPEN
    ),
    InvestigationCase(
        case_id="CASE-003",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="A transfer was reversed but I want to know whether my balance was restored.",
        submitted_at=datetime(2026, 8, 29, 9, 0),
        status=InvestigationCaseStatus.OPEN
    ),
]

# Case Transactions
CASE_TRANSACTIONS = [
    CaseTransaction(
        case_id="CASE-001",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY
    ),
    CaseTransaction(
        case_id="CASE-001",
        transaction_id="TX-1004",
        relevance=CaseTransactionRelevance.PRIMARY
    ),
    CaseTransaction(
        case_id="CASE-002",
        transaction_id="TX-1005",
        relevance=CaseTransactionRelevance.PRIMARY
    ),
    CaseTransaction(
        case_id="CASE-003",
        transaction_id="TX-1007",
        relevance=CaseTransactionRelevance.PRIMARY
    ),
]
