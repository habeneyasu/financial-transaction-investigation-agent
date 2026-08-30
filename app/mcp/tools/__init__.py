"""MCP tools for the financial transaction investigation agent.

Each module in this package exposes tool factory functions that accept the
service dependencies they need. The :func:`register_tools` helper wires the
full set of tools onto an MCP server.
"""

from mcp.server.mcpserver import MCPServer

from app.data.database import Database, db
from app.services.account_service import AccountService
from app.services.customer_service import CustomerService
from app.services.ledger_service import LedgerService
from app.services.transaction_service import TransactionService

from .accounts import compare_account_balance_tool, get_account_tool
from .customers import get_customer_tool
from .ledger import get_ledger_entries_tool
from .transactions import get_transactions_tool

__all__ = [
    "register_tools",
    "get_customer_tool",
    "get_account_tool",
    "compare_account_balance_tool",
    "get_transactions_tool",
    "get_ledger_entries_tool",
]


def register_tools(
    server: MCPServer,
    database: Database | None = None,
) -> MCPServer:
    """Register all investigation MCP tools onto the given server.

    Args:
        server: The MCP server to register the tools on.
        database: Database dependency. Defaults to the global :data:`db`.

    Returns:
        The same server instance with the tools registered.
    """
    database = database or db

    customer_service = CustomerService(database)
    account_service = AccountService(database)
    transaction_service = TransactionService(database)
    ledger_service = LedgerService(database)

    server.add_tool(
        get_customer_tool(customer_service),
        name="get_customer",
        title="Get Customer",
        description="Retrieve customer information by customer ID.",
    )
    server.add_tool(
        get_account_tool(account_service),
        name="get_account",
        title="Get Account",
        description="Retrieve account information by account ID.",
    )
    server.add_tool(
        compare_account_balance_tool(account_service, ledger_service, transaction_service),
        name="compare_account_balance",
        title="Compare Account Balance",
        description=(
            "Deterministically report whether the reported account balance "
            "matches the expected balance derived from its posted ledger entries, "
            "and flag any suspected duplicate debit as advisory evidence."
        ),
    )
    server.add_tool(
        get_transactions_tool(transaction_service),
        name="get_transactions",
        title="Get Transactions",
        description="Retrieve transaction records relevant to an account.",
    )
    server.add_tool(
        get_ledger_entries_tool(ledger_service),
        name="get_ledger_entries",
        title="Get Ledger Entries",
        description="Retrieve ledger entries for an account.",
    )

    return server
