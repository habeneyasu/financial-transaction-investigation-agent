from datetime import datetime

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.ledger_entry import LedgerEntry

logger = get_logger(__name__)


class LedgerService:
    def __init__(self, database: Database):
        self.database = database

    def get_ledger_entries(
        self,
        account_id: str,
        as_of: datetime | None = None,
    ) -> list[LedgerEntry]:
        """Retrieve ledger entries for an account."""
        try:
            entries = (
                self.database.get_ledger_entries(account_id)
                if as_of is None
                else self.database.get_ledger_entries(account_id, as_of)
            )

            logger.info(
                "Retrieved %d ledger entries for account: %s",
                len(entries),
                account_id,
            )
            return entries

        except Exception as exc:
            logger.exception(
                "Failed to retrieve ledger entries for account: %s",
                account_id,
            )
            raise DatabaseError(
                f"Failed to retrieve ledger entries for account {account_id}"
            ) from exc

