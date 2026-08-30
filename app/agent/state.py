from dataclasses import dataclass, field
from typing import Any

from app.models.investigation import InvestigationCase


@dataclass
class InvestigationState:
    """State accumulated during a financial transaction investigation."""

    case: InvestigationCase | None = None

    customer: dict[str, Any] | None = None
    account: dict[str, Any] | None = None

    transactions: list[dict[str, Any]] = field(default_factory=list)
    ledger_entries: list[dict[str, Any]] = field(default_factory=list)

    balance_comparison: dict[str, Any] | None = None

    findings: list[str] = field(default_factory=list)
    conclusion: str | None = None