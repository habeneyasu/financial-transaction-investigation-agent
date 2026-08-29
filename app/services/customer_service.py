
from app.core.exceptions import CustomerNotFoundError, DatabaseError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.customer import Customer

logger = get_logger(__name__)


class CustomerService:
    def __init__(self, database: Database):
        self.database = database

    def get_customer(self, customer_id: str) -> Customer:
        try:
            customer = self.database.get_customer(customer_id)

            if customer is None:
                logger.warning("Customer not found: %s", customer_id)
                raise CustomerNotFoundError(
                    f"Customer with ID {customer_id} not found"
                )

            logger.info("Retrieved customer: %s", customer_id)
            return customer

        except CustomerNotFoundError:
            raise
        except Exception as exc:
            logger.exception("Failed to retrieve customer: %s", customer_id)
            raise DatabaseError(
                f"Failed to retrieve customer {customer_id}"
            ) from exc

