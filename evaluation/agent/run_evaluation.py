import argparse
import asyncio
import json
from pathlib import Path

from google.genai.errors import ClientError

from app.agent.investigation_agent import InvestigationAgent
from app.data.database import db
from app.llm.client import LLMClient
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService

from evaluation.cases.cases import EVALUATION_CASES
from evaluation.evaluator import evaluate_case


RESULTS_FILE = (
    Path(__file__).parent.parent
    / "results"
    / "agent.json"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run financial investigation agent evaluation.",
    )

    parser.add_argument(
        "--start-case",
        type=int,
        default=1,
        help=(
            "Case number to start from, "
            "e.g. 18 for CASE-018."
        ),
    )

    parser.add_argument(
        "--record-trajectories",
        action="store_true",
        help=(
            "Rerun cases and record investigation trajectories."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Rerun cases even if an evaluation result "
            "already exists."
        ),
    )

    return parser.parse_args()


def load_existing_results():
    if not RESULTS_FILE.exists():
        return []

    try:
        data = json.loads(
            RESULTS_FILE.read_text(
                encoding="utf-8",
            )
        )

        if not isinstance(data, list):
            print(
                f"Warning: {RESULTS_FILE} does not contain "
                "a JSON list. Starting with empty results."
            )
            return []

        return data

    except json.JSONDecodeError:
        print(
            f"Warning: Could not parse {RESULTS_FILE}. "
            "Starting with empty results."
        )

        return []


def save_results(results):
    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULTS_FILE.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )


def remove_existing_case(
    results,
    case_id,
):
    return [
        result
        for result in results
        if result.get("case_id") != case_id
    ]


def print_evaluation(evaluation):
    print(
        f"Score: "
        f"{evaluation.passed}/"
        f"{evaluation.total} "
        f"({evaluation.score:.0%})"
    )

    print()

    for criterion in evaluation.criteria:
        status = (
            "PASS"
            if criterion.passed
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{criterion.name}"
        )

        if not criterion.passed and criterion.reason:
            print(
                f"       {criterion.reason}"
            )


def print_summary(results):
    if not results:
        print("\nNo evaluation results recorded.")
        return

    total_cases = len(results)

    passed_cases = sum(
        result.get("score", 0.0) == 1.0
        for result in results
    )

    average_score = (
        sum(
            result.get("score", 0.0)
            for result in results
        )
        / total_cases
    )

    total_criteria = sum(
        result.get("total", 0)
        for result in results
    )

    passed_criteria = sum(
        result.get("passed", 0)
        for result in results
    )

    criteria_score = (
        passed_criteria / total_criteria
        if total_criteria
        else 0.0
    )

    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Cases evaluated:      {total_cases}"
    )

    print(
        f"Fully correct cases:  "
        f"{passed_cases}/{total_cases} "
        f"({passed_cases / total_cases:.0%})"
    )

    print(
        f"Average case score:   "
        f"{average_score:.0%}"
    )

    print(
        f"Criteria passed:      "
        f"{passed_criteria}/{total_criteria} "
        f"({criteria_score:.0%})"
    )

    print("=" * 60)


async def main():
    args = parse_args()

    start_case_id = (
        f"CASE-{args.start_case:03d}"
    )

    existing_results = load_existing_results()

    print(
        f"Starting evaluation from "
        f"{start_case_id}"
    )

    print(
        f"Existing results: "
        f"{len(existing_results)}"
    )

    investigation_service = InvestigationService(db)

    mcp_client = McpClient()

    llm_client = LLMClient()

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    async with mcp_client:
        for evaluation_case in EVALUATION_CASES:
            case_id = evaluation_case.case_id

            case_number = int(
                case_id.split("-")[1]
            )

            if case_number < args.start_case:
                continue

            existing_case = next(
                (
                    result
                    for result in existing_results
                    if result.get("case_id") == case_id
                ),
                None,
            )

            should_skip = (
                existing_case is not None
                and not args.force
                and not args.record_trajectories
            )

            if should_skip:
                print(
                    f"\nSkipping {case_id} "
                    "— already evaluated."
                )
                continue

            print()
            print("=" * 60)
            print(f"Evaluating {case_id}")
            print("=" * 60)

            try:
                result = await agent.investigate(
                    case_id
                )

                evaluation = evaluate_case(
                    evaluation_case,
                    result.model_dump(),
                )

                evaluation_result = {
                    "case_id": evaluation.case_id,
                    "passed": evaluation.passed,
                    "total": evaluation.total,
                    "score": evaluation.score,
                    "criteria": [
                        {
                            "name": criterion.name,
                            "passed": criterion.passed,
                            "reason": criterion.reason,
                        }
                        for criterion in evaluation.criteria
                    ],
                }

                # Remove the old result when rerunning.
                existing_results = (
                    remove_existing_case(
                        existing_results,
                        case_id,
                    )
                )

                existing_results.append(
                    evaluation_result
                )

                # Save immediately after each case.
                save_results(
                    existing_results
                )

                print_evaluation(
                    evaluation
                )

            except ClientError as exc:
                if getattr(
                    exc,
                    "code",
                    None,
                ) == 429:
                    print()
                    print(
                        f"Rate limit reached while "
                        f"evaluating {case_id}."
                    )

                    print(
                        "No result was recorded "
                        "for this case."
                    )

                    print(
                        "Resume later with the same "
                        "command."
                    )

                    break

                raise

            except Exception as exc:
                print()
                print(
                    f"ERROR while evaluating "
                    f"{case_id}: {exc}"
                )

                print(
                    "No evaluation result was "
                    "recorded for this case."
                )

                # Continue with the next case.
                continue

    save_results(
        existing_results
    )

    print()
    print(
        f"Results saved to: "
        f"{RESULTS_FILE}"
    )

    print(
        f"Total saved results: "
        f"{len(existing_results)}"
    )

    print_summary(
        existing_results
    )


if __name__ == "__main__":
    asyncio.run(main())