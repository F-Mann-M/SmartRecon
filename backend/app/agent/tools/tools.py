
from langchain_core.tools import tool
from typing import List, Optional
from datetime import date
from pydantic import Field

from db.repositories.invoice_repository import similarity_search
from db.repositories.bank_repository import BankRepository
from db.session import get_db


@tool
def calculator(expression: str) -> str:
    """A simple calculator that can add, subtract, multiply, or divide two numbers.
    Input should be a mathematical expression like '2 + 2' or '15 / 3'."""
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the internal knowledge base for relevant document chunks and context.
    Use this tool whenever you need to look up information from uploaded invoices, 
    PDFs, or internal documents to answer the user's request.
    
    Args:
        query: The semantic search query string.
    """
    results = similarity_search(query)
 
    return results

@tool
def get_all_transactions(
        vendor_name: str = Field(default=None, description="Filter by vendor name"),
        transaction_date: date = Field(default=None, description="Filter by transaction date in YYYY-MM-DD format"),
        amount: float = Field(default=None, description="Filter by transaction amount"),
        direction: str = Field(default=None, description="Filter by transaction direction (e.g., IN or OUT)"),
        category: str = Field(default=None, description="Filter by transaction category"),
        status: str = Field(default=None, description="Filter by transaction status like PENDING, RECONCILED, etc."),
        bank_name: str = Field(default=None, description="Filter by bank name"),
        account_number_suffix: str = Field(default=None, description="Filter by last few digits of the account number"),
        start_date: date = Field(default=None, description="Filter by start date in YYYY-MM-DD format"),
        end_date: date = Field(default=None, description="Filter by end date in YYYY-MM-DD format"),
    ) -> List[dict]:
    """
    Retrieve all transactions from the database.
    This tool can be used to fetch transaction data for analysis or reconciliation.
    It can also filter transactions based on various criteria like vendor name, date, amount, direction, category, status, bank name, and account number suffix.
    Args:
        vendor_name: Optional; Filter transactions by vendor name.
        transaction_date: Optional; Filter transactions by date in YYYY-MM-DD format.
        amount: Optional; Filter transactions by amount.
        direction: Optional; Filter transactions by direction (IN or OUT). it only
        category: Optional; Filter transactions by category.
        status: Optional; Filter transactions by status (e.g., PENDING, RECONCILED, DISPUTED).
        bank_name: Optional; Filter transactions by bank name.
        account_number_suffix: Optional; Filter transactions by the last few digits of the account number.
        time_period: Optional; Filter transactions by statement period as a tuple of start and end dates in YYYY-MM-DD format.
    Returns:
        A list of dictionaries, each representing a transaction with its details.
    """

    with get_db() as db:
        bank_repo = BankRepository(db)
        transactions = bank_repo.get_transaction_by_filter(
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
        return transactions
    
# Tool List
agent_tools = [calculator, search_knowledge_base, get_all_transactions]