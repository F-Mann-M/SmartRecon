
from db.models import TransactionModel
from core.llm.llm_client import local_llm
from agent.tools.tools import agent_tools
from agent.chat_agent import AgentManager
from parsers.invoice_parser import load_and_process_pdf
from db.session import Base, engine, get_db
from parsers.bank_parser import process_statement_folder
from db.repositories.reconciliation_repository import find_best_invoice_match

import logging
from fastapi import FastAPI

from api.v1.router import router as api_v1_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# create Tables
Base.metadata.create_all(engine)

# loads pdf and stores in PGVector store
load_and_process_pdf()

# loads bank statements from a directory, parses them, and stores in PostgreSQL
process_statement_folder()

# reconciliation
with get_db() as db:
    print(f"\nGet all transactions...")
    transaction = db.query(TransactionModel).all()
    find_best_invoice_match(db=db, transactions=transaction)
    

def create_app() -> FastAPI:
    app = FastAPI(
        title="smartRecon API",
        description="Backend API for bank statement and invoice parsing, vector search, and reconciliation.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
   

    # Register API Routers
    app.include_router(api_v1_router, prefix="/api/router", tags=["API"])

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

    

