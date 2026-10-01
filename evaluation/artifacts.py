import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evaluation.cases.cases import EVALUATION_CASES


ARTIFACT_SCHEMA_VERSION = 2
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROUND_TRUTH_FILE = PROJECT_ROOT / "evaluation" / "results" / "ground_truth.json"

IDENTITY_FIELDS = (
    "artifact_schema_version",
    "system",
    "rubric_hash",
    "ground_truth_hash",
    "provider",
    "model",
    "prompt_hash",
    "implementation_hash",
    "generation_config",
)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rubric_hash() -> str:
    criteria = [
        {
            "case_id": case.case_id,
            "criteria": [
                {
                    "name": criterion.name,
                    "required_terms": criterion.required_terms,
                    "forbidden_terms": criterion.forbidden_terms,
                    "match_any_terms": criterion.match_any_terms,
                }
                for criterion in case.criteria
            ],
        }
        for case in EVALUATION_CASES
    ]
    payload = json.dumps(
        criteria,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256(payload)


def ground_truth_hash() -> str:
    return _sha256(GROUND_TRUTH_FILE.read_bytes())


def text_hash(*values: str) -> str:
    return _sha256("\n".join(values).encode("utf-8"))


def _git_metadata() -> tuple[str | None, bool | None]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if revision.returncode != 0:
        return None, None

    return revision.stdout.strip(), bool(status.stdout.strip())


def build_metadata(
    system: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    prompt_hash: str | None = None,
    implementation_hash: str | None = None,
    generation_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    git_commit, git_dirty = _git_metadata()
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "system": system,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rubric_hash": rubric_hash(),
        "ground_truth_hash": ground_truth_hash(),
        "provider": provider,
        "model": model,
        "prompt_hash": prompt_hash,
        "implementation_hash": implementation_hash,
        "generation_config": generation_config,
        "python_version": sys.version.split()[0],
        "git_commit": git_commit,
        "git_dirty": git_dirty,
    }


def load_artifact(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Evaluation artifact must be a JSON object.")

    metadata = data.get("metadata")
    results = data.get("results")

    if not isinstance(metadata, dict):
        raise ValueError("Evaluation artifact metadata must be an object.")
    if not isinstance(results, list):
        raise ValueError("Evaluation artifact results must be a list.")

    return metadata, results


def metadata_is_compatible(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> bool:
    return all(actual.get(field) == expected.get(field) for field in IDENTITY_FIELDS)


def save_artifact(
    path: Path,
    metadata: dict[str, Any],
    results: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "metadata": metadata,
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )