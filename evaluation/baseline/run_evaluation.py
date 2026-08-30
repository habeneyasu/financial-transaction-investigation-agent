import asyncio
import json
from pathlib import Path

from app.data.database import db
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService

from evaluation.cases.cases import EVALUATION_CASES
from evaluation.evaluator import evaluate_case


RESULTS_FILE = (
    Path(__file__).parent.parent / "results" / "baseline.json"
)


def build_baseline_result(
    case_id: str,
    transactions: list[dict],
    ledger_entries: list[dict],
    balance_comparison: dict,
) -> str:
    """Generate a deterministic investigation result."""

    lines = [f"Investigation case: {case_id}"]

    # Transaction rules
    for transaction in transactions:
        transaction_id = transaction["transaction_id"]
        status = transaction["status"]
        amount = transaction["amount"]

        lines.append(
            f"Transaction {transaction_id}: "
            f"{amount} ETB, status {status}."
        )

        # Failed transaction
        if status == "FAILED":
            transaction_ledger = [
                entry
                for entry in ledger_entries
                if entry["transaction_id"] == transaction_id
            ]

            has_debit = any(
                entry["entry_type"] == "DEBIT"
                for entry in transaction_ledger
            )

            if not has_debit:
                lines.append(
                    f"Transaction {transaction_id} is FAILED "
                    f"and has no ledger debit."
                )

        # Reversed transaction
        if status == "REVERSED":
            transaction_ledger = [
                entry
                for entry in ledger_entries
                if entry["transaction_id"] == transaction_id
            ]

            has_debit = any(
                entry["entry_type"] == "DEBIT"
                for entry in transaction_ledger
            )

            has_credit = any(
                entry["entry_type"] == "CREDIT"
                for entry in transaction_ledger
            )

            if has_debit and has_credit:
                lines.append(
                    f"Transaction {transaction_id} was REVERSED "
                    f"with a debit and reversal credit."
                )

                lines.append(
                    f"The reversal amount is {amount} ETB."
                )

    # Duplicate transaction rule
    successful_transactions = [
        transaction
        for transaction in transactions
        if transaction["status"] == "SUCCESS"
    ]

    for i, first in enumerate(successful_transactions):
        for second in successful_transactions[i + 1:]:
            if (
                first["amount"] == second["amount"]
                and first["to_account_id"]
                == second["to_account_id"]
            ):
                lines.append(
                    f"Transactions {first['transaction_id']} and "
                    f"{second['transaction_id']} are suspected duplicate "
                    f"transactions of {first['amount']} ETB."
                )

    # Balance consistency rule
    if not balance_comparison["consistent"]:
        lines.append(
            "The account balance has a discrepancy between "
            "the reported balance and expected balance."
        )

    return "\n".join(lines)


async def main():
    investigation_service = InvestigationService(db)
    mcp_client = McpClient()

    results = []

    async with mcp_client:
        for evaluation_case in EVALUATION_CASES:
            case_id = evaluation_case.case_id

            print(f"\n{'=' * 60}")
            print(f"Evaluating {case_id}")
            print(f"{'=' * 60}")

            case = investigation_service.get_investigation_case(
                case_id
            )

            transactions = await mcp_client.get_transactions(
                case.account_id
            )

            ledger_entries = await mcp_client.get_ledger_entries(
                case.account_id
            )

            balance_comparison = (
                await mcp_client.compare_account_balance(
                    case.account_id
                )
            )

            baseline_result = build_baseline_result(
                case_id=case_id,
                transactions=transactions,
                ledger_entries=ledger_entries,
                balance_comparison=balance_comparison,
            )

            evaluation = evaluate_case(
                evaluation_case,
                baseline_result,
            )

            results.append(
                {
                    "case_id": evaluation.case_id,
                    "passed": evaluation.passed,
                    "total": evaluation.total,
                    "score": evaluation.score,
                    "criteria": [
                        {
                            "name": criterion.name,
                            "passed": criterion.passed,
                        }
                        for criterion in evaluation.criteria
                    ],
                }
            )

            print(
                f"Score: {evaluation.passed}/{evaluation.total} "
                f"({evaluation.score:.0%})"
            )

            for criterion in evaluation.criteria:
                status = "PASS" if criterion.passed else "FAIL"
                print(f"[{status}] {criterion.name}")

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTS_FILE.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())