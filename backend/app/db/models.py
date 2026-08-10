import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Numeric, Text, Date, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from backend.app.db.session import Base

timezone = datetime.now().astimezone().tzinfo  # Get the local timezone


# BankAccount model for storing bank account data
class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_holder: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(datetime.timezone.utc))

    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="bank_account")


# Invoice model for storing invoice data and embeddings
class TransactionModel(Base): 
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reconciliation: Mapped[Optional["ReconciliationModel"]] = relationship(back_populates="transaction")
    bank_account: Mapped["BankAccountModel"] = relationship(back_populates="transactions")
    

# Invoice model for storing invoice data and embeddings
class InvoiceModel(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(768)) # Match model output dim
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reconciliation: Mapped[Optional["ReconciliationModel"]] = relationship(back_populates="invoice")


# Reconciliation model for linking transactions and invoices
class ReconciliationModel(Base):
    __tablename__ = "reconciliations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"), unique=True, nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transaction: Mapped["TransactionModel"] = relationship(back_populates="reconciliation")
    invoice: Mapped["InvoiceModel"] = relationship(back_populates="reconciliation")