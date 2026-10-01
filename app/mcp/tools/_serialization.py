"""Helper utilities for serializing tool results to JSON-safe values."""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


def jsonable(value):
    """Recursively convert a value into a JSON-serializable representation."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if is_dataclass(value):
        value = asdict(value)

    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]

    return str(value)


def parse_optional_datetime(value: str | None) -> datetime | None:
    """Parse an optional ISO 8601 timestamp supplied to an MCP tool."""
    return datetime.fromisoformat(value) if value is not None else None
