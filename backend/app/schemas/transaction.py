from pydantic import BaseModel
from datetime import date
from typing import Optional
import uuid

class DetailedTransactionSchema(BaseModel):
    # Transaction Fields
    id: uuid.UUID
    transaction_date: date
    amount: float
    currency: str
    description: str
    status: str
    balance: Optional[float] = None
    
    # Joined Bank Account Fields
    bank_name: str
    account_number_suffix: str
    
    # Joined Statement File Fields
    file_name: Optional[str] = None
    statement_period: Optional[str] = None

    # Joined Invoice / Reconciliation Fields (if matched)
    reconciled_invoice_id: Optional[uuid.UUID] = None
    reconciled_vendor_name: Optional[str] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True