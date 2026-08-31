"""Investigation API routes."""

from fastapi import APIRouter

from app.agent.investigation_agent import InvestigationAgent
from app.api.schemas.investigation import (
    InvestigationRequest,
    InvestigationResult,
)
from app.data.database import db
from app.llm.client import LLMClient
from app.mcp.client import McpClient
from app.services.investigation_service import InvestigationService

router = APIRouter(
    prefix="/investigations",
    tags=["investigation"],
)


@router.post(
    "",
    response_model=InvestigationResult,
    summary="Run a financial transaction investigation",
)
async def investigate(
    request: InvestigationRequest,
) -> InvestigationResult:
    """Investigate a transaction complaint and return the structured result."""

    investigation_service = InvestigationService(db)
    llm_client = LLMClient()

    async with McpClient() as mcp_client:
        agent = InvestigationAgent(
            investigation_service=investigation_service,
            mcp_client=mcp_client,
            llm_client=llm_client,
        )

        return await agent.investigate(request.case_id)

