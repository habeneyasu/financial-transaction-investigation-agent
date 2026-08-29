"""FastAPI global exception handlers for mapping application exceptions to HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    InvestigationError,
    CustomerNotFoundError,
    AccountNotFoundError,
    TransactionNotFoundError,
    InvestigationCaseNotFoundError,
    MCPError,
    LLMError,
    ApplicationValidationError,
    InvestigationTimeoutError,
    InvestigationMaxStepsError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""
    
    @app.exception_handler(CustomerNotFoundError)
    async def customer_not_found_handler(request: Request, exc: CustomerNotFoundError) -> JSONResponse:
        logger.warning(f"Customer not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(AccountNotFoundError)
    async def account_not_found_handler(request: Request, exc: AccountNotFoundError) -> JSONResponse:
        logger.warning(f"Account not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(TransactionNotFoundError)
    async def transaction_not_found_handler(request: Request, exc: TransactionNotFoundError) -> JSONResponse:
        logger.warning(f"Transaction not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(InvestigationCaseNotFoundError)
    async def investigation_case_not_found_handler(request: Request, exc: InvestigationCaseNotFoundError) -> JSONResponse:
        logger.warning(f"Investigation case not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(ApplicationValidationError)
    async def validation_error_handler(request: Request, exc: ApplicationValidationError) -> JSONResponse:
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(InvestigationTimeoutError)
    async def investigation_timeout_handler(request: Request, exc: InvestigationTimeoutError) -> JSONResponse:
        logger.error(f"Investigation timeout: {exc}")
        return JSONResponse(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            content={"detail": "Investigation timed out. Please try again."},
        )
    
    @app.exception_handler(InvestigationMaxStepsError)
    async def investigation_max_steps_handler(request: Request, exc: InvestigationMaxStepsError) -> JSONResponse:
        logger.error(f"Investigation exceeded maximum steps: {exc}")
        return JSONResponse(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            content={"detail": "Investigation exceeded maximum allowed steps."},
        )
    
    @app.exception_handler(MCPError)
    async def mcp_error_handler(request: Request, exc: MCPError) -> JSONResponse:
        logger.error(f"MCP error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Service temporarily unavailable due to MCP error."},
        )
    
    @app.exception_handler(LLMError)
    async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
        logger.error(f"LLM error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Service temporarily unavailable due to LLM error."},
        )
    
    @app.exception_handler(InvestigationError)
    async def investigation_error_handler(request: Request, exc: InvestigationError) -> JSONResponse:
        logger.error(f"Investigation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal error occurred during investigation."},
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."},
        )
