"""MCP tool: retrieve transaction records for an account."""

from app.mcp.tools._serialization import jsonable
from app.services.transaction_service import TransactionService


def get_transactions_tool(transaction_service: TransactionService):
    """Build the get_transactions MCP tool bound to the given service."""

    async def get_transactions(account_id: str) -> list[dict]:
        """Retrieve transaction records relevant to an account."""
        transactions = transaction_service.get_transactions_for_account(account_id)
        return jsonable(transactions)

    return get_transactions
