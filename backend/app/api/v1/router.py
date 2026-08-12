from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db_fastapi
from db.repositories.bank_repository import BankRepository

router = APIRouter()

@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db_fastapi)):
    """
    Endpoint to retrieve all transactions from the database.
    """
    bank_repo = BankRepository(db_session=db)
    transactions = bank_repo.get_transaction()
    return transactions

