# Parses invoices PDF and images

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from db.vector_store import add_chunks_to_collection, compute_file_hash
from core.config import settings
import logging


# logger = logging.basicConfig()

# def load_pdf(file_path):
#     """Load a PDF file and return its content as a list of documents."""
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()
#     return documents

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

    # Process each file individually with its own hash
    for file_path, docs in files_to_docs.items():
        try:
            file_hash = compute_file_hash(file_path)
            chunks = split_document(docs)
            add_chunks_to_collection(documents=chunks, file_path=file_path, file_hash=file_hash)
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

    print("Directory processing completed.")
