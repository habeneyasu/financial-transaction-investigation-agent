import json
from pathlib import Path


RESULTS_DIR = Path(__file__).parent / "results"

BASELINE_FILE = RESULTS_DIR / "baseline.json"
AGENT_FILE = RESULTS_DIR / "agent.json"


def load_results(path: Path) -> list[dict]:
    """Load evaluation results from a JSON file."""
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def main():
    baseline_results = load_results(BASELINE_FILE)
    agent_results = load_results(AGENT_FILE)

    baseline_by_case = {
        result["case_id"]: result
        for result in baseline_results
    }

    agent_by_case = {
        result["case_id"]: result
        for result in agent_results
    }

    case_ids = sorted(
        set(baseline_by_case) & set(agent_by_case)
    )

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

    print("\n" + "=" * 70)
    print("OVERALL")
    print("=" * 70)

    print(f"Baseline:    {overall_baseline:.0%}")
    print(f"Agent:       {overall_agent:.0%}")
    print(f"Improvement: {overall_improvement:+.0%}")


if __name__ == "__main__":
    main()