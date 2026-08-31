import json

from datetime import datetime, timezone

from pathlib import Path

from typing import Any


TRAJECTORY_DIR = (
    Path(__file__).resolve().parents[2]
    / "evaluation"
    / "results"
    / "trajectories"
)


# Customer PII fields that must never be stored
# in the investigation trajectory.
PII_FIELDS = {
    "name",
    "full_name",
    "first_name",
    "last_name",
    "phone",
    "phone_number",
    "email",
    "address",
    "national_id",
    "id_number",
    "date_of_birth",
}


class InvestigationTrajectory:
    """Records the execution trajectory of a financial investigation."""

    WORKFLOW_VERSION = "1.0"

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.agent_name = "financial_investigation_agent"
        self.started_at = self._timestamp()
        self.steps: list[dict[str, Any]] = []

    @staticmethod
    def _timestamp() -> str:
        """Return the current UTC timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _sanitize(value: Any) -> Any:
        """
        Recursively remove customer PII from trajectory data.

        Identifiers such as customer_id, account_id, and transaction_id
        are preserved because they are useful for investigation tracing.
        """

        if isinstance(value, dict):
            return {
                key: InvestigationTrajectory._sanitize(item)
                for key, item in value.items()
                if key.lower() not in PII_FIELDS
            }

        if isinstance(value, list):
            return [
                InvestigationTrajectory._sanitize(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return tuple(
                InvestigationTrajectory._sanitize(item)
                for item in value
            )

        return value

    def record_workflow_start(
        self,
        objective: str,
        instructions: str,
        evaluation_case: bool = True,
    ) -> None:
        """
        Record the agent objective and instructions without
        recording private model reasoning.
        """

        self.record(
            step="workflow_start",
            action="Start investigation",
            details={
                "agent": self.agent_name,
                "workflow_version": self.WORKFLOW_VERSION,
                "objective": objective,
                "instructions": instructions,
                "evaluation_case": evaluation_case,
            },
        )

    def record(
        self,
        step: str,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record one step in the investigation trajectory."""

        sanitized_details = self._sanitize(
            details or {}
        )

        self.steps.append(
            {
                "step": step,
                "action": action,
                "details": sanitized_details,
                "timestamp": self._timestamp(),
            }
        )

    def save(self) -> Path:
        """Persist the trajectory to the evaluation results directory."""

        TRAJECTORY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            TRAJECTORY_DIR
            / f"{self.case_id}.json"
        )

        trajectory = {
            "case_id": self.case_id,
            "agent": self.agent_name,
            "workflow_version": self.WORKFLOW_VERSION,
            "started_at": self.started_at,
            "completed_at": self._timestamp(),
            "steps": self.steps,
        }

        output_file.write_text(
            json.dumps(
                trajectory,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

        return output_file