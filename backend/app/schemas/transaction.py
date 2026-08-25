from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
import uuid

        
class DetailedTransactionSchema(BaseModel):
    # Transaction Fields
    id: uuid.UUID = Field(default=None, description="Unique identifier for the transaction")
    transaction_date: Optional[date] = Field(default=None, description="Date of the transaction in YYYY-MM-DD format")
    amount: Optional[float] = Field(default=None, description="Amount of the transaction")
    direction: Optional[str] = Field(default=None, description="Direction of the transaction (e.g., IN or OUT)")
    currency: Optional[str] = Field(default=None, description="Currency of the transaction")
    description: Optional[str] = Field(default=None, description="Description of the transaction")
    status: Optional[str] = Field(default=None, description="Status of the transaction")
    balance: Optional[float] = Field(default=None, description="Balance after the transaction")
    vendor_name: Optional[str] = Field(default=None, description="Name of the vendor involved in the transaction")
    
    # Joined Bank Account Fields
    bank_name: Optional[str] = Field(default=None, description="Name of the bank")
    account_number_suffix: Optional[str] = Field(default=None, description="Last few digits of the account number")
    
    # Joined Statement File Fields
    file_name: Optional[str] = Field(default=None, description="Name of the statement file")
    statement_period: Optional[str] = Field(default=None, description="Statement period in YYYY-MM format")

    # Joined Invoice / Reconciliation Fields (if matched)
    reconciled_invoice_id: Optional[uuid.UUID] = Field(default=None, description="ID of the reconciled invoice")
    reconciled_vendor_name: Optional[str] = Field(default=None, description="Name of the reconciled vendor")
    confidence_score: Optional[float] = Field(default=None, description="Confidence score of the reconciliation match")

    class Config:
        from_attributes = True