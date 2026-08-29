from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaction:
    transaction_id: str
    from_account_id: str
    to_account_id: str
    amount: Decimal
    currency: str
    transaction_type: str
    transaction_date: datetime
    status: str
    reference: str
    created_at: datetime
    completed_at: datetime | None = None