import json

import pytest

from evaluation.artifacts import (
    load_artifact,
    metadata_is_compatible,
    save_artifact,
)


def test_artifact_round_trip(tmp_path):
    path = tmp_path / "result.json"
    metadata = {
        "artifact_schema_version": 2,
        "system": "agent",
        "rubric_hash": "rubric",
        "ground_truth_hash": "data",
        "provider": "test",
        "model": "test-model",
        "prompt_hash": "prompt",
    }
    results = [{"case_id": "CASE-001", "score": 1.0}]

    save_artifact(path, metadata, results)

    assert load_artifact(path) == (metadata, results)


def test_metadata_rejects_changed_rubric():
    actual = {
        "artifact_schema_version": 2,
        "system": "agent",
        "rubric_hash": "old",
        "ground_truth_hash": "data",
        "provider": "test",
        "model": "test-model",
        "prompt_hash": "prompt",
    }
    expected = {**actual, "rubric_hash": "new"}

    assert not metadata_is_compatible(actual, expected)


def test_load_artifact_rejects_legacy_list(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="must be a JSON object",
    ):
        load_artifact(path)