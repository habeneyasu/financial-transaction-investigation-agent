from app.core.exceptions import DatabaseError, TransactionNotFoundError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.transaction import Transaction

logger = get_logger(__name__)


class TransactionService:
    def __init__(self, database: Database):
        self.database = database

    def get_transaction(self, transaction_id: str) -> Transaction:
        try:
            transaction = self.database.get_transaction(transaction_id)

            if transaction is None:
                logger.warning("Transaction not found: %s", transaction_id)
                raise TransactionNotFoundError(
                    f"Transaction with ID {transaction_id} not found"
                )

            logger.info("Retrieved transaction: %s", transaction_id)
            return transaction

        except TransactionNotFoundError:
            raise

        except Exception as exc:
            logger.exception(
                "Failed to retrieve transaction: %s",
                transaction_id,
            )
            raise DatabaseError(
                f"Failed to retrieve transaction {transaction_id}"
            ) from exc

    def get_transactions_for_account(self, account_id: str) -> list[Transaction]:
        """Retrieve all transactions associated with an account."""
        try:
            transactions = self.database.get_transactions(account_id)
            logger.info(
                "Retrieved %d transactions for account: %s",
                len(transactions),
                account_id,
            )
            return transactions

        except Exception as exc:
            logger.exception(
                "Failed to retrieve transactions for account: %s",
                account_id,
            )
            raise DatabaseError(
                f"Failed to retrieve transactions for account {account_id}"
            ) from exc