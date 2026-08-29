import sqlite3
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Optional

from app.data.seed import (
    CUSTOMERS,
    ACCOUNTS,
    TRANSACTIONS,
    LEDGER_ENTRIES,
    INVESTIGATION_CASES,
    CASE_TRANSACTIONS,
)
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry, LedgerEntryType, LedgerEntryStatus
from app.models.investigation import InvestigationCase, InvestigationCaseStatus
from app.models.case_transactions import CaseTransaction, CaseTransactionRelevance


class Database:
    def __init__(self, db_path: str = "core_banking.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establish database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def initialize_schema(self) -> None:
        """Create database tables from schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()

    def reset_database(self) -> None:
        """Drop all tables and recreate schema."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Drop tables in reverse order of dependencies
        cursor.execute("DROP TABLE IF EXISTS case_transactions")
        cursor.execute("DROP TABLE IF EXISTS investigation_cases")
        cursor.execute("DROP TABLE IF EXISTS ledger_entries")
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS accounts")
        cursor.execute("DROP TABLE IF EXISTS customers")
        
        conn.commit()
        self.initialize_schema()

    def seed_data(self, force: bool = False) -> None:
        """Populate database with synthetic data.
        
        Args:
            force: If True, reset database before seeding. If False, only insert if empty.
        """
        if force:
            self.reset_database()
        
        conn = self.connect()
        cursor = conn.cursor()

        # Check if database is already seeded
        cursor.execute("SELECT COUNT(*) FROM customers")
        if not force and cursor.fetchone()[0] > 0:
            return  # Database already seeded

        # Seed customers
        for customer in CUSTOMERS:
            cursor.execute(
                """
                INSERT INTO customers 
                (customer_id, first_name, last_name, phone_number, email, customer_since, country, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer.customer_id,
                    customer.first_name,
                    customer.last_name,
                    customer.phone_number,
                    customer.email,
                    customer.customer_since,
                    customer.country,
                    customer.status,
                ),
            )

        # Seed accounts
        for account in ACCOUNTS:
            cursor.execute(
                """
                INSERT INTO accounts 
                (account_id, customer_id, account_number, account_type, currency, opening_balance, current_balance, opened_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account.account_id,
                    account.customer_id,
                    account.account_number,
                    account.account_type,
                    account.currency,
                    str(account.opening_balance),
                    str(account.current_balance),
                    account.opened_at,
                    account.status,
                ),
            )

        # Seed transactions
        for transaction in TRANSACTIONS:
            cursor.execute(
                """
                INSERT INTO transactions 
                (transaction_id, from_account_id, to_account_id, amount, currency, transaction_type, transaction_date, status, reference, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction.transaction_id,
                    transaction.from_account_id,
                    transaction.to_account_id,
                    str(transaction.amount),
                    transaction.currency,
                    transaction.transaction_type,
                    transaction.transaction_date,
                    transaction.status,
                    transaction.reference,
                    transaction.created_at,
                    transaction.completed_at,
                ),
            )

        # Seed ledger entries
        for entry in LEDGER_ENTRIES:
            cursor.execute(
                """
                INSERT INTO ledger_entries 
                (ledger_entry_id, transaction_id, account_id, entry_type, amount, currency, balance_before, balance_after, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.ledger_entry_id,
                    entry.transaction_id,
                    entry.account_id,
                    entry.entry_type.value,
                    str(entry.amount),
                    entry.currency,
                    str(entry.balance_before),
                    str(entry.balance_after),
                    entry.created_at,
                    entry.status.value,
                ),
            )

        # Seed investigation cases
        for case in INVESTIGATION_CASES:
            cursor.execute(
                """
                INSERT INTO investigation_cases 
                (case_id, customer_id, account_id, complaint, submitted_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    case.case_id,
                    case.customer_id,
                    case.account_id,
                    case.complaint,
                    case.submitted_at,
                    case.status.value,
                ),
            )

        # Seed case transactions
        for case_transaction in CASE_TRANSACTIONS:
            cursor.execute(
                """
                INSERT INTO case_transactions 
                (case_id, transaction_id, relevance)
                VALUES (?, ?, ?)
                """,
                (
                    case_transaction.case_id,
                    case_transaction.transaction_id,
                    case_transaction.relevance.value,
                ),
            )

        conn.commit()

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Retrieve customer by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM customers WHERE customer_id = ?", (customer_id,)
        )
        row = cursor.fetchone()
        if row:
            return Customer(
                customer_id=row["customer_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                phone_number=row["phone_number"],
                email=row["email"],
                customer_since=date.fromisoformat(row["customer_since"]),
                country=row["country"],
                status=row["status"],
            )
        return None

    def get_account(self, account_id: str) -> Optional[Account]:
        """Retrieve account by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM accounts WHERE account_id = ?", (account_id,)
        )
        row = cursor.fetchone()
        if row:
            return Account(
                account_id=row["account_id"],
                customer_id=row["customer_id"],
                account_number=row["account_number"],
                account_type=row["account_type"],
                currency=row["currency"],
                opening_balance=Decimal(row["opening_balance"]),
                current_balance=Decimal(row["current_balance"]),
                opened_at=date.fromisoformat(row["opened_at"]),
                status=row["status"],
            )
        return None

    def get_transactions(self, account_id: str) -> list[Transaction]:
        """Retrieve transactions for an account."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transactions 
            WHERE from_account_id = ? OR to_account_id = ?
            ORDER BY transaction_date DESC
            """,
            (account_id, account_id),
        )
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append(
                Transaction(
                    transaction_id=row["transaction_id"],
                    from_account_id=row["from_account_id"],
                    to_account_id=row["to_account_id"],
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    transaction_type=row["transaction_type"],
                    transaction_date=datetime.fromisoformat(row["transaction_date"]),
                    status=row["status"],
                    reference=row["reference"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                )
            )
        return transactions

    def get_ledger_entries(self, account_id: str) -> list[LedgerEntry]:
        """Retrieve ledger entries for an account."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM ledger_entries 
            WHERE account_id = ?
            ORDER BY created_at DESC
            """,
            (account_id,),
        )
        rows = cursor.fetchall()
        entries = []
        for row in rows:
            entries.append(
                LedgerEntry(
                    ledger_entry_id=row["ledger_entry_id"],
                    transaction_id=row["transaction_id"],
                    account_id=row["account_id"],
                    entry_type=LedgerEntryType(row["entry_type"]),
                    amount=Decimal(row["amount"]),
                    currency=row["currency"],
                    balance_before=Decimal(row["balance_before"]),
                    balance_after=Decimal(row["balance_after"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    status=LedgerEntryStatus(row["status"]),
                )
            )
        return entries

    def get_investigation_case(self, case_id: str) -> Optional[InvestigationCase]:
        """Retrieve investigation case by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM investigation_cases WHERE case_id = ?", (case_id,)
        )
        row = cursor.fetchone()
        if row:
            return InvestigationCase(
                case_id=row["case_id"],
                customer_id=row["customer_id"],
                account_id=row["account_id"],
                complaint=row["complaint"],
                submitted_at=datetime.fromisoformat(row["submitted_at"]),
                status=InvestigationCaseStatus(row["status"]),
            )
        return None

    def get_case_transactions(self, case_id: str) -> list[CaseTransaction]:
        """Retrieve transactions associated with an investigation case."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM case_transactions WHERE case_id = ?", (case_id,)
        )
        rows = cursor.fetchall()
        case_transactions = []
        for row in rows:
            case_transactions.append(
                CaseTransaction(
                    case_id=row["case_id"],
                    transaction_id=row["transaction_id"],
                    relevance=CaseTransactionRelevance(row["relevance"]),
                )
            )
        return case_transactions


# Global database instance
db = Database()
