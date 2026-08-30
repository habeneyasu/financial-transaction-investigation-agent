"""Main application entry point for the financial transaction investigation agent."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.config.settings import settings
from app.core.logging import setup_logging, get_logger
from app.data.database import db


# Initialize logging at application startup
setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Financial Transaction Investigation Agent")
    
    # Initialize database
    logger.info("Initializing database")
    db.initialize_schema()
    db.seed_data()
    logger.info("Database initialized and seeded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Financial Transaction Investigation Agent")
    db.close()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Financial Transaction Investigation Agent",
        description="An agentic system for investigating financial transaction disputes using LLM reasoning and controlled data access via MCP.",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug,
    )
    
    # Register global exception handlers
    register_exception_handlers(app)
    
    # Include routers
    from app.api.routes.mcp import router as mcp_router
    app.include_router(mcp_router, prefix="/api/v1")
    # from app.api.routes.investigation import router as investigation_router
    # app.include_router(investigation_router, prefix="/api/v1", tags=["investigation"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "financial-transaction-investigation-agent"}
    
    logger.info("FastAPI application created")
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
