from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class InvoiceSchema(BaseModel):
    vendor_name: Optional[str] = Field(description="Name of the vendor/supplier")
    invoice_date: Optional[date] = Field(description="Invoice date in YYYY-MM-DD")
    total_amount: Optional[float] = Field(description="Total invoice amount")
    tax_amount: Optional[float] = Field(description="Tax or VAT amount")
    currency: Optional[str] = Field(description="Currency of the invoice amount, e.g., USD, EUR")
    description: Optional[str] = Field(default=None, description="Optional description or notes about the invoice")