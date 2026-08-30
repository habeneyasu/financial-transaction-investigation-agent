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
    Path(__file__).parent.parent / "results" / "agent.json"
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run agent evaluation from a specific case."
    )
    parser.add_argument(
        "--start-case",
        type=int,
        default=1,
        help="Case number to start from, e.g. 18 for CASE-018.",
    )
    return parser.parse_args()


def load_existing_results():
    if not RESULTS_FILE.exists():
        return []

    try:
        return json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError:
        print(
            f"Warning: Could not parse {RESULTS_FILE}. "
            "Starting with empty results."
        )
        return []


def save_results(results):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    RESULTS_FILE.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )


async def main():
    args = parse_args()

    start_case_id = f"CASE-{args.start_case:03d}"

    existing_results = load_existing_results()

    # Avoid duplicating results if a case is accidentally rerun.
    existing_case_ids = {
        result["case_id"]
        for result in existing_results
        if "case_id" in result
    }

    print(f"Starting evaluation from {start_case_id}")
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

            case_number = int(case_id.split("-")[1])

            if case_number < args.start_case:
                continue

            if case_id in existing_case_ids:
                print(f"\nSkipping {case_id} — already evaluated.")
                continue

            print(f"\n{'=' * 60}")
            print(f"Evaluating {case_id}")
            print(f"{'=' * 60}")

            try:
                result = await agent.investigate(case_id)

                result_json = result.model_dump_json()

                evaluation = evaluate_case(
                    evaluation_case,
                    result_json,
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
                        }
                        for criterion in evaluation.criteria
                    ],
                }

                existing_results.append(evaluation_result)
                existing_case_ids.add(case_id)

                # Save immediately after every successful case.
                save_results(existing_results)

                print(
                    f"Score: "
                    f"{evaluation.passed}/{evaluation.total} "
                    f"({evaluation.score:.0%})"
                )

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

            except ClientError as exc:
                if getattr(exc, "code", None) == 429:
                    print(
                        f"\nRate limit reached while evaluating "
                        f"{case_id}."
                    )
                    print(
                        "No result was recorded for this case."
                    )
                    print(
                        "Resume later with the same command."
                    )
                    break

                raise

    save_results(existing_results)

    print(
        f"\nResults saved to: {RESULTS_FILE}"
    )
    print(
        f"Total saved results: "
        f"{len(existing_results)}"
    )


if __name__ == "__main__":
    asyncio.run(main())

