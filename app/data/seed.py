from datetime import datetime, date
from decimal import Decimal

from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.ledger_entry import (
    LedgerEntry,
    LedgerEntryType,
    LedgerEntryStatus,
)
from app.models.investigation import (
    InvestigationCase,
    InvestigationCaseStatus,
)
from app.models.case_transactions import (
    CaseTransaction,
    CaseTransactionRelevance,
)


# ============================================================
# Customers
# ============================================================

CUSTOMERS = [
    Customer(
        customer_id="CUST-001",
        first_name="Abebe",
        last_name="Kebede",
        phone_number="+251900000001",
        email="abebe.kebede@example.com",
        customer_since=date(2022, 3, 15),
        country="ET",
        status="ACTIVE",
    ),
    Customer(
        customer_id="CUST-002",
        first_name="Hana",
        last_name="Tesfaye",
        phone_number="+251900000002",
        email="hana.tesfaye@example.com",
        customer_since=date(2023, 7, 10),
        country="ET",
        status="ACTIVE",
    ),
    Customer(
        customer_id="CUST-003",
        first_name="Dawit",
        last_name="Alemu",
        phone_number="+251900000003",
        email="dawit.alemu@example.com",
        customer_since=date(2021, 11, 20),
        country="ET",
        status="ACTIVE",
    ),
    Customer(
        customer_id="CUST-004",
        first_name="Sara",
        last_name="Mohammed",
        phone_number="+251900000004",
        email="sara.mohammed@example.com",
        customer_since=date(2024, 1, 12),
        country="ET",
        status="ACTIVE",
    ),
    Customer(
        customer_id="CUST-005",
        first_name="Yonas",
        last_name="Bekele",
        phone_number="+251900000005",
        email="yonas.bekele@example.com",
        customer_since=date(2020, 9, 5),
        country="ET",
        status="ACTIVE",
    ),
]


# ============================================================
# Accounts
# ============================================================

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
        status="ACTIVE",
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
        status="ACTIVE",
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
        status="ACTIVE",
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
        status="ACTIVE",
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
        status="ACTIVE",
    ),
]


# ============================================================
# Transactions
# ============================================================

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
        completed_at=datetime(2026, 8, 27, 9, 15),
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
        completed_at=datetime(2026, 8, 26, 14, 20),
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
        completed_at=datetime(2026, 8, 25, 11, 30),
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
        completed_at=datetime(2026, 8, 27, 9, 17),
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
        completed_at=datetime(2026, 8, 27, 16, 1),
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
        completed_at=datetime(2026, 8, 28, 10, 10),
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
        completed_at=datetime(2026, 8, 28, 12, 30),
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
        completed_at=datetime(2026, 8, 28, 13, 30),
    ),
]


# ============================================================
# Ledger Entries
# ============================================================

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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
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
        status=LedgerEntryStatus.POSTED,
    ),
]


# ============================================================
# Investigation Cases
# ============================================================

INVESTIGATION_CASES = [
  
    InvestigationCase(
        case_id="CASE-001",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I transferred 5,000 ETB yesterday but my balance is wrong.",
        submitted_at=datetime(2026, 8, 28, 9, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-002",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="My 10,000 ETB transfer failed. Please check if money was deducted.",
        submitted_at=datetime(2026, 8, 28, 17, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-003",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="A transfer was reversed but I want to know whether my balance was restored.",
        submitted_at=datetime(2026, 8, 29, 9, 0),
        status=InvestigationCaseStatus.OPEN,
    ),


    InvestigationCase(
        case_id="CASE-004",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="I received a 5,000 ETB transfer. Please confirm the transaction and the amount credited to my account.",
        submitted_at=datetime(2026, 8, 28, 9, 30),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-005",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I sent 2,000 ETB to another account. Please confirm whether the transfer was completed and my account was debited.",
        submitted_at=datetime(2026, 8, 28, 9, 45),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-006",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="I received 2,000 ETB. Please verify that the money was actually credited to my account.",
        submitted_at=datetime(2026, 8, 28, 10, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-007",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="I sent 1,500 ETB and want to confirm whether it was deducted from my balance.",
        submitted_at=datetime(2026, 8, 28, 10, 15),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-008",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I received 1,500 ETB. Please check the transaction and confirm the credited amount.",
        submitted_at=datetime(2026, 8, 28, 10, 30),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-009",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I see two transfers of 5,000 ETB to the same account only two minutes apart. Please investigate both transactions.",
        submitted_at=datetime(2026, 8, 28, 11, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-010",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="The 10,000 ETB transfer shows as failed. Please determine whether my account was permanently debited.",
        submitted_at=datetime(2026, 8, 28, 11, 15),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-011",
        customer_id="CUST-004",
        account_id="ACC-1004",
        complaint="Someone attempted to transfer 10,000 ETB to my account, but the transfer failed. Please confirm whether any money was credited.",
        submitted_at=datetime(2026, 8, 28, 11, 30),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-012",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I received 2,000 ETB from another account. Please verify the transaction and resulting balance change.",
        submitted_at=datetime(2026, 8, 28, 11, 45),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-013",
        customer_id="CUST-004",
        account_id="ACC-1004",
        complaint="I transferred 2,000 ETB to another account. Please verify that my account was debited correctly.",
        submitted_at=datetime(2026, 8, 28, 12, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-014",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="The 1,000 ETB transfer from my account was reversed. Please check the debit and the subsequent restoration.",
        submitted_at=datetime(2026, 8, 28, 14, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-015",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="I received a 1,000 ETB transfer that was later reversed. Please verify what happened to my balance.",
        submitted_at=datetime(2026, 8, 28, 14, 15),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-016",
        customer_id="CUST-003",
        account_id="ACC-1003",
        complaint="I sent 2,500 ETB to another account. Please confirm the transaction status and amount deducted.",
        submitted_at=datetime(2026, 8, 28, 14, 30),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-017",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="I received 2,500 ETB. Please verify that the amount was credited correctly.",
        submitted_at=datetime(2026, 8, 28, 14, 45),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-018",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="Please review my recent account activity and identify the transfers that affected my balance, including the amounts and direction of each transfer.",
        submitted_at=datetime(2026, 8, 28, 15, 0),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-019",
        customer_id="CUST-002",
        account_id="ACC-1002",
        complaint="Please review my recent transfer activity and explain the successful incoming, outgoing, and reversed transactions involving my account.",
        submitted_at=datetime(2026, 8, 28, 15, 15),
        status=InvestigationCaseStatus.OPEN,
    ),

    InvestigationCase(
        case_id="CASE-020",
        customer_id="CUST-001",
        account_id="ACC-1001",
        complaint="I made two 5,000 ETB transfers to the same account within minutes of each other. Please determine whether both transactions were successfully processed and how they affected my balance.",
        submitted_at=datetime(2026, 8, 28, 15, 30),
        status=InvestigationCaseStatus.OPEN,
    ),
]


# ============================================================
# Case Transactions
#
# Ground-truth transaction relevance for each investigation.
# ============================================================

CASE_TRANSACTIONS = [
    # --------------------------------------------------------
    # Original cases - preserved
    # --------------------------------------------------------

    CaseTransaction(
        case_id="CASE-001",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-001",
        transaction_id="TX-1004",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-002",
        transaction_id="TX-1005",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-003",
        transaction_id="TX-1007",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    # --------------------------------------------------------
    # Additional cases
    # --------------------------------------------------------

    CaseTransaction(
        case_id="CASE-004",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-005",
        transaction_id="TX-1002",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-006",
        transaction_id="TX-1002",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-007",
        transaction_id="TX-1003",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-008",
        transaction_id="TX-1003",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-009",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-009",
        transaction_id="TX-1004",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-010",
        transaction_id="TX-1005",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-011",
        transaction_id="TX-1005",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-012",
        transaction_id="TX-1006",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-013",
        transaction_id="TX-1006",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-014",
        transaction_id="TX-1007",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-015",
        transaction_id="TX-1007",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-016",
        transaction_id="TX-1008",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-017",
        transaction_id="TX-1008",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    # CASE-018 requires investigation of multiple transactions
    # involving ACC-1001.
    CaseTransaction(
        case_id="CASE-018",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-018",
        transaction_id="TX-1002",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-018",
        transaction_id="TX-1003",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-018",
        transaction_id="TX-1004",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-018",
        transaction_id="TX-1006",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    # CASE-019 requires investigation of multiple transactions
    # involving ACC-1002.
    CaseTransaction(
        case_id="CASE-019",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-019",
        transaction_id="TX-1003",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-019",
        transaction_id="TX-1007",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-019",
        transaction_id="TX-1008",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    # CASE-020 is deliberately similar to CASE-009 but asks
    # for both processing status and balance impact.
    CaseTransaction(
        case_id="CASE-020",
        transaction_id="TX-1001",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),

    CaseTransaction(
        case_id="CASE-020",
        transaction_id="TX-1004",
        relevance=CaseTransactionRelevance.PRIMARY,
    ),
]