"""MCP tool: retrieve ledger entries for an account."""

from app.mcp.tools._serialization import jsonable, parse_optional_datetime
from app.services.ledger_service import LedgerService


def get_ledger_entries_tool(ledger_service: LedgerService):
    """Build the get_ledger_entries MCP tool bound to the given service."""

    async def get_ledger_entries(
        account_id: str,
        as_of: str | None = None,
    ) -> list[dict]:
        """Retrieve ledger entries for an account."""
        cutoff = parse_optional_datetime(as_of)
        entries = (
            ledger_service.get_ledger_entries(account_id)
            if cutoff is None
            else ledger_service.get_ledger_entries(account_id, cutoff)
        )
        return jsonable(entries)

    return get_ledger_entries
