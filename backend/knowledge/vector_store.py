import chromadb
from chromadb.utils import embedding_functions
import os


client = chromadb.Client()

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="embeddinggemma"
    )

def get_or_create_collection(
        collection_name: str = "invoice", 
        space: str = "cosine", 
        ef_search: int = 100,
        ef_construction: int = 100,
        max_neighbors: int = 16,
    ):
    """ Gets or creates a ChromaDB collection"""

    print(f"get or create collection: {collection_name}")

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ollama_ef,
        metadata={"description": "A collection for storing invoices"},
        configuration={
            "hnsw": {
                "space": space,
                "ef_search": ef_search,
                "ef_construction": ef_construction,
                "max_neighbors": 16,
            },
            
        }   
    )
    return collection


def add_chunks_to_collection(documents, collection_name: str = "invoice"):
    """
    Takes in LangChain Documents, 
    separates content and metadata form Documents,
    creates unique ID for each Chunk,
    embeds to collection
    """

    print("Add chunks to collection")
    collection = get_or_create_collection()
    
    docs_text = []
    metadata = []
    ids = []

    for id, doc in enumerate(documents):
        docs_text.append(doc.page_content)

        meta = dict(doc.metadata) if doc.metadata else {}
        metadata.append(meta)

        # add id
        source_path = meta.get("source", "doc")
        file_name = os.path.basename(source_path)
        ids.append(f"{file_name}_chunk_{id}")

    # populate collection
    collection.add(
        documents=docs_text,
        metadatas=metadata,
        ids=ids,
        )
        

def similarity_search(query: str, n_results: int = 3, where_filter: dict = None) -> list:
    """
    Takes in query and execute basic similarity search
    format output to downstream to llm
    """
    print("\nStart similarity search...")
    collection = get_or_create_collection()

    results = collection.query(
        query_texts=query,
        n_results=n_results,
        where=where_filter
    )

    if not results or not results["documents"] or not results["documents"][0]:
            return "No relevant documents found in the knowledge base."
    
    # Format the retrieved chunks into a clean string for the LLM
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_blocks = []
    for doc, meta in zip(documents, metadatas):
        source = meta.get("file_name", meta.get("source", "Unknown Source"))
        page = meta.get("page", 0)
        context_blocks.append(f"--- Source: {source} (Page {page}) ---\n{doc}")

    return "\n\n".join(context_blocks)

