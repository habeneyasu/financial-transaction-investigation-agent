import pytest

from app.mcp.tools.customers import get_customer_tool


@pytest.mark.asyncio
class TestGetCustomerTool:
    async def test_returns_customer_as_jsonable_dict(self, sample_customer):
        service = type(
            "S", (), {"get_customer": lambda self, customer_id: sample_customer}
        )()
        tool = get_customer_tool(service)

        result = await tool("CUST-001")

        assert result["customer_id"] == "CUST-001"
        assert result["first_name"] == "Abebe"
        assert result["status"] == "ACTIVE"
        assert result["customer_since"] == "2021-03-15"
