from app.core.exceptions import AccountNotFoundError, DatabaseError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.account import Account

logger = get_logger(__name__)


class AccountService:
    def __init__(self, database: Database):
        self.database = database

    def get_account(self, account_id: str) -> Account:
        try:
            account = self.database.get_account(account_id)

            if account is None:
                logger.warning("Account not found: %s", account_id)
                raise AccountNotFoundError(
                    f"Account with ID {account_id} not found"
                )

            logger.info("Retrieved account: %s", account_id)
            return account

        except AccountNotFoundError:
            raise
        except Exception as exc:
            logger.exception("Failed to retrieve account: %s", account_id)
            raise DatabaseError(
                f"Failed to retrieve account {account_id}"
            ) from exc