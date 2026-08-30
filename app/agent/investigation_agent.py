import json
from typing import Any

from app.agent.prompts import INVESTIGATION_PROMPT, SYSTEM_PROMPT
from app.agent.schemas import InvestigationResult
from app.agent.state import InvestigationState
from app.llm.client import LLMClient
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService


class InvestigationAgent:
    """Orchestrates financial transaction investigations."""

    def __init__(
        self,
        investigation_service: InvestigationService,
        mcp_client: McpClient,
        llm_client: LLMClient,
    ):
        self._investigation_service = investigation_service
        self._mcp_client = mcp_client
        self._llm_client = llm_client

    async def investigate(
        self,
        case_id: str,
    ) -> InvestigationResult:
        """Run a complete investigation for an investigation case."""

        # Retrieve the investigation case.
        case = self._investigation_service.get_investigation_case(case_id)

        # Initialize investigation state.
        state = InvestigationState(case=case)

        # Collect customer evidence.
        state.customer = await self._mcp_client.get_customer(
            case.customer_id
        )

        # Collect account evidence.
        state.account = await self._mcp_client.get_account(
            case.account_id
        )

        # Collect transaction evidence.
        state.transactions = await self._mcp_client.get_transactions(
            case.account_id
        )

        # Collect ledger evidence.
        state.ledger_entries = (
            await self._mcp_client.get_ledger_entries(
                case.account_id
            )
        )

        # Perform deterministic balance comparison.
        state.balance_comparison = (
            await self._mcp_client.compare_account_balance(
                case.account_id
            )
        )

        # Build the investigation prompt from the collected evidence.
        prompt = INVESTIGATION_PROMPT.format(
            case=_serialize(state.case),
            customer=_serialize(state.customer),
            account=_serialize(state.account),
            transactions=_serialize(state.transactions),
            ledger_entries=_serialize(state.ledger_entries),
            balance_comparison=_serialize(
                state.balance_comparison
            ),
        )

        # Ask Gemini to analyze the evidence.
        response = await self._llm_client.generate(
            SYSTEM_PROMPT,
            prompt,
        )

        # Validate the LLM response against our application schema.
        return self._parse_result(
            case_id=case_id,
            response=response,
        )

    
    @staticmethod
    def _parse_result(
        case_id: str,
        response: str,
    ) -> InvestigationResult:
        """Parse and validate the structured LLM response."""

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "LLM returned JSON, but the result was not an object."
            )

        data["case_id"] = case_id

        confidence = data.get("confidence")

        if isinstance(confidence, str):
            data["confidence"] = confidence.strip().upper()

        return InvestigationResult.model_validate(data)




def _serialize(value: Any) -> Any:
    """Convert application objects into JSON-compatible values."""

    if value is None:
        return None

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    if hasattr(value, "value"):
        return value.value

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if hasattr(value, "__dataclass_fields__"):
        return {
            key: _serialize(getattr(value, key))
            for key in value.__dataclass_fields__
        }

    return value