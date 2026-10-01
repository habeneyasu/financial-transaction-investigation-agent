import asyncio
import json
from pathlib import Path

from app.data.database import Database, db
from app.mcp.client import McpClient
from app.mcp.server import create_mcp_server
from app.mcp.tools._serialization import jsonable
from app.services.investigation_service import InvestigationService

from evaluation.cases.cases import EVALUATION_CASES


OUTPUT_FILE = Path(__file__).parent / "results" / "ground_truth.json"


async def build_ground_truth(
    database: Database = db,
) -> list[dict]:
    investigation_service = InvestigationService(database)
    ground_truth = []

    async with McpClient(create_mcp_server(database)) as client:
        for evaluation_case in EVALUATION_CASES:
            case = investigation_service.get_investigation_case(
                evaluation_case.case_id
            )
            customer = await client.get_customer(case.customer_id)
            account = await client.get_account(case.account_id)
            transactions = await client.get_transactions(
                case.account_id,
                as_of=case.submitted_at,
            )
            ledger_entries = await client.get_ledger_entries(
                case.account_id,
                as_of=case.submitted_at,
            )
            balance_comparison = await client.compare_account_balance(
                case.account_id,
                as_of=case.submitted_at,
            )

            case_transaction_ids = [
                relation.transaction_id
                for relation in database.get_case_transactions(case.case_id)
            ]
            relevant_transactions = [
                transaction
                for transaction in transactions
                if transaction["transaction_id"] in case_transaction_ids
            ]

            transaction_facts = []
            for transaction in relevant_transactions:
                transaction_id = transaction["transaction_id"]
                if transaction["from_account_id"] == case.account_id:
                    direction = "OUTGOING"
                elif transaction["to_account_id"] == case.account_id:
                    direction = "INCOMING"
                else:
                    direction = "UNKNOWN"

                transaction_facts.append(
                    {
                        **transaction,
                        "direction": direction,
                        "ledger_entries": [
                            entry
                            for entry in ledger_entries
                            if entry["transaction_id"] == transaction_id
                        ],
                    }
                )

            ground_truth.append(
                {
                    "case_id": case.case_id,
                    "as_of": case.submitted_at.isoformat(),
                    "case": jsonable(case),
                    "customer": customer,
                    "account": account,
                    "case_transaction_ids": case_transaction_ids,
                    "relevant_transactions": relevant_transactions,
                    "transaction_facts": transaction_facts,
                    "transactions": transactions,
                    "ledger_entries": ledger_entries,
                    "balance_comparison": balance_comparison,
                }
            )

    return ground_truth


async def main() -> None:
    db.initialize_schema()
    db.seed_data()
    ground_truth = await build_ground_truth()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(ground_truth, indent=2),
        encoding="utf-8",
    )
    print(f"Ground truth saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())