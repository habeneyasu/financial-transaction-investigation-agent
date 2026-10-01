from evaluation.baseline.run_evaluation import build_baseline_result


def test_baseline_reports_direction_and_posted_ledger_effect():
    result = build_baseline_result(
        case_id="CASE-TEST",
        account_id="ACC-001",
        transactions=[
            {
                "transaction_id": "TX-001",
                "from_account_id": "ACC-002",
                "to_account_id": "ACC-001",
                "amount": "1000",
                "status": "SUCCESS",
            }
        ],
        ledger_entries=[
            {
                "transaction_id": "TX-001",
                "entry_type": "CREDIT",
                "amount": "1000",
                "status": "POSTED",
            }
        ],
        balance_comparison={"consistent": True},
    )

    assert "incoming transfer" in result
    assert "posted CREDIT ledger entry" in result
    assert "credit increased the account balance" in result


def test_baseline_reports_only_balanced_reversal_as_restored():
    transaction = {
        "transaction_id": "TX-002",
        "from_account_id": "ACC-001",
        "to_account_id": "ACC-002",
        "amount": "1000",
        "status": "REVERSED",
    }
    entries = [
        {
            "transaction_id": "TX-002",
            "entry_type": entry_type,
            "amount": "1000",
            "status": "POSTED",
        }
        for entry_type in ("DEBIT", "CREDIT")
    ]

    result = build_baseline_result(
        case_id="CASE-TEST",
        account_id="ACC-001",
        transactions=[transaction],
        ledger_entries=entries,
        balance_comparison={"consistent": True},
    )

    assert "fully restored" in result
    assert "net effect of 0 ETB" in result


def test_baseline_reports_failed_incoming_transaction_has_no_credit():
    result = build_baseline_result(
        case_id="CASE-TEST",
        account_id="ACC-001",
        transactions=[
            {
                "transaction_id": "TX-003",
                "from_account_id": "ACC-002",
                "to_account_id": "ACC-001",
                "amount": "1000",
                "status": "FAILED",
            }
        ],
        ledger_entries=[],
        balance_comparison={"consistent": True},
    )

    assert "no ledger credit" in result