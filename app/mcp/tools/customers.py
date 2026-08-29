"""MCP tool: retrieve customer information by customer ID."""

from app.mcp.tools._serialization import jsonable
from app.services.customer_service import CustomerService


def get_customer_tool(customer_service: CustomerService):
    """Build the get_customer MCP tool bound to the given service."""

    async def get_customer(customer_id: str) -> dict:
        """Retrieve customer information by customer ID."""
        customer = customer_service.get_customer(customer_id)
        return jsonable(customer)

    return get_customer
