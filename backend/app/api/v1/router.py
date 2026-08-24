from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db_fastapi
from db.repositories.bank_repository import BankRepository
from db.repositories.invoice_repository import get_all_invoices
from schemas.transaction import DetailedTransactionSchema



router = APIRouter()

@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all transactions from the database.
    """
    bank_repo = BankRepository(db_session=db)
    transactions = bank_repo.get_transaction()
    return transactions


@router.get("/transactions/detailed", response_model=List[DetailedTransactionSchema])
def get_all_detailed_transactions(db: Session = Depends(get_db_fastapi)):
    """
    Retrieves a complete overview of all transactions with joined account, 
    statement, and reconciliation metadata.
    """
    repo = BankRepository(db_session=db)
    detailed_transactions = repo.get_detailed_transactions()
    return detailed_transactions


@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all invoices from the database.
    """
    invoices = get_all_invoices(db=db)
    return invoices


@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all invoices from the database.
    """
    invoices = get_all_invoices(db=db)
    return invoices