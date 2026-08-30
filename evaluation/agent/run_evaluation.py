import asyncio

from app.agent.investigation_agent import InvestigationAgent
from app.data.database import db
from app.llm.client import LLMClient
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService

from evaluation.cases.cases import EVALUATION_CASES
from evaluation.evaluator import evaluate_case


async def main():
    investigation_service = InvestigationService(db)
    mcp_client = McpClient()
    llm_client = LLMClient()

    agent = InvestigationAgent(
        investigation_service=investigation_service,
        mcp_client=mcp_client,
        llm_client=llm_client,
    )

    async with mcp_client:
        for evaluation_case in EVALUATION_CASES:
            case_id = evaluation_case.case_id

            print(f"\n{'=' * 60}")
            print(f"Evaluating {case_id}")
            print(f"{'=' * 60}")

            result = await agent.investigate(case_id)

            result_json = result.model_dump_json()

            evaluation = evaluate_case(
                evaluation_case,
                result_json,
            )

            print(
                f"Score: "
                f"{evaluation.passed}/{evaluation.total} "
                f"({evaluation.score:.0%})"
            )

            for criterion in evaluation.criteria:
                status = "PASS" if criterion.passed else "FAIL"
                print(f"[{status}] {criterion.name}")


if __name__ == "__main__":
    asyncio.run(main())
