from db.models import StatementFileModel, TransactionModel, InvoiceModel, ReconciliationModel, BankAccountModel
from schemas.bank_statement import StatementSchema, TransactionSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from datetime import date

class BankRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def is_file_already_in_db(self, file_hash: str) -> bool:
        result = await self.db_session.execute(
            select(StatementFileModel).filter_by(file_hash=file_hash)
        )
        return result.scalars().first() is not None

    def set_transaction_direction(self, transaction: float) -> str:
        if transaction < 0:
            return "OUT"
        return "IN"
    

    async def save_to_postgres(self, statement_data, file_name: str, file_hash: str) -> StatementFileModel:
        """
        Save the structured statement data to PostgreSQL using SQLAlchemy.
        """

        try:
            # Check if the bank account already exists in the database
            bank_account = await self.get_or_create_bank_account(statement_data.bank_name, statement_data.account_number_suffix)

            # Create a new StatementFileModel entry
            print("\n\nSaving statement data to PostgreSQL...")
            statement_file = StatementFileModel(
                bank_account_id=bank_account.id,
                file_name=file_name,
                file_hash=file_hash,
                statement_period=statement_data.statement_period
            )
            self.db_session.add(statement_file)
            await self.db_session.flush()
            
            # Add transactions to the database
            print(f"Saving {len(statement_data.transactions)} transactions to PostgreSQL...")
            for transaction in statement_data.transactions:                
                transaction_model = TransactionModel(
                    vendor_name=transaction.vendor_name,
                    bank_account_id=bank_account.id,
                    statement_file_id=statement_file.id,
                    transaction_date=transaction.transaction_date,
                    amount=transaction.amount,
                    currency="EUR",
                    description=transaction.description,
                    category=None,
                    status="PENDING",
                    balance=transaction.balance,
                    direction=self.set_transaction_direction(transaction.amount)
                )
                self.db_session.add(transaction_model)

            await self.db_session.commit()
            print(f"Saving {file_name} with hash {file_hash} to PostgreSQL...")
            return statement_file
        
        except Exception as e:
            await self.db_session.rollback()
            print(f"Database error while saving {file_name}: {e}")
            raise


    async def get_or_create_bank_account(self, bank_name: str, account_number_suffix: str) -> BankAccountModel:
        """
        Check if a bank account exists in the database. If not, create a new one."""
        # TODO: consider to put the function back into the save_to_postgres function, as it is only used there.
        # Check if the bank account already exists in the database
        result = await self.db_session.execute(
            select(BankAccountModel).filter_by(
                account_number_suffix=account_number_suffix,
                bank_name=bank_name
            )
        )
        bank_account = result.scalars().first()

        if bank_account:
            print(f"Bank account {bank_name} with suffix {account_number_suffix} already exists in the database.")
            return bank_account

        # If the bank account does not exist, create a new one
        if not bank_account:
            print(f"Creating new bank account for {bank_name} with suffix {account_number_suffix}.")
            bank_account = BankAccountModel(
                account_number_suffix=account_number_suffix,
                bank_name=bank_name,
                account_holder="Unknown"
            )
            self.db_session.add(bank_account)
            await self.db_session.flush()  # Flush to get the bank_account.id
            return bank_account


    async def get_transaction(self) -> List[TransactionModel]:
        all_transactions = (await self.db_session.scalar(select(TransactionModel))).all()
        return all_transactions


    async def get_detailed_transactions(self) -> List[dict]:
        """
        Executes an explicit SQL JOIN across transactions, bank_accounts, 
        statement_files, and reconciliations/invoices.
        """
        stmt = (
            select(
                TransactionModel.id,
                TransactionModel.transaction_date,
                TransactionModel.vendor_name,
                TransactionModel.amount,
                TransactionModel.currency,
                TransactionModel.description,
                TransactionModel.status,
                TransactionModel.balance,
                TransactionModel.direction,
                BankAccountModel.bank_name,
                BankAccountModel.account_number_suffix,
                StatementFileModel.file_name,
                StatementFileModel.statement_period,
                ReconciliationModel.invoice_id.label("reconciled_invoice_id"),
                InvoiceModel.vendor_name.label("reconciled_vendor_name"),
                ReconciliationModel.confidence_score,
            )
            .join(BankAccountModel, TransactionModel.bank_account_id == BankAccountModel.id)
            .outerjoin(StatementFileModel, TransactionModel.statement_file_id == StatementFileModel.id)
            .outerjoin(ReconciliationModel, TransactionModel.id == ReconciliationModel.transaction_id)
            .outerjoin(InvoiceModel, ReconciliationModel.invoice_id == InvoiceModel.id)
            .order_by(TransactionModel.transaction_date.desc())
        )

        result = await self.db_session.execute(stmt)

        # Convert SQLAlchemy Row objects to dicts for Pydantic parsing
        return [row._asdict() for row in result.all()] # use _asdict() to convert Row objects to dicts for LLM parsing and Pydantic validation.
    
    async def get_all_invoices(self) -> List[InvoiceModel]:
        """
        Retrieve all invoices from the database.
        """
        result = await self.db_session.execute(select(InvoiceModel))
        return result.scalars().all()
    
    
    async def get_transaction_by_filter(
        self, 
        vendor_name: str = None, 
        transaction_date: date = None, 
        amount: float = None,
        direction: str = None, # "IN" or "OUT"
        category: str = None,
        status: str = None, # "PENDING", "RECONCILED", "DISPUTED"
        bank_name: str = None,
        account_number_suffix: str = None,
        start_date: date = None,
        end_date: date = None,
        ) -> List[dict]:
        """
        Retrieve transactions from the database based on provided filters.
        """
        stmt = (
            select(
                TransactionModel.id,
                TransactionModel.transaction_date,
                TransactionModel.vendor_name,
                TransactionModel.amount,
                TransactionModel.currency,
                TransactionModel.description,
                TransactionModel.status,
                TransactionModel.balance,
                TransactionModel.direction,
                BankAccountModel.bank_name,
                BankAccountModel.account_number_suffix,
                StatementFileModel.file_name,
                StatementFileModel.statement_period,
                ReconciliationModel.invoice_id.label("reconciled_invoice_id"),
                InvoiceModel.vendor_name.label("reconciled_vendor_name"),
                ReconciliationModel.confidence_score,
            )
            .join(BankAccountModel, TransactionModel.bank_account_id == BankAccountModel.id)
            .outerjoin(StatementFileModel, TransactionModel.statement_file_id == StatementFileModel.id)
            .outerjoin(ReconciliationModel, TransactionModel.id == ReconciliationModel.transaction_id)
            .outerjoin(InvoiceModel, ReconciliationModel.invoice_id == InvoiceModel.id)
        )

        if vendor_name:
            stmt = stmt.where(TransactionModel.vendor_name.ilike(f"%{vendor_name.lower()}%"))
        if transaction_date:
            stmt = stmt.where(TransactionModel.transaction_date == transaction_date)
        if amount:
            stmt = stmt.where(TransactionModel.amount == amount)
        if direction:
            stmt = stmt.where(TransactionModel.direction == direction)
        if category:
            stmt = stmt.where(TransactionModel.category.ilike(f"%{category}%"))
        if status:
            stmt = stmt.where(TransactionModel.status == status)
        if bank_name:
            stmt = stmt.where(
                (BankAccountModel.bank_name.ilike(f"%{bank_name}%"))
            )
        if account_number_suffix:
            stmt = stmt.where(
                BankAccountModel.account_number_suffix.ilike(f"%{account_number_suffix}%")
            )
        if start_date and end_date:
            stmt = stmt.where(TransactionModel.transaction_date.between(start_date, end_date))

        stmt = stmt.order_by(TransactionModel.transaction_date.desc())

        result = await self.db_session.execute(stmt)
        return [row._asdict() for row in result.all()]


# TODO: Consider adding error handling and logging for database operations to ensure robustness and traceability.
    