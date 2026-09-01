# Parses invoices PDF and images

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

from db.repositories.invoice_repository import add_chunks_to_collection, parse_and_store_invoice_sql
from db.repositories.utilities import compute_file_hash
from core.config import settings
from db.models import InvoiceModel
from db.session import get_db


def get_raw_invoice_dir() -> Path:
    """Returns the path or the blob storage directory where raw invoice PDFs are stored."""
    if settings.ENVIRONMENT == "cloud":
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set in the environment variables.")
        return Path(settings.AZURE_STORAGE_CONNECTION_STRING)
    return Path(settings.RAW_INVOICE_DIR)

async def load_from_directory(dir_path: str = None):
    """adds PDF form data/raw and converts them to LangChain Documents"""
    if dir_path is None:
            dir_path = str(get_raw_invoice_dir())
            
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


async def split_document(documents, chunk_size=1000, chunk_overlap=200):
    """Takes in a document, split its content into chunks, and return the chunks."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


async def load_and_process_pdf():
    """Loads PDFs from directory, processes each file individually, and avoids re-embedding existing files."""
    pages = await load_from_directory()
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
            async with await get_db() as db:
                existing_invoice = await db.query(InvoiceModel).filter_by(file_hash=file_hash).first()
                if not existing_invoice:
                    # Combine all page contents into full raw text for context-complete LLM parsing
                    full_raw_text = "\n\n".join([doc.page_content for doc in docs])
                    await parse_and_store_invoice_sql(db=db, raw_text=full_raw_text, file_path=file_path, file_hash=file_hash)
                else:
                    print(f"Invoice {file_name} already exists in relational database.")

            # Chunk and Embed into PGVector Collection
            chunks = await split_document(docs)
            await add_chunks_to_collection(documents=chunks, file_path=file_path, file_hash=file_hash)

        except Exception as e:
            print(f"Failed to process invoice {file_name}: {e}")

    print("\nDirectory processing completed successfully.")

