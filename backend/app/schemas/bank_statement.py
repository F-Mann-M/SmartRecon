from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class TransactionSchema(BaseModel):
    transaction_date: date = Field(description="Transaction date in YYYY-MM-DD")
    description: str = Field(description="Cleaned payor/payee or transaction summary")
    amount: float = Field(description="Transaction amount (negative for debit, positive for credit)")
    balance: Optional[float] = Field(description="Running balance if present")
    

class StatementSchema(BaseModel):
    bank_name: str
    account_number_suffix: str
    statement_period: str
    transactions: List[TransactionSchema]