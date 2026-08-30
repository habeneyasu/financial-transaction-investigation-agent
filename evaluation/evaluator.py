from dataclasses import dataclass
import re

from evaluation.cases.cases import EvaluationCase


@dataclass(frozen=True)
class CriterionResult:
    """Result of evaluating a single criterion."""

    name: str
    passed: bool


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating one investigation case."""

    case_id: str
    passed: int
    total: int
    score: float
    criteria: tuple[CriterionResult, ...]


def _normalize_text(text: str) -> str:
    """Normalize text for deterministic evaluation."""

    text = text.lower()

    # Normalize comma-separated numbers.
    text = re.sub(
        r"(\d),(\d{3})",
        r"\1\2",
        text,
    )

    # Normalize repeated whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _contains_term(
    text: str,
    term: str,
) -> bool:
    """Check whether a normalized term exists in normalized text."""

    normalized_term = _normalize_text(term)

    return normalized_term in text


def evaluate_case(
    evaluation_case: EvaluationCase,
    investigation_result: str,
) -> EvaluationResult:
    """Evaluate an investigation result against deterministic criteria."""

    text = _normalize_text(investigation_result)

    results = []

    for criterion in evaluation_case.criteria:
        required_passed = all(
            _contains_term(text, term)
            for term in criterion.required_terms
        )

        match_any_passed = (
            not criterion.match_any_terms
            or any(
                _contains_term(text, term)
                for term in criterion.match_any_terms
            )
        )

        forbidden_passed = all(
            not _contains_term(text, term)
            for term in criterion.forbidden_terms
        )

        results.append(
            CriterionResult(
                name=criterion.name,
                passed=(
                    required_passed
                    and match_any_passed
                    and forbidden_passed
                ),
            )
        )

    passed_count = sum(
        result.passed
        for result in results
    )

    total = len(results)

    score = (
        passed_count / total
        if total
        else 0.0
    )

    return EvaluationResult(
        case_id=evaluation_case.case_id,
        passed=passed_count,
        total=total,
        score=score,
        criteria=tuple(results),
    )