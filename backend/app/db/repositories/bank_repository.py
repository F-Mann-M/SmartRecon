from db.models import StatementFileModel, TransactionModel, InvoiceModel, ReconciliationModel, BankAccountModel
from schemas.bank_statement import StatementSchema, TransactionSchema
from sqlalchemy.orm import Session
from typing import List

class BankRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def is_file_already_in_db(self, file_hash: str) -> bool:
        return self.db_session.query(StatementFileModel).filter_by(file_hash=file_hash).first() is not None


    def save_to_postgres(self, statement_data, file_name: str, file_hash: str) -> StatementFileModel:
        """
        Save the structured statement data to PostgreSQL using SQLAlchemy.
        """

        try:
            # Check if the bank account already exists in the database
            bank_account = self.get_or_create_bank_account(statement_data.bank_name, statement_data.account_number_suffix)

            # Create a new StatementFileModel entry
            statement_file = StatementFileModel(
                bank_account_id=bank_account.id,
                file_name=file_name,
                file_hash=file_hash,
                statement_period=statement_data.statement_period
            )
            self.db_session.add(statement_file)
            self.db_session.flush()  # Flush to get the statement_file.id

            # Add transactions to the database
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
                    balance=transaction.balance
                )
                self.db_session.add(transaction_model)

            self.db_session.commit()
            print(f"Saving {file_name} with hash {file_hash} to PostgreSQL...")
            return statement_file
        
        except Exception as e:
            self.db_session.rollback()
            print(f"Database error while saving {file_name}: {e}")
            raise


    def get_or_create_bank_account(self, bank_name: str, account_number_suffix: str) -> BankAccountModel:
        """
        Check if a bank account exists in the database. If not, create a new one."""
        # TODO: consider to put the function back into the save_to_postgres function, as it is only used there.
        # Check if the bank account already exists in the database
        bank_account = self.db_session.query(BankAccountModel).filter_by(
            account_number_suffix=account_number_suffix,
            bank_name=bank_name
        ).first()

        if bank_account:
            print(f"Bank account {bank_name} with suffix {account_number_suffix} already exists in the database.")

        # If the bank account does not exist, create a new one
        if not bank_account:
            print(f"Creating new bank account for {bank_name} with suffix {account_number_suffix}.")
            bank_account = BankAccountModel(
                account_number_suffix=account_number_suffix,
                bank_name=bank_name,
                account_holder="Unknown"
            )
            self.db_session.add(bank_account)
            self.db_session.flush()  # Flush to get the bank_account.id
            return bank_account


    def get_transaction(self) -> TransactionModel:
        return self.db_session.query(TransactionModel).all()


    def get_detailed_transactions(self) -> List[dict]:
        """
        Executes an explicit SQL JOIN across transactions, bank_accounts, 
        statement_files, and reconciliations/invoices.
        """
        results = (
            self.db_session.query(
                TransactionModel.id,
                TransactionModel.transaction_date,
                TransactionModel.vendor_name,
                TransactionModel.amount,
                TransactionModel.currency,
                TransactionModel.description,
                TransactionModel.status,
                TransactionModel.balance,
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
            .all()
        )

        # Convert SQLAlchemy Row objects to dicts for Pydantic parsing
        return [row._asdict() for row in results]
 
# TODO: Avoid duplicates. currently there a duplicates in database!!! 
# TODO: Consider adding error handling and logging for database operations to ensure robustness and traceability.
# TODO: Add InvoiceModel and ReconciliationModel saving logic
# TODO: Add process for handling transactions and linking them to invoices with confidence scores in the ReconciliationModel.
# TODO: Add invoices to invoices table (LLM parsed) and link them to transactions with confidence scores in the ReconciliationModel.