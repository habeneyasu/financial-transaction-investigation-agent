import pytest
from datetime import date

from app.core.exceptions import CustomerNotFoundError, DatabaseError
from app.models.customer import Customer
from app.services.customer_service import CustomerService


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


class TestCustomerService:
    def test_get_customer_returns_customer_when_found(self, sample_customer):
        database = type("DB", (), {"get_customer": lambda self, cid: sample_customer})()
        service = CustomerService(database)

        result = service.get_customer("CUST-001")

        assert result is sample_customer

    def test_get_customer_raises_customer_not_found(self):
        database = type("DB", (), {"get_customer": lambda self, cid: None})()
        service = CustomerService(database)

        with pytest.raises(CustomerNotFoundError):
            service.get_customer("CUST-999")

    def test_get_customer_raises_database_error_on_exception(self):
        def raise_error(cid):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_customer": raise_error})()
        service = CustomerService(database)

        with pytest.raises(DatabaseError):
            service.get_customer("CUST-001")

    def test_get_customer_propagates_customer_not_found_from_database(self, sample_customer):
        def not_found(self, cid):
            raise CustomerNotFoundError("Customer with ID x not found")

        database = type("DB", (), {"get_customer": not_found})()
        service = CustomerService(database)

        with pytest.raises(CustomerNotFoundError):
            service.get_customer("CUST-001")
