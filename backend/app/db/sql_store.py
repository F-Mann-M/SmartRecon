from db.models import StatementFileModel, TransactionModel, InvoiceModel, ReconciliationModel, BankAccountModel
from sqlalchemy.orm import Session


def is_file_already_in_db(db: Session, file_hash: str) -> bool:
    return db.query(StatementFileModel).filter_by(file_hash=file_hash).first() is not None


def save_to_postgres(session: Session, statement_data, file_name: str, file_hash: str) -> StatementFileModel:
    """
    Save the structured statement data to PostgreSQL using SQLAlchemy.
    """

    try:
        # Check if the bank account already exists in the database
        bank_account = session.query(BankAccountModel).filter_by(
            account_number_suffix=statement_data.account_number_suffix,
            bank_name=statement_data.bank_name
        ).first()

        if bank_account:
            print(f"Bank account {statement_data.bank_name} with suffix {statement_data.account_number_suffix} already exists in the database.")

        if not bank_account:
            print(f"Creating new bank account for {statement_data.bank_name} with suffix {statement_data.account_number_suffix}.")
            bank_account = BankAccountModel(
                account_number_suffix=statement_data.account_number_suffix,
                bank_name=statement_data.bank_name,
                account_holder="Unknown"
            )
            session.add(bank_account)
            session.flush()  # Flush to get the bank_account.id

        statement_file = StatementFileModel(
            bank_account_id=bank_account.id,
            file_name=file_name,
            file_hash=file_hash,
            statement_period=statement_data.statement_period
        )
        session.add(statement_file)

        for transaction in statement_data.transactions:
            transaction_model = TransactionModel(
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
            session.add(transaction_model)

        session.commit()
        print(f"Saving {file_name} with hash {file_hash} to PostgreSQL...")
        return statement_file
    except Exception:
        session.rollback()
        print(f"Database error while saving {file_name}: {e}")
        raise
   

# TODO: Consider adding error handling and logging for database operations to ensure robustness and traceability.
# TODO: Add InvoiceModel and ReconciliationModel saving logic
# TODO: Add process for handling transactions and linking them to invoices with confidence scores in the ReconciliationModel.
# TODO: Add invoices to invoices table (LLM parsed) and link them to transactions with confidence scores in the ReconciliationModel.