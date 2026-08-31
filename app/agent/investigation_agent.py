import json
from typing import Any

from app.agent.prompts import (
    INVESTIGATION_PROMPT,
    SYSTEM_PROMPT,
)
from app.agent.schemas import InvestigationResult
from app.agent.state import InvestigationState
from app.agent.trajectory import InvestigationTrajectory
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

        # ---------------------------------------------------------
        # Initialize trajectory recording
        # ---------------------------------------------------------

        trajectory = InvestigationTrajectory(
            case_id=case_id,
        )

        trajectory.record_workflow_start(
            objective=(
                "Investigate the reported financial transaction issue."
            ),
            instructions=(
                "Collect relevant case, account, transaction and ledger "
                "evidence. Use deterministic checks where available. "
                "Produce an evidence-backed investigation result. "
                "Do not execute consequential actions without human approval."
            ),
            evaluation_case=True,
        )

        # ---------------------------------------------------------
        # Connect MCP retry events to the trajectory
        # ---------------------------------------------------------

        # The callback is invoked by McpClient only when an actual
        # transient MCP/client failure causes a retry.

        self._mcp_client.set_retry_callback(
            lambda tool_name, retry_number, max_retries:
            self._record_mcp_retry(
                trajectory=trajectory,
                tool_name=tool_name,
                retry_number=retry_number,
                max_retries=max_retries,
            )
        )

        try:
            # -----------------------------------------------------
            # Retrieve investigation case
            # -----------------------------------------------------

            case = (
                self._investigation_service
                .get_investigation_case(case_id)
            )

            trajectory.record(
                step="case_retrieval",
                action="Retrieve investigation case",
                details={
                    "case_id": case.case_id,
                    "customer_id": case.customer_id,
                    "account_id": case.account_id,
                    "complaint": case.complaint,
                    "submitted_at": _serialize(
                        case.submitted_at
                    ),
                    "status": _serialize(
                        case.status
                    ),
                },
            )

            # -----------------------------------------------------
            # Initialize investigation state
            # -----------------------------------------------------

            state = InvestigationState(
                case=case,
            )

            # -----------------------------------------------------
            # Customer evidence
            # -----------------------------------------------------

            trajectory.record(
                step="customer_evidence_request",
                action="get_customer",
                details={
                    "customer_id": case.customer_id,
                    "source": "MCP",
                },
            )

            state.customer = (
                await self._mcp_client.get_customer(
                    case.customer_id
                )
            )

            trajectory.record(
                step="customer_evidence_response",
                action="get_customer",
                details={
                    "customer_id": case.customer_id,
                    "source": "MCP",
                    "result": _serialize(
                        state.customer
                    ),
                },
            )

            # -----------------------------------------------------
            # Account evidence
            # -----------------------------------------------------

            trajectory.record(
                step="account_evidence_request",
                action="get_account",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                },
            )

            state.account = (
                await self._mcp_client.get_account(
                    case.account_id
                )
            )

            trajectory.record(
                step="account_evidence_response",
                action="get_account",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                    "result": _serialize(
                        state.account
                    ),
                },
            )

            # -----------------------------------------------------
            # Transaction evidence
            # -----------------------------------------------------

            trajectory.record(
                step="transaction_evidence_request",
                action="get_transactions",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                },
            )

            state.transactions = (
                await self._mcp_client.get_transactions(
                    case.account_id
                )
            )

            trajectory.record(
                step="transaction_evidence_response",
                action="get_transactions",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                    "result_count": len(
                        state.transactions
                    ),
                    "result": _serialize(
                        state.transactions
                    ),
                },
            )

            # -----------------------------------------------------
            # Ledger evidence
            # -----------------------------------------------------

            trajectory.record(
                step="ledger_evidence_request",
                action="get_ledger_entries",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                },
            )

            state.ledger_entries = (
                await self._mcp_client.get_ledger_entries(
                    case.account_id
                )
            )

            trajectory.record(
                step="ledger_evidence_response",
                action="get_ledger_entries",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                    "result_count": len(
                        state.ledger_entries
                    ),
                    "result": _serialize(
                        state.ledger_entries
                    ),
                },
            )

            # -----------------------------------------------------
            # Deterministic balance comparison
            # -----------------------------------------------------

            trajectory.record(
                step="balance_comparison_request",
                action="compare_account_balance",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                    "deterministic": True,
                },
            )

            state.balance_comparison = (
                await self._mcp_client.compare_account_balance(
                    case.account_id
                )
            )

            trajectory.record(
                step="balance_comparison_response",
                action="compare_account_balance",
                details={
                    "account_id": case.account_id,
                    "source": "MCP",
                    "deterministic": True,
                    "result": _serialize(
                        state.balance_comparison
                    ),
                },
            )

            # -----------------------------------------------------
            # Build investigation prompt
            # -----------------------------------------------------

            prompt = INVESTIGATION_PROMPT.format(
                case=_serialize(
                    state.case
                ),
                customer=_serialize(
                    state.customer
                ),
                account=_serialize(
                    state.account
                ),
                transactions=_serialize(
                    state.transactions
                ),
                ledger_entries=_serialize(
                    state.ledger_entries
                ),
                balance_comparison=_serialize(
                    state.balance_comparison
                ),
            )

            trajectory.record(
                step="investigation_prompt",
                action="Build investigation prompt",
                details={
                    "evidence_sources": [
                        "case",
                        "customer",
                        "account",
                        "transactions",
                        "ledger_entries",
                        "balance_comparison",
                    ],
                },
            )

            # -----------------------------------------------------
            # LLM analysis
            # -----------------------------------------------------

            trajectory.record(
                step="llm_request",
                action="Analyze collected evidence",
                details={
                    "provider": getattr(
                        self._llm_client,
                        "provider",
                        None,
                    ),
                    "evidence_sources": [
                        "case",
                        "customer",
                        "account",
                        "transactions",
                        "ledger_entries",
                        "balance_comparison",
                    ],
                },
            )

            response = await self._llm_client.generate(
                SYSTEM_PROMPT,
                prompt,
            )

            # Do not persist the raw LLM response.
            #
            # The response may contain unnecessary sensitive
            # information copied from the investigation evidence.
            # The validated structured result is recorded after
            # parsing instead.

            trajectory.record(
                step="llm_response",
                action="Generate structured investigation analysis",
                details={
                    "response_received": True,
                },
            )

            # -----------------------------------------------------
            # Validate structured result
            # -----------------------------------------------------

            trajectory.record(
                step="result_validation",
                action="Validate LLM response",
                details={
                    "schema": "InvestigationResult",
                },
            )

            result = self._parse_result(
                case_id=case_id,
                response=response,
            )

            # -----------------------------------------------------
            # HUMAN REVIEW ENFORCEMENT
            # -----------------------------------------------------

            # Human review is mandatory for every investigation
            # result.
            #
            # These values are enforced by application code rather
            # than trusting the LLM to decide whether review is
            # necessary.
            #
            # No approval is simulated or manufactured here.
            # The investigation simply reaches a human-review
            # boundary.

            result.requires_human_review = True
            result.status = "PENDING_REVIEW"

            trajectory.record(
                step="human_checkpoint",
                action="Require mandatory human review",
                details={
                    "status": result.status,
                    "requires_human_review": (
                        result.requires_human_review
                    ),
                    "approval_received": False,
                    "consequential_action_executed": False,
                    "message": (
                        "Investigation recommendation requires "
                        "qualified human review before any "
                        "consequential action."
                    ),
                },
            )

            # -----------------------------------------------------
            # Final result
            # -----------------------------------------------------

            # Record only the validated structured result.
            #
            # This captures:
            # - evidence-based findings
            # - conclusion
            # - confidence
            # - advisory recommendation
            # - mandatory human-review status
            #
            # It intentionally does not persist the raw LLM response.

            trajectory.record(
                step="final_result",
                action="Produce validated investigation result",
                details={
                    "result": _serialize(
                        result
                    ),
                },
            )

            return result

        except Exception as exc:
            # Record investigation failures before propagating them.

            trajectory.record(
                step="error",
                action="Investigation failed",
                details={
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )

            raise

        finally:
            # Remove the callback before saving the trajectory.
            #
            # This prevents a later investigation from accidentally
            # writing retry events into this trajectory.

            self._mcp_client.set_retry_callback(None)

            # Always persist the trajectory, including failed runs.
            trajectory.save()

    @staticmethod
    def _record_mcp_retry(
        trajectory: InvestigationTrajectory,
        tool_name: str,
        retry_number: int,
        max_retries: int,
    ) -> None:
        """Record a genuine MCP retry in the investigation trajectory."""

        trajectory.record(
            step="mcp_retry",
            action="Retry MCP tool call",
            details={
                "tool": tool_name,
                "retry_number": retry_number,
                "max_retries": max_retries,
            },
        )

    @staticmethod
    def _parse_result(
        case_id: str,
        response: str,
    ) -> InvestigationResult:
        """Parse and validate the structured LLM response."""

        response = response.strip()

        try:
            data = json.loads(response)

        except json.JSONDecodeError:
            # Gemini may occasionally wrap otherwise valid JSON
            # in a Markdown JSON code fence.
            if response.startswith("```") and response.endswith("```"):
                lines = response.splitlines()

                if lines and lines[0].strip().lower() in {
                    "```json",
                    "```",
                }:
                    lines = lines[1:]

                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]

                cleaned_response = "\n".join(lines).strip()

                try:
                    data = json.loads(cleaned_response)

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "LLM returned invalid JSON."
                    ) from exc

            else:
                raise ValueError(
                    "LLM returned invalid JSON."
                )

        if not isinstance(data, dict):
            raise ValueError(
                "LLM returned JSON, but the result "
                "was not an object."
            )

        # case_id is application-controlled and must not come
        # from the LLM.
        data["case_id"] = case_id

        confidence = data.get("confidence")

        if isinstance(confidence, str):
            data["confidence"] = (
                confidence.strip().upper()
            )

        return InvestigationResult.model_validate(
            data
        )


def _serialize(value: Any) -> Any:
    """Convert application objects into JSON-compatible values."""

    if value is None:
        return None

    if isinstance(value, list):
        return [
            _serialize(item)
            for item in value
        ]

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
            key: _serialize(
                getattr(value, key)
            )
            for key in value.__dataclass_fields__
        }

    if hasattr(value, "model_dump"):
        return _serialize(
            value.model_dump()
        )

    return value