import pytest

from evaluation.artifacts import ARTIFACT_SCHEMA_VERSION
from evaluation.cases.cases import EVALUATION_CASES
from evaluation.compare import validate_comparable


def _metadata(**overrides):
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "rubric_hash": "rubric",
        "ground_truth_hash": "ground-truth",
        **overrides,
    }


def _results():
    return [
        {
            "case_id": case.case_id,
            "passed": len(case.criteria),
            "total": len(case.criteria),
            "score": 1.0,
        }
        for case in EVALUATION_CASES
    ]


def test_validate_comparable_accepts_complete_matching_artifacts():
    validate_comparable(
        _metadata(),
        _results(),
        _metadata(),
        _results(),
    )


def test_validate_comparable_rejects_different_rubric():
    with pytest.raises(ValueError, match="different rubric_hash"):
        validate_comparable(
            _metadata(),
            _results(),
            _metadata(rubric_hash="changed"),
            _results(),
        )


def test_validate_comparable_rejects_missing_case():
    with pytest.raises(ValueError, match="case set is incomplete"):
        validate_comparable(
            _metadata(),
            _results(),
            _metadata(),
            _results()[:-1],
        )


def test_validate_comparable_rejects_duplicate_case():
    duplicate_results = _results()
    duplicate_results.append(duplicate_results[0])

    with pytest.raises(ValueError, match="duplicate cases"):
        validate_comparable(
            _metadata(),
            _results(),
            _metadata(),
            duplicate_results,
        )