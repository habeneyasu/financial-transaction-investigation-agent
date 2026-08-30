from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCriterion:
    """A deterministic criterion used to evaluate an investigation result."""

    name: str
    required_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()
    match_any_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationCase:
    """Expected evaluation criteria for an investigation case."""

    case_id: str
    criteria: tuple[EvaluationCriterion, ...]


EVALUATION_CASES = (
    EvaluationCase(
        case_id="CASE-001",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1001",
                required_terms=("TX-1001",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1004",
                required_terms=("TX-1004",),
            ),
            EvaluationCriterion(
                name="Identifies both transfers as 5,000 ETB",
                required_terms=("5,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transactions",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies suspected duplicate",
                required_terms=("suspected duplicate",),
            ),
            EvaluationCriterion(
                name="Identifies balance inconsistency",
                required_terms=("balance", "inconsisten"),
            ),
            EvaluationCriterion(
                name="Does not claim confirmed fraud",
                required_terms=(),
                forbidden_terms=("confirmed fraud",),
            ),
        ),
    ),
    EvaluationCase(
        case_id="CASE-002",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1005",
                required_terms=("TX-1005",),
            ),
            EvaluationCriterion(
                name="Identifies 10,000 ETB disputed amount",
                required_terms=("10,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies failed transaction",
                required_terms=("FAILED",),
            ),
            EvaluationCriterion(
                name="Identifies no ledger debit for TX-1005",
                required_terms=("no", "ledger", "TX-1005"),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),
    EvaluationCase(
        case_id="CASE-003",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1007",
                required_terms=("TX-1007",),
            ),
            EvaluationCriterion(
                name="Identifies reversed transaction",
                required_terms=("REVERSED",),
            ),
            EvaluationCriterion(
                name="Identifies 1,000 ETB reversal",
                required_terms=("reversal",),
                match_any_terms=(
                    "1,000 ETB",
                    "1000 ETB",
                    "difference of -1000",
                    "debit of 1000",
                ),
            ),
            EvaluationCriterion(
                name="Identifies debit and reversal credit",
                required_terms=("debit", "credit"),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),
)