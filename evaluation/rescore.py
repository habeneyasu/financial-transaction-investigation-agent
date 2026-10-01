import argparse
from datetime import datetime, timezone
from pathlib import Path

from evaluation.artifacts import (
    ground_truth_hash,
    load_artifact,
    rubric_hash,
    save_artifact,
)
from evaluation.cases.cases import EVALUATION_CASES
from evaluation.evaluator import evaluate_case


def rescore_artifact(
    path: Path,
    *,
    allow_ground_truth_change: bool = False,
) -> None:
    metadata, stored_results = load_artifact(path)
    current_ground_truth_hash = ground_truth_hash()

    if (
        metadata.get("ground_truth_hash") != current_ground_truth_hash
        and not allow_ground_truth_change
    ):
        raise ValueError(
            "Ground truth changed. Re-run with --allow-ground-truth-change "
            "only when stored outputs were generated from equivalent inputs."
        )

    stored_by_case = {
        result["case_id"]: result
        for result in stored_results
    }
    expected_case_ids = {case.case_id for case in EVALUATION_CASES}
    if set(stored_by_case) != expected_case_ids:
        raise ValueError("Artifact must contain every evaluation case.")

    rescored_results = []
    for evaluation_case in EVALUATION_CASES:
        stored = stored_by_case[evaluation_case.case_id]
        if "output" not in stored:
            raise ValueError(
                f"{evaluation_case.case_id} has no stored output to rescore."
            )

        evaluation = evaluate_case(
            evaluation_case,
            stored["output"],
        )
        rescored_results.append(
            {
                **stored,
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
        )

    metadata = {
        **metadata,
        "rubric_hash": rubric_hash(),
        "ground_truth_hash": current_ground_truth_hash,
        "rescored_at": datetime.now(timezone.utc).isoformat(),
    }
    save_artifact(path, metadata, rescored_results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rescore stored evaluation outputs without rerunning a system."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--allow-ground-truth-change",
        action="store_true",
        help=(
            "Acknowledge that stored outputs were generated from evidence "
            "equivalent to the current ground truth."
        ),
    )
    args = parser.parse_args()
    rescore_artifact(
        args.path,
        allow_ground_truth_change=args.allow_ground_truth_change,
    )
    print(f"Rescored artifact: {args.path}")


if __name__ == "__main__":
    main()