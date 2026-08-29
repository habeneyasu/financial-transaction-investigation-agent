from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Account:
    account_id: str
    customer_id: str
    account_number: str
    account_type: str
    currency: str
    opening_balance: Decimal
    current_balance: Decimal
    opened_at: date
    status: str