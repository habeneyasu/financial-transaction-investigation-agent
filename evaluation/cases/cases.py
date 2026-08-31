from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCriterion:
    """A deterministic criterion used to evaluate an investigation result."""

    name: str

    required_terms: tuple[str, ...] = ()

    forbidden_terms: tuple[str, ...] = ()

    match_any_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationCase:
    """Expected evaluation criteria for an investigation case."""

    case_id: str

    criteria: tuple[EvaluationCriterion, ...]


EVALUATION_CASES = (
    # ============================================================
    # CASE-001
    # Duplicate successful transfers + balance discrepancy
    # ============================================================
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
                name="Identifies 5,000 ETB transfers",
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
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
            EvaluationCriterion(
                name="Does not claim confirmed fraud",
                forbidden_terms=("confirmed fraud",),
            ),
        ),
    ),

    # ============================================================
    # CASE-002
    # Failed transaction with no ledger debit
    # ============================================================
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


    # ============================================================
    # CASE-003
    # Reversed transaction with debit and reversal credit
    # ============================================================
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
                ),
            ),

            EvaluationCriterion(
                name="Identifies debit and reversal credit",
                required_terms=("debit", "credit"),
            ),

            EvaluationCriterion(
                name="Identifies balance was restored",
                required_terms=("restored",),
                match_any_terms=(
                    "fully reversed",
                    "fully restored",
                    "net effect of 0",
                    "net effect is 0",
                    "balance was restored",
                ),
            ),

            EvaluationCriterion(
                name="Does not claim balance discrepancy",
                required_terms=(),
                forbidden_terms=(
                    "balance discrepancy",
                    "balance was not restored",
                ),
            ),
        ),
    ),

    # ============================================================
    # CASE-004
    # Successful incoming 5,000 ETB transfer
    # ============================================================

    EvaluationCase(
        case_id="CASE-004",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1001",
                required_terms=("TX-1001",),
            ),

            EvaluationCriterion(
                name="Identifies 5,000 ETB transaction",
                required_terms=("5,000 ETB",),
            ),

            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),

            EvaluationCriterion(
                name="Identifies incoming credit",
                required_terms=("credit",),
                match_any_terms=(
                    "incoming",
                    "credited",
                    "received",
                ),
            ),

            EvaluationCriterion(
                name="Identifies 5,000 ETB credited",
                required_terms=("5,000 ETB",),
                match_any_terms=(
                    "credited",
                    "credit",
                    "received",
                ),
            ),

            EvaluationCriterion(
                name="Identifies balance increase",
                required_terms=("balance",),
                match_any_terms=(
                    "8,000 ETB",
                    "13,000 ETB",
                    "increased",
                    "increase",
                    "8000",
                    "13000",
                ),
            ),

            EvaluationCriterion(
                name="Does not claim balance discrepancy",
                forbidden_terms=(
                    "balance discrepancy",
                    "balance was wrong",
                    "missing 2,500 ETB",
                    "2,500 ETB discrepancy",
                ),
            ),
        ),
    ),

    # ============================================================
    # CASE-005
    # Successful outgoing 2,000 ETB transfer
    # ============================================================

    EvaluationCase(
        case_id="CASE-005",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1002",
                required_terms=("TX-1002",),
            ),

            EvaluationCriterion(
                name="Identifies 2,000 ETB transaction",
                required_terms=("2,000 ETB",),
            ),

            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),

            EvaluationCriterion(
                name="Identifies outgoing transfer",
                required_terms=("outgoing",),
                match_any_terms=(
                    "outgoing",
                    "sent",
                    "debited",
                ),
            ),

            EvaluationCriterion(
                name="Identifies account debit",
                required_terms=("debit",),
            ),

            EvaluationCriterion(
                name="Identifies 2,000 ETB debit",
                required_terms=("2,000 ETB", "debit"),
            ),

            EvaluationCriterion(
                name="Does not claim balance discrepancy",
                forbidden_terms=(
                    "balance discrepancy",
                    "balance was wrong",
                    "balance mismatch",
                ),
            ),
        ),
    ),

    # ============================================================
    # CASE-006
    # Successful incoming 2,000 ETB transfer with account balance
    # inconsistency
    # ============================================================

    EvaluationCase(
        case_id="CASE-006",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1002",
                required_terms=("TX-1002",),
            ),

            EvaluationCriterion(
                name="Identifies 2,000 ETB transaction",
                required_terms=("2,000 ETB",),
            ),

            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),

            EvaluationCriterion(
                name="Identifies incoming credit",
                required_terms=("credit",),
                match_any_terms=(
                    "incoming",
                    "credited",
                    "received",
                ),
            ),

            EvaluationCriterion(
                name="Identifies 2,000 ETB credited",
                required_terms=("2,000 ETB",),
                match_any_terms=(
                    "credited",
                    "credit",
                    "received",
                ),
            ),

            EvaluationCriterion(
                name="Identifies account balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),

            EvaluationCriterion(
                name="Does not claim TX-1002 credit was missing",
                forbidden_terms=(
                    "2,000 ETB was not credited",
                    "2,000 ETB missing",
                    "credit was missing",
                    "TX-1002 was not credited",
                ),
            ),
        ),
    ),

    # ============================================================
    # CASE-007
    # Successful outgoing 1,500 ETB transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-007",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1003",
                required_terms=("TX-1003",),
            ),
            EvaluationCriterion(
                name="Identifies 1,500 ETB transaction",
                required_terms=("1,500 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-008
    # Incoming 1,500 ETB transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-008",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1003",
                required_terms=("TX-1003",),
            ),
            EvaluationCriterion(
                name="Identifies 1,500 ETB transaction",
                required_terms=("1,500 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-009
    # Explicit duplicate investigation
    # ============================================================
    EvaluationCase(
        case_id="CASE-009",
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
                name="Identifies both transactions as successful",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies suspected duplicate",
                required_terms=("suspected duplicate",),
            ),
            EvaluationCriterion(
                name="Identifies 5,000 ETB amount",
                required_terms=("5,000 ETB",),
            ),
        ),
    ),

    # ============================================================
    # CASE-010
    # Failed transaction and permanent-debit investigation
    # ============================================================
    EvaluationCase(
        case_id="CASE-010",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1005",
                required_terms=("TX-1005",),
            ),
            EvaluationCriterion(
                name="Identifies failed status",
                required_terms=("FAILED",),
            ),
            EvaluationCriterion(
                name="Identifies 10,000 ETB amount",
                required_terms=("10,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies absence of ledger debit",
                required_terms=("no", "ledger"),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-011
    # Failed incoming transfer to ACC-1004
    # ============================================================
    EvaluationCase(
        case_id="CASE-011",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1005",
                required_terms=("TX-1005",),
            ),
            EvaluationCriterion(
                name="Identifies failed transaction",
                required_terms=("FAILED",),
            ),
            EvaluationCriterion(
                name="Identifies 10,000 ETB amount",
                required_terms=("10,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies no ledger debit",
                required_terms=("no", "ledger"),
            ),
        ),
    ),

    # ============================================================
    # CASE-012
    # Successful 2,000 ETB incoming transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-012",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1006",
                required_terms=("TX-1006",),
            ),
            EvaluationCriterion(
                name="Identifies 2,000 ETB transaction",
                required_terms=("2,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-013
    # Successful outgoing 2,000 ETB transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-013",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1006",
                required_terms=("TX-1006",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies 2,000 ETB amount",
                required_terms=("2,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies account balance is consistent",
                forbidden_terms=("discrepancy", "inconsisten"),
            ),
        ),
    ),

    # ============================================================
    # CASE-014
    # Reversed outgoing transaction
    # ============================================================
    EvaluationCase(
        case_id="CASE-014",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1007",
                required_terms=("TX-1007",),
            ),
            EvaluationCriterion(
                name="Identifies reversed status",
                required_terms=("REVERSED",),
            ),
            EvaluationCriterion(
                name="Identifies reversal",
                required_terms=("reversal",),
            ),
            EvaluationCriterion(
                name="Identifies debit and credit",
                required_terms=("debit", "credit"),
            ),
            EvaluationCriterion(
                name="Identifies 1,000 ETB amount",
                required_terms=("1,000 ETB",),
            ),
        ),
    ),

    # ============================================================
    # CASE-015
    # Reversed incoming transaction
    # ============================================================
    EvaluationCase(
        case_id="CASE-015",
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
                name="Identifies debit and reversal credit",
                required_terms=("debit", "credit"),
            ),
            EvaluationCriterion(
                name="Identifies reversal amount",
                required_terms=("reversal",),
                match_any_terms=(
                    "1,000 ETB",
                    "1000 ETB",
                ),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-016
    # Successful 2,500 ETB outgoing transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-016",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1008",
                required_terms=("TX-1008",),
            ),
            EvaluationCriterion(
                name="Identifies 2,500 ETB amount",
                required_terms=("2,500 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-017
    # Successful 2,500 ETB incoming transfer
    # ============================================================
    EvaluationCase(
        case_id="CASE-017",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1008",
                required_terms=("TX-1008",),
            ),
            EvaluationCriterion(
                name="Identifies 2,500 ETB amount",
                required_terms=("2,500 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful transaction",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-018
    # Multi-transaction account activity investigation
    # ============================================================
    EvaluationCase(
        case_id="CASE-018",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1001",
                required_terms=("TX-1001",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1002",
                required_terms=("TX-1002",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1003",
                required_terms=("TX-1003",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1004",
                required_terms=("TX-1004",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1006",
                required_terms=("TX-1006",),
            ),
            EvaluationCriterion(
                name="Identifies successful transactions",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies duplicate pair",
                required_terms=("suspected duplicate",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-019
    # Multi-transaction account activity including reversal
    # ============================================================
    EvaluationCase(
        case_id="CASE-019",
        criteria=(
            EvaluationCriterion(
                name="Identifies TX-1001",
                required_terms=("TX-1001",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1003",
                required_terms=("TX-1003",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1007",
                required_terms=("TX-1007",),
            ),
            EvaluationCriterion(
                name="Identifies TX-1008",
                required_terms=("TX-1008",),
            ),
            EvaluationCriterion(
                name="Identifies reversed transaction",
                required_terms=("REVERSED",),
            ),
            EvaluationCriterion(
                name="Identifies reversal debit and credit",
                required_terms=("debit", "credit"),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),

    # ============================================================
    # CASE-020
    # Duplicate transactions + status + balance impact
    # ============================================================
    EvaluationCase(
        case_id="CASE-020",
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
                name="Identifies 5,000 ETB amount",
                required_terms=("5,000 ETB",),
            ),
            EvaluationCriterion(
                name="Identifies successful status",
                required_terms=("SUCCESS",),
            ),
            EvaluationCriterion(
                name="Identifies suspected duplicate",
                required_terms=("suspected duplicate",),
            ),
            EvaluationCriterion(
                name="Identifies balance discrepancy",
                required_terms=("balance", "discrepancy"),
            ),
        ),
    ),
)