from datetime import datetime

import pytest

from app.data.database import Database
from evaluation.cases.cases import EVALUATION_CASES
from evaluation.generate_ground_truth import build_ground_truth


@pytest.mark.asyncio
async def test_ground_truth_matches_cases_and_respects_cutoff(tmp_path):
    database = Database(str(tmp_path / "ground-truth.db"))
    database.initialize_schema()
    database.seed_data()

    ground_truth = await build_ground_truth(database)

    assert [item["case_id"] for item in ground_truth] == [
        case.case_id for case in EVALUATION_CASES
    ]

    for item in ground_truth:
        cutoff = datetime.fromisoformat(item["as_of"])
        assert all(
            datetime.fromisoformat(transaction["created_at"]) <= cutoff
            for transaction in item["transactions"]
        )
        assert all(
            datetime.fromisoformat(entry["created_at"]) <= cutoff
            for entry in item["ledger_entries"]
        )

    database.close()