from core.llm.llm_client import local_embeddings
from core.config import settings
from langchain_postgres import PGVector
from typing import List
import os

vector_store = PGVector(
    embeddings=local_embeddings,
    collection_name="invoice",
    connection=settings.DATABASE_URL,
    use_jsonb=True,
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})


def add_chunks_to_collection(documents: List[Document])-> None:
    """
    Takes in a list of LangChain Documents, 
    generate embeddings,
    and insert them into the PGVector
    """

    if not documents:
        print("No documents provided")

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

