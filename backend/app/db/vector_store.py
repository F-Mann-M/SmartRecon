from core.llm.llm_client import local_embeddings
from core.config import settings
from langchain_postgres import PGVector
from typing import List, Optional
from langchain_core.documents import Document
import os
import hashlib

vector_store = PGVector(
    embeddings=local_embeddings,
    collection_name="invoice",
    connection=settings.DATABASE_URL,
    use_jsonb=True,
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash for a file at file_path. Returns hex digest."""
    print(f"Computing hash for file: {file_path}")
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception as e:
        # Re-raise to let callers decide; callers may choose to handle remote files differently
        raise
    return h.hexdigest()


def file_already_embedded(file_path: Optional[str] = None, file_hash: Optional[str] = None) -> bool:
    """Return True if any documents with the given file_hash already exist in the vector store.

    Accepts either a file_path or a precomputed file_hash. If both provided, file_hash is used.
    Uses a filter-based search on the vector_store to look up documents with matching metadata.
    Falls back to a filename-based check if file_hash checks fail (best-effort).
    """

    print("Checking if file is already embedded...")
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

    # If we received file metadata, check for duplicates before embedding
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

