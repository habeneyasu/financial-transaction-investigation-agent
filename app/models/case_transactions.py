from dataclasses import dataclass
from enum import Enum


class CaseTransactionRelevance(str, Enum):
    PRIMARY = "PRIMARY"
    RELATED = "RELATED"


@dataclass
class CaseTransaction:

    case_id: str

    transaction_id: str

    relevance: CaseTransactionRelevance