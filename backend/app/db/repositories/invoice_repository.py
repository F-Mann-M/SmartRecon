from langchain_postgres import PGVector
from typing import List, Optional
from langchain_core.documents import Document
from sqlalchemy.orm import Session
import os
from langchain_ollama import ChatOllama

from core.llm.llm_client import local_embeddings
from core.config import settings
from db.models import InvoiceModel
from schemas.invoice import InvoiceSchema


# TODO: Consider moving vector_store initialization to a separate module or configuration file for better maintainability and testability.

vector_store = PGVector(
    embeddings=local_embeddings,
    collection_name="invoice",
    connection=settings.DATABASE_URL,
    use_jsonb=True,
)


def file_already_embedded(file_path: Optional[str] = None, file_hash: Optional[str] = None) -> bool:
    """Return True if any documents with the given file_hash already exist in the vector store.

    Accepts either a file_path or a precomputed file_hash. If both provided, file_hash is used.
    Uses a filter-based search on the vector_store to look up documents with matching metadata.
    Falls back to a filename-based check if file_hash checks fail (best-effort).
    """

    print("\nChecking if file is already embedded...")
    print(f"file_path: {file_path}, file_hash: {file_hash}")

    if not file_hash:
        if not file_path:
            raise ValueError("Either file_path or file_hash must be provided")
        file_hash = compute_file_hash(file_path)

    # Try exact match by file_hash using vector_store's filter. Use a cheap k=1 query — we only need to know if any record exists.
    try:
        results = vector_store.similarity_search(query=".", k=1, filter={"file_hash": file_hash}) # check if any document with this hash exists
        if results:
            print(f"File with hash {file_hash} already embedded.")
            return True # if any document with this hash exists, we consider the file already embedded
    except Exception as e:
        # If filter is not supported or other errors occur, continue to fallback
        print(f"file_already_embedded: hash-based check failed: {e}")

    # Fallback: check by file_name if we have a path
    if file_path:
        file_name = os.path.basename(file_path)
        try:
            results = vector_store.similarity_search(query=".", k=1, filter={"file_name": file_name})
            if results:
                return True
        except Exception as e:
            print(f"file_already_embedded: file_name-based check failed: {e}")

    return False


def add_chunks_to_collection(documents: List[Document], file_path: Optional[str] = None, file_hash: Optional[str] = None) -> None:
    """
    Takes in a list of LangChain Documents, generate embeddings, and insert them into the PGVector.

    Optional parameters:
    - file_path: path to the original PDF file (used to compute file_hash for dedup checks)
    - file_hash: precomputed hash for the file (skips computing it locally)

    If a file is already embedded (detected by file_hash or file_name), the function will skip embedding.
    """

    if not documents:
        print("No documents provided")
        return

    # check for duplicates before embedding
    try:
        already = False
        if file_hash or file_path:
            already = file_already_embedded(file_path=file_path, file_hash=file_hash)
        if already:
            print("File already embedded — skipping embedding.")
            return
    except Exception as e:
        # If dedup check fails for any reason, log and proceed to avoid blocking ingestion
        print(f"Dedup check failed, proceeding to embed. Error: {e}")

    # Ensure each document carries the file_hash (compute if necessary) so future checks can rely on it
    if not file_hash and file_path:
        try:
            file_hash = compute_file_hash(file_path)
        except Exception:
            file_hash = None

    if file_hash:
        for doc in documents:
            meta = doc.metadata or {}
            if "file_hash" not in meta:
                meta["file_hash"] = file_hash
            if "file_name" not in meta and file_path:
                meta["file_name"] = os.path.basename(file_path)
            doc.metadata = meta

    vector_store.add_documents(documents=documents)

    print("Chunks successfully embedded")


def similarity_search(query: str, n_results: int = 3, where_filter: dict = None) -> list:
    """
    Takes in query and execute basic similarity search
    format output to downstream to llm
    """
    print("\nStart similarity search...")

    results = vector_store.similarity_search(
         query=query,
         k=n_results,
         filter=where_filter
    )

    if not results:
            return "No relevant documents found in the knowledge base."
    
    
    context_blocks = []
    for doc in results:
        meta = doc.metadata or {}
        
        # Extract metadata fallback values
        source_path = meta.get("file_name", meta.get("source", "Unknown Source"))
        source_name = os.path.basename(source_path)
        page = meta.get("page", 0)
        
        context_blocks.append(f"--- Source: {source_name} (Page {page}) ---\n{doc.page_content}")

    return "\n\n".join(context_blocks)


def parse_and_store_invoice_sql(db: Session, raw_text: str, file_hash: str, file_path: str) -> InvoiceModel:
    """
    Parses the raw text of an invoice, structures data by using a LLM and store structured data in the database.
    Returns the created InvoiceModel instance.
    """
    llm = ChatOllama(model="llama3.1:8b", temperature=0)
    structured_llm = llm.with_structured_output(InvoiceSchema)

    prompt = f"""
You are an AI assistant that extracts structured data from invoice text: \n{raw_text}\n
Please extract the following fields:
- vendor_name: Name of the vendor/supplier
- invoice_date: Invoice date in YYYY-MM-DD format
- total_amount: Total invoice amount
- tax_amount: Tax or VAT amount
- currency: Currency of the invoice amount, e.g., USD, EUR
- description: Description or notes about the invoice or any additional relevant information like invoice number
Return the extracted data in JSON format adhering to the InvoiceSchema.
    """
    print(f"\nParsing invoice data for file {file_path} with hash {file_hash}...")
    data: InvoiceSchema = structured_llm.invoke(prompt)

    # Create and store the InvoiceModel instance in the database
    invoice = InvoiceModel(
        vendor_name=data.vendor_name,
        invoice_date=data.invoice_date,
        total_amount=data.total_amount,
        tax_amount=data.tax_amount,
        currency=data.currency,
        description=data.description, # TODO: Check why description is always None — might be an issue with LLM parsing or schema mapping
        file_hash=file_hash,
        file_path=file_path,
        raw_text=raw_text
    )
    print(f"\nStoring invoice data in PostgreSQL for file {file_path} with hash {file_hash}...")
    for field, value in data.dict().items():
        print(f"{field}: {value}")

    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

def get_invoice_by_hash(db: Session, file_hash: str) -> Optional[InvoiceModel]:
    """Retrieve an invoice from the database by its file hash."""
    return db.query(InvoiceModel).filter_by(file_hash=file_hash).first()


def get_all_invoices(db: Session) -> List[dict]:
    return db.query(InvoiceModel).all()