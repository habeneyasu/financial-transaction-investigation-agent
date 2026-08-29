from app.core.exceptions import CustomerNotFoundError
from app.core.logging import get_logger
from app.data.database import Database
from app.models.customer import Customer


class CustomerService:
    def __init__(self, database: Database):
        self.database = database
        self.logger = get_logger(__name__)

    def get_customer(self, customer_id: str) -> Customer:
        """Retrieve customer by ID.
        
        Args:
            customer_id: The customer ID to retrieve.
            
        Returns:
            The customer object.
            
        Raises:
            CustomerNotFoundError: If customer is not found.
        """
        try:
            customer = self.database.get_customer(customer_id)
            if customer is None:
                self.logger.error(f"Customer not found: {customer_id}")
                raise CustomerNotFoundError(f"Customer with ID {customer_id} not found")
            
            self.logger.info(f"Retrieved customer: {customer_id}")
            return customer
        except Exception as exc:
            if isinstance(exc, CustomerNotFoundError):
                raise
            self.logger.error(f"Failed to retrieve customer {customer_id}: {exc}")
            raise CustomerNotFoundError(f"Failed to retrieve customer {customer_id}") from exc
