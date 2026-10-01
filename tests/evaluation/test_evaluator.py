import json

import pytest

from evaluation.cases.cases import EvaluationCase, EvaluationCriterion
from evaluation.evaluator import evaluate_case


def _case(*criteria: EvaluationCriterion) -> EvaluationCase:
    return EvaluationCase(case_id="CASE-TEST", criteria=criteria)


def test_evaluate_case_accepts_plain_text_baseline_result():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            )
        ),
        "Transaction TX-001 has status SUCCESS.",
    )

    assert evaluation.is_correct


def test_evaluate_case_accepts_serialized_json_object():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Identifies transaction",
                required_terms=("TX-001",),
            )
        ),
        json.dumps(
            {
                "conclusion": "Transaction TX-001 was identified.",
                "findings": [],
            }
        ),
    )

    assert evaluation.is_correct


def test_evaluate_case_rejects_serialized_non_object():
    with pytest.raises(
        ValueError,
        match="must be a JSON object",
    ):
        evaluate_case(_case(), "[]")


def test_evaluate_case_reports_all_criterion_failures():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Combined criterion",
                required_terms=("TX-001", "SUCCESS"),
                match_any_terms=("credited", "received"),
                forbidden_terms=("confirmed fraud",),
            )
        ),
        {
            "conclusion": "TX-001 was marked as confirmed fraud.",
            "findings": [],
        },
    )

    criterion = evaluation.criteria[0]

    assert not criterion.passed
    assert "Missing: SUCCESS" in criterion.reason
    assert "None of alternatives matched" in criterion.reason
    assert "Forbidden terms found: confirmed fraud" in criterion.reason


def test_evaluate_case_does_not_reward_negated_claims():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Balance discrepancy",
                required_terms=("balance discrepancy",),
            ),
        ),
        {
            "conclusion": (
                "The transaction was not SUCCESS and there was no balance "
                "discrepancy."
            ),
            "findings": [],
        },
    )

    assert evaluation.passed == 0


def test_evaluate_case_does_not_penalize_negated_forbidden_claim():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Does not claim fraud",
                forbidden_terms=("confirmed fraud",),
            )
        ),
        {
            "conclusion": "The evidence does not establish confirmed fraud.",
            "findings": [],
        },
    )

    assert evaluation.is_correct


def test_evaluate_case_normalizes_amount_thousands_separator():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Amount",
                required_terms=("1,000 ETB",),
            )
        ),
        "The reversal amount was 1000 ETB.",
    )

    assert evaluation.is_correct


def test_negation_does_not_cross_sentence_boundary():
    evaluation = evaluate_case(
        _case(
            EvaluationCriterion(
                name="Transaction ID",
                required_terms=("TX-1002",),
            )
        ),
        "There was no ledger debit. Transaction TX-1002 was successful.",
    )

    assert evaluation.is_correct