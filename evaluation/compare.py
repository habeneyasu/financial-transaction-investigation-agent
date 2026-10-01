from pathlib import Path

from evaluation.artifacts import load_artifact
from evaluation.cases.cases import EVALUATION_CASES


RESULTS_DIR = Path(__file__).parent / "results"

BASELINE_FILE = RESULTS_DIR / "baseline.json"
AGENT_FILE = RESULTS_DIR / "agent.json"


def validate_comparable(
    baseline_metadata: dict,
    baseline_results: list[dict],
    agent_metadata: dict,
    agent_results: list[dict],
) -> None:
    """Require complete artifacts produced from the same evaluation inputs."""
    for field in (
        "artifact_schema_version",
        "rubric_hash",
        "ground_truth_hash",
    ):
        if baseline_metadata.get(field) != agent_metadata.get(field):
            raise ValueError(
                f"Evaluation artifacts have different {field}."
            )

    expected_case_ids = {case.case_id for case in EVALUATION_CASES}

    for system, results in (
        ("baseline", baseline_results),
        ("agent", agent_results),
    ):
        case_ids = [result.get("case_id") for result in results]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError(
                f"{system.capitalize()} artifact contains duplicate cases."
            )

        actual_case_ids = set(case_ids)
        if actual_case_ids != expected_case_ids:
            missing = sorted(expected_case_ids - actual_case_ids)
            unexpected = sorted(actual_case_ids - expected_case_ids)
            raise ValueError(
                f"{system.capitalize()} artifact case set is incomplete: "
                f"missing={missing}, unexpected={unexpected}."
            )


def main():
    baseline_metadata, baseline_results = load_artifact(BASELINE_FILE)
    agent_metadata, agent_results = load_artifact(AGENT_FILE)

    validate_comparable(
        baseline_metadata,
        baseline_results,
        agent_metadata,
        agent_results,
    )

    baseline_by_case = {
        result["case_id"]: result
        for result in baseline_results
    }

    agent_by_case = {
        result["case_id"]: result
        for result in agent_results
    }

    case_ids = sorted(baseline_by_case)

    print("=" * 70)
    print("BASELINE VS AGENT")
    print("=" * 70)

    baseline_scores = []
    agent_scores = []

    for case_id in case_ids:
        baseline_score = baseline_by_case[case_id]["score"]
        agent_score = agent_by_case[case_id]["score"]

        improvement = agent_score - baseline_score

        baseline_scores.append(baseline_score)
        agent_scores.append(agent_score)

        print(f"\n{case_id}")
        print(f"Baseline:    {baseline_score:.0%}")
        print(f"Agent:       {agent_score:.0%}")
        print(f"Improvement: {improvement:+.0%}")

    overall_baseline = (
        sum(baseline_scores) / len(baseline_scores)
        if baseline_scores
        else 0.0
    )

    overall_agent = (
        sum(agent_scores) / len(agent_scores)
        if agent_scores
        else 0.0
    )

    overall_improvement = (
        overall_agent - overall_baseline
    )

    baseline_correct = sum(score == 1.0 for score in baseline_scores)
    agent_correct = sum(score == 1.0 for score in agent_scores)

    baseline_criteria_passed = sum(
        result["passed"] for result in baseline_results
    )
    agent_criteria_passed = sum(
        result["passed"] for result in agent_results
    )
    baseline_criteria_total = sum(
        result["total"] for result in baseline_results
    )
    agent_criteria_total = sum(
        result["total"] for result in agent_results
    )

    print("\n" + "=" * 70)
    print("OVERALL")
    print("=" * 70)

    print(f"Baseline:    {overall_baseline:.0%}")
    print(f"Agent:       {overall_agent:.0%}")
    print(f"Improvement: {overall_improvement:+.0%}")
    print(
        f"Fully correct cases: baseline {baseline_correct}/{len(case_ids)}, "
        f"agent {agent_correct}/{len(case_ids)}"
    )
    print(
        "Criteria passed:     "
        f"baseline {baseline_criteria_passed}/{baseline_criteria_total}, "
        f"agent {agent_criteria_passed}/{agent_criteria_total}"
    )


if __name__ == "__main__":
    main()