import pytest
from datetime import datetime

from app.core.exceptions import DatabaseError, InvestigationCaseNotFoundError
from app.models.investigation import InvestigationCase, InvestigationCaseStatus
from app.services.investigation_service import InvestigationService


@pytest.fixture
def sample_case():
    return InvestigationCase(
        case_id="CASE-001",
        customer_id="CUST-001",
        account_id="ACC-001",
        complaint="I transferred 5,000 ETB but my balance is incorrect.",
        submitted_at=datetime(2024, 5, 3, 12, 0, 0),
        status=InvestigationCaseStatus.OPEN,
    )


class TestInvestigationService:
    def test_get_investigation_case_returns_case_when_found(self, sample_case):
        database = type("DB", (), {"get_investigation_case": lambda self, cid: sample_case})()
        service = InvestigationService(database)

        result = service.get_investigation_case("CASE-001")

        assert result is sample_case

    def test_get_investigation_case_raises_case_not_found(self):
        database = type("DB", (), {"get_investigation_case": lambda self, cid: None})()
        service = InvestigationService(database)

        with pytest.raises(InvestigationCaseNotFoundError):
            service.get_investigation_case("CASE-999")

    def test_get_investigation_case_raises_database_error_on_exception(self):
        def raise_error(cid):
            raise RuntimeError("boom")

        database = type("DB", (), {"get_investigation_case": raise_error})()
        service = InvestigationService(database)

        with pytest.raises(DatabaseError):
            service.get_investigation_case("CASE-001")

    def test_get_investigation_case_propagates_case_not_found_from_database(self, sample_case):
        def not_found(self, cid):
            raise InvestigationCaseNotFoundError("Investigation case with ID x not found")

        database = type("DB", (), {"get_investigation_case": not_found})()
        service = InvestigationService(database)

        with pytest.raises(InvestigationCaseNotFoundError):
            service.get_investigation_case("CASE-001")
