

from dataclasses import dataclass
from datetime import date


@dataclass
class Customer:
    customer_id: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    customer_since: date
    country: str
    status: str

      
