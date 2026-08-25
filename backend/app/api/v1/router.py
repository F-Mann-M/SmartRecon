from datetime import date

from fastapi import APIRouter, Depends
from pydantic import Field
from sqlalchemy.orm import Session
from typing import List, Tuple

from db.session import get_db_fastapi
from db.repositories.bank_repository import BankRepository
from db.repositories.invoice_repository import get_all_invoices, get_invoice_by_filter
from db.repositories.reconciliation_repository import get_all_reconciliation_entries
from schemas.transaction import DetailedTransactionSchema

router = APIRouter()


# transaction endpoints
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


@router.get("/transactions/filtered", response_model=List[DetailedTransactionSchema])
def get_filtered_transactions(
    vendor_name: str = None,
    transaction_date: date = None,
    amount: float = None,
    direction: str = None,
    category: str = None,
    status: str = None,
    bank_name: str = None,
    account_number_suffix: str = None,
    start_date: date = None, # Start date for filtering transactions (YYYY-MM-DD)
    end_date: date = None,   # End date for filtering transactions (YYYY-MM-DD)
    db: Session = Depends(get_db_fastapi)
):
    """
    Retrieves transactions from the database based on provided filters.
    """
    repo = BankRepository(db_session=db)
    filtered_transactions = repo.get_transaction_by_filter(
        vendor_name=vendor_name,
        transaction_date=transaction_date,
        amount=amount,
        direction=direction,
        category=category,
        status=status,
        bank_name=bank_name,
        account_number_suffix=account_number_suffix,
        start_date=start_date,
        end_date=end_date,
    )
    return filtered_transactions



# invoice endpoints
@router.get("/invoices")
def get_invoices(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all invoices from the database.
    """
    invoices = get_all_invoices(db=db)
    return invoices


@router.get("/invoices/filtered")
def get_filtered_invoices(
    vendor_name: str = None,
    invoice_date: date = None,
    total_amount: float = None,
    invoice_id: str = None,
    db: Session = Depends(get_db_fastapi)
):
    """
    Retrieves invoices from the database based on provided filters.
    """
    filtered_invoices = get_invoice_by_filter(
        db=db,
        vendor_name=vendor_name,
        invoice_date=invoice_date,
        total_amount=total_amount,
        invoice_id=invoice_id
    )
    return filtered_invoices



# reconciliation endpoints
@router.get("/reconciliation")
def get_all_reconciliation(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all reconciliation entries from the database.
    """
    reconciliations = get_all_reconciliation_entries(db=db)
    return reconciliations

