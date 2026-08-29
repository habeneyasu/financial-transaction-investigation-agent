"""MCP tool: retrieve ledger entries for an account."""

from app.mcp.tools._serialization import jsonable
from app.services.ledger_service import LedgerService


def get_ledger_entries_tool(ledger_service: LedgerService):
    """Build the get_ledger_entries MCP tool bound to the given service."""

    async def get_ledger_entries(account_id: str) -> list[dict]:
        """Retrieve ledger entries for an account."""
        entries = ledger_service.get_ledger_entries(account_id)
        return jsonable(entries)

    return get_ledger_entries
