# Parses invoices PDF and images

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

from db.repositories.invoice_repository import add_chunks_to_collection, parse_and_store_invoice_sql
from db.repositories.utilities import compute_file_hash
from core.config import settings
from db.models import InvoiceModel
from db.session import get_db


def load_from_directory(dir_path: str = settings.RAW_INVOICE_DIR):
    """loads PDF form data/raw and converts them to LangChain Documents"""

    try:
        print("start loading PDF...")
        loader = PyPDFDirectoryLoader(
            path=dir_path, 
            recursive=False)
        
        pages = loader.load()

        if not pages:
            print(f"No PDF found in {dir_path}.")
            return []
        
        print(f"Loaded page count {len(pages)}")
        print("PDF successfully loaded")
        return pages
    
    except Exception as e:
        print(f"Error during loading PDF: {e}")


def split_document(documents, chunk_size=1000, chunk_overlap=200):
    """Takes in a document, split its content into chunks, and return the chunks."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def load_and_process_pdf():
    """Loads PDFs from directory, processes each file individually, and avoids re-embedding existing files."""
    pages = load_from_directory()
    if not pages:
        return

    # Group pages by their file path (PyPDFDirectoryLoader sets doc.metadata["source"])
    files_to_docs = {}
    for doc in pages:
        source_path = doc.metadata.get("source")
        if source_path:
            files_to_docs.setdefault(source_path, []).append(doc)

    # Process each PDF file individually
    for file_path, docs in files_to_docs.items():
        file_name = Path(file_path).name
        print(f"--- Processing Invoice: {file_name} ---")

        try:
            file_hash = compute_file_hash(file_path)

            #  Check and Save Relational Data in PostgreSQL
            with get_db() as db:
                existing_invoice = db.query(InvoiceModel).filter_by(file_hash=file_hash).first()
                if not existing_invoice:
                    # Combine all page contents into full raw text for context-complete LLM parsing
                    full_raw_text = "\n\n".join([doc.page_content for doc in docs])
                    parse_and_store_invoice_sql(db=db, raw_text=full_raw_text, file_path=file_path, file_hash=file_hash)
                else:
                    print(f"Invoice {file_name} already exists in relational database.")

            # Chunk and Embed into PGVector Collection
            chunks = split_document(docs)
            add_chunks_to_collection(documents=chunks, file_path=file_path, file_hash=file_hash)

        except Exception as e:
            print(f"Failed to process invoice {file_name}: {e}")

    print("\nDirectory processing completed successfully.")

