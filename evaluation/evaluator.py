from dataclasses import dataclass
from typing import Any

from evaluation.cases.cases import EvaluationCase


@dataclass(frozen=True)
class CriterionResult:
    """Result of evaluating a single investigation criterion."""

    name: str
    passed: bool
    reason: str = ""


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating one investigation case."""

    case_id: str
    passed: int
    total: int
    score: float
    criteria: tuple[CriterionResult, ...]

    @property
    def is_correct(self) -> bool:
        """Whether the investigation passed all criteria."""

        return self.score == 1.0


def _collect_result_text(result: dict[str, Any]) -> str:
    """
    Flatten the structured investigation result into text.

    This is retained only for backward-compatible deterministic
    criteria such as required/forbidden terms.
    """

    parts: list[str] = []

    parts.append(str(result.get("case_id", "")))
    parts.append(str(result.get("conclusion", "")))
    parts.append(str(result.get("recommendation", "")))
    parts.append(str(result.get("confidence", "")))
    parts.append(str(result.get("status", "")))

    for finding in result.get("findings", []):
        parts.append(str(finding.get("description", "")))

        for evidence in finding.get("evidence", []):
            parts.append(str(evidence))

    return " ".join(parts).lower()


def _contains_term(text: str, term: str) -> bool:
    """Check whether a term exists in normalized text."""

    return term.lower() in text


def evaluate_case(
    evaluation_case: EvaluationCase,
    investigation_result: str | dict[str, Any],
) -> EvaluationResult:
    """
    Evaluate an investigation result.

    The result is expected to be the structured InvestigationResult
    serialized as JSON, although a dictionary is also accepted.
    """

    if isinstance(investigation_result, str):
        import json

        result = json.loads(investigation_result)
    else:
        result = investigation_result

    text = _collect_result_text(result)

    results: list[CriterionResult] = []

    for criterion in evaluation_case.criteria:
        missing_required = [
            term
            for term in criterion.required_terms
            if not _contains_term(text, term)
        ]

        matched_any = True

        if criterion.match_any_terms:
            matched_any = any(
                _contains_term(text, term)
                for term in criterion.match_any_terms
            )

        forbidden_found = [
            term
            for term in criterion.forbidden_terms
            if _contains_term(text, term)
        ]

        passed = (
            not missing_required
            and matched_any
            and not forbidden_found
        )

        reasons: list[str] = []

        if missing_required:
            reasons.append(
                "Missing: " + ", ".join(missing_required)
            )

        if criterion.match_any_terms and not matched_any:
            reasons.append(
                "None of alternatives matched: "
                + ", ".join(criterion.match_any_terms)
            )

        if forbidden_found:
            reasons.append(
                "Forbidden terms found: "
                + ", ".join(forbidden_found)
            )

        results.append(
            CriterionResult(
                name=criterion.name,
                passed=passed,
                reason="; ".join(reasons),
            )
        )

    passed_count = sum(
        criterion.passed
        for criterion in results
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