from app.core.exceptions import DatabaseError, InvestigationCaseNotFoundError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.investigation import InvestigationCase

logger = get_logger(__name__)


class InvestigationService:
    def __init__(self, database: Database):
        self.database = database

    def get_investigation_case(self, case_id: str) -> InvestigationCase:
        try:
            case = self.database.get_investigation_case(case_id)

            if case is None:
                logger.warning("Investigation case not found: %s", case_id)
                raise InvestigationCaseNotFoundError(
                    f"Investigation case with ID {case_id} not found"
                )

            logger.info("Retrieved investigation case: %s", case_id)
            return case

        except InvestigationCaseNotFoundError:
            raise
        except Exception as exc:
            logger.exception("Failed to retrieve investigation case: %s", case_id)
            raise DatabaseError(
                f"Failed to retrieve investigation case {case_id}"
            ) from exc
