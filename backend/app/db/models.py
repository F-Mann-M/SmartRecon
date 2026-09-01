import enum
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Numeric, Text, Date, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine


Base = declarative_base()

async def create_tables(engine: AsyncEngine) -> None:
    """Creates all tables in the database."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

# BankAccount model for storing bank account data
class BankAccountModel(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_number_suffix: Mapped[str] = mapped_column(String(34), nullable=False, unique=True)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_holder: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    statement_files: Mapped[list["StatementFileModel"]] = relationship(back_populates="bank_account", cascade="all, delete-orphan")
    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="bank_account", cascade="all, delete-orphan")


# for storing bank statement files and their metadata
class StatementFileModel(Base):
    __tablename__ = "statement_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bank_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bank_accounts.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # SHA-256 Dedup Check
    statement_period: Mapped[Optional[str]] = mapped_column(String(100))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bank_account: Mapped["BankAccountModel"] = relationship(back_populates="statement_files")
    transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="statement_file", cascade="all, delete-orphan")


# Transaction model for storing individual transactions from bank statements
class TransactionModel(Base): 
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bank_account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bank_accounts.id"), nullable=False)
    statement_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("statement_files.id", ondelete="CASCADE"))
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # "IN" or "OUT"
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    balance: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bank_account: Mapped["BankAccountModel"] = relationship(back_populates="transactions")
    statement_file: Mapped[Optional["StatementFileModel"]] = relationship(back_populates="transactions")
    reconciliation: Mapped[Optional["ReconciliationModel"]] = relationship(back_populates="transaction")


# Invoice model for storing invoice data and its embedding
class InvoiceModel(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True)  # Added file_hash to invoices as well
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3), default="EUR")
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reconciliation: Mapped[Optional["ReconciliationModel"]] = relationship(back_populates="invoice")


# Reconciliation model for linking transactions and invoices with a confidence score
class ReconciliationModel(Base):
    __tablename__ = "reconciliations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transactions.id"), unique=True, nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False) # Confidence score between 0 and 1 indicating the likelihood of a match
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transaction: Mapped["TransactionModel"] = relationship(back_populates="reconciliation")
    invoice: Mapped["InvoiceModel"] = relationship(back_populates="reconciliation")