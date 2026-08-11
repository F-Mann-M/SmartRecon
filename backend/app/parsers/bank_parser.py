from langchain_community.document_loaders import PDFPlumberLoader
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from langchain_ollama import ChatOllama
from core.config import settings
from db.sql_store import is_file_already_in_db, save_to_postgres
from db.vector_store import compute_file_hash

from pathlib import Path
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


def process_statement_folder(folder_path: str = settings.RAW_STATEMENT_DIR):
    """Processes all bank statement PDFs in the specified folder, extracting structured data and saving it to PostgreSQL."""
    directory = Path(folder_path) # get the directory path as a Path object
    pdf_files = list(directory.glob("*.pdf", case_sensitive=False))
    
    print(f"Debug: Looking for PDF files in {directory.resolve()}")
    for pdf_file in pdf_files:
        print(f"Debug: Found PDF file: {pdf_file.name}")

    if not pdf_files:
        print(f"No PDF files found in {directory.resolve()}")
        return

    # Initialize Ollama model once
    # TODO: move llm initialization to llm_client.py and import it here for consistency?!
    llm = ChatOllama(model="gemma4", temperature=0)

    print(f"Found {len(pdf_files)} statement(s) to process in {directory.name}\n")

    for file_path in pdf_files:
        print(f"--- Processing: {file_path.name} ---")

        try:
            # Compute hash
            file_hash = compute_file_hash(file_path)

            # check if file is already in database
            if is_file_already_in_db(file_hash):
                print(f"Skipping {file_path.name} — already present in database.\n")
                continue

            # Parse statement to structured Pydantic object
            statement_data: StatementSchema = parse_statement_to_sql_payload(file_path)

            print(f"\n\nSuccessfully parsed {file_path.name} to structured data.")
            print(f"Bank: {statement_data.bank_name}")
            print(f"Account Suffix: {statement_data.account_number_suffix}")
            print(f"Period: {statement_data.statement_period}")
            #print(f"Extracted {len(statement_data.transactions)} transaction(s).")

            # Save statement_data to PostgreSQL (SQLAlchemy / psycopg)
            save_to_postgres(statement_data, file_name=file_path.name, file_hash=file_hash)

            print(f"Successfully processed and stored {file_path.name}\n")

        except Exception as e:
            print(f"Failed to process {file_path.name}. Error: {e}\n")


def parse_statement_to_sql_payload(pdf_path: str) -> StatementSchema:
    """ Parses a bank statement PDF and returns structured data as a StatementSchema object."""
    loader = PDFPlumberLoader(pdf_path)
    docs = loader.load()
    
    # Combine page contents
    raw_text = "\n".join([doc.page_content for doc in docs])

    # TODO: Consider moving the LLM initialization to a separate module (like llm_client.py) for consistency and easier testing.
    llm = ChatOllama(model="gemma2:9b", temperature=0)
    structured_llm = llm.with_structured_output(StatementSchema)

    prompt = f"""
    Extract all transaction entries and statement metadata from this bank statement text.
    Ensure:
    - All dates are in standard YYYY-MM-DD format.
    - Debit/expenses are strictly NEGATIVE numbers.
    - Credit/deposits are strictly POSITIVE numbers.
    - If no transactions are found, set 'transactions': [].

    Statement Content:
    {raw_text}
    """
    
    return structured_llm.invoke(prompt)


