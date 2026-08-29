from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class InvestigationCaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"


@dataclass
class InvestigationCase:

    case_id: str

    customer_id: str

    account_id: str

    complaint: str

    submitted_at: datetime

    status: InvestigationCaseStatus