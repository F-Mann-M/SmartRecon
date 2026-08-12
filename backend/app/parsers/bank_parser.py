from langchain_community.document_loaders import PDFPlumberLoader
import langchain
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import date
from langchain_ollama import ChatOllama
from core.config import settings
from db.repositories.bank_repository import BankRepository
from db.repositories.invoice_repository import compute_file_hash
from db.session import get_db
from schemas.bank_statement import StatementSchema, TransactionSchema

from pathlib import Path
from datetime import date

bank_repo = BankRepository(db_session=get_db())  # Initialize the repository with a database session
langchain.debug = True  # Enable debug mode for LangChain to get detailed logs

def process_statement_folder(folder_path: str = settings.RAW_STATEMENT_DIR):
    """Processes all bank statement PDFs in the specified folder, extracting structured data and saving it to PostgreSQL."""
    directory = Path(folder_path) # get the directory path as a Path object
    pdf_files = list(directory.glob("*.pdf", case_sensitive=False))
    
    print(f"\nDebug: Looking for PDF files in {directory.resolve()}")
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
            with get_db() as db:
                bank_repo = BankRepository(db_session=db)
                if bank_repo.is_file_already_in_db(file_hash):
                    print(f"Skipping {file_path.name} — already present in database.\n")
                    continue
           
            # Parse statement to structured Pydantic object
            statement_data: StatementSchema = parse_statement_to_sql_payload(file_path)

            print(f"\n\nSuccessfully parsed {file_path.name} to structured data.")
            print(f"Bank: {statement_data.bank_name}")
            print(f"Account Suffix: {statement_data.account_number_suffix}")
            print(f"Period: {statement_data.statement_period}")
            print(f"Extracted {len(statement_data.transactions)} transaction(s).")

            # Save statement_data to PostgreSQL (SQLAlchemy / psycopg)
            with get_db() as db:
                bank_repo = BankRepository(db_session=db)
                bank_repo.save_to_postgres(statement_data, file_name=file_path.name, file_hash=file_hash)

            print(f"Successfully processed and stored {file_path.name}\n")

        except Exception as e:
            print(f"Failed to process {file_path.name}. Error: {e}\n")



def parse_statement_to_sql_payload(pdf_path: Union[str, Path])-> StatementSchema:
    """
    Parses a bank statement PDF page-by-page and returns consolidated structured data.
    """
    path_str = str(pdf_path)
    loader = PDFPlumberLoader(path_str)
    docs = loader.load()

    if not docs:
        raise ValueError(f"No pages or text extracted from {path_str}")

    # Initialize LLM if not injected by caller (llama3.1:8b recommended for reliable schema adherence)
    llm = ChatOllama(model="gemma2:9b", temperature=0, verbose=True)

    structured_llm = llm.with_structured_output(StatementSchema)

    combined_transactions = []
    metadata = {
        "bank_name": None,
        "account_number_suffix": None,
        "statement_period": None,
    }

    # Process page-by-page to minimize TTFT and avoid hitting memory limits
    for page_idx, page in enumerate(docs, start=1):
        print(f"\n--- Parsing page {page_idx} of {len(docs)} ---")
        page_text = page.page_content.strip()
        if not page_text:
            continue

        prompt = f"""
        Extract transaction entries and statement metadata from this bank statement page (Page {page_idx} of {len(docs)}).

        CRITICAL RULES:
        - You MUST include the 'transactions' list field in your JSON response.
        - If no transactions exist on this specific page, set 'transactions': [].
        - All dates MUST be in standard YYYY-MM-DD format.
        - Expenses/debits MUST be negative numbers (e.g. -45.50).
        - Deposits/credits MUST be positive numbers (e.g. 1200.00).

        Page Content:
        {page_text}
        """

        try:
            print(f"\nParsing page {page_idx} of {len(docs)}...")
            page_data: StatementSchema = structured_llm.invoke(prompt)

            # Capture metadata from the first page that contains it
            if page_data.bank_name and not metadata["bank_name"]:
                metadata["bank_name"] = page_data.bank_name
            if page_data.account_number_suffix and not metadata["account_number_suffix"]:
                metadata["account_number_suffix"] = page_data.account_number_suffix
            if page_data.statement_period and not metadata["statement_period"]:
                metadata["statement_period"] = page_data.statement_period

            # Collect transactions from this page
            if page_data.transactions:
                combined_transactions.extend(page_data.transactions)

        except Exception as e:
            print(f"Warning: Failed to parse page {page_idx} of {path_str}: {e}")
            continue

    # Return unified StatementSchema containing all gathered transactions
    return StatementSchema(
        bank_name=metadata["bank_name"] or "Unknown Bank",
        account_number_suffix=metadata["account_number_suffix"] or "Unknown",
        statement_period=metadata["statement_period"] or "Unknown",
        transactions=combined_transactions,
    )


