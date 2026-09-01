
from sqlalchemy import select
from db.models import TransactionModel, create_tables
from parsers.invoice_parser import load_and_process_pdf
from db.session import engine, get_db
from parsers.bank_parser import process_statement_folder
from db.repositories.reconciliation_repository import find_best_invoice_match

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.v1.router import router as api_v1_router
from api.v1.agent import chat_router as api_v1_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_startup_pipeline() -> None:
    """Runs table creation, ingestion, and reconciliation once at app startup."""
    # create Tables
    await create_tables(engine)

    # loads pdf and stores in PGVector store
    await load_and_process_pdf()

    # loads bank statements from a directory, parses them, and stores in PostgreSQL
    await process_statement_folder()

    # reconciliation
    async with get_db() as db:
        print(f"\nGet all transactions...")
        result = await db.execute(select(TransactionModel))
        transaction = result.scalars().all()
        await find_best_invoice_match(db=db, transactions=transaction)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs startup pipeline in the same event loop uvicorn uses, before serving requests."""
    await run_startup_pipeline()
    yield
    # TODO: add any shutdown logic here, if needed in the future.

def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="smartRecon API",
        description="Backend API for bank statement and invoice parsing, vector search, and reconciliation.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
   

    # Register API Routers
    app.include_router(api_v1_router, prefix="/api/v1/router", tags=["API"])
    app.include_router(api_v1_agent, prefix="/api/v1/agent", tags=["API Agent"])

    @app.get("/health", tags=["Health"])
    def health_check():
        """Health check endpoint for container probes and monitoring."""
        return {"status": "ok", "service": "smartRecon-backend"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Run application using uvicorn when executing main.py directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

    

