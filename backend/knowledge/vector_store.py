import chromadb
from chromadb.utils import embedding_functions
import os


client = chromadb.Client()

ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="embeddinggemma"
    )


collection = client.create_collection(
    name="invoices",
    metadata={"description": "A collection for storing invoices"},
    configuration={
        "hnsw": {
            "space": "cosine",
            "ef_search": 100,
            "ef_construction": 100,
            "max_neighbors": 16
        },
        "embedding_function": ef
    }
)

def add_chunks_to_chroma(documents):
    
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

    collection.add(
        documents=docs_text,
        metadatas=metadata,
        ids=ids
    )

    print(f"\nChroma collection: {collection.name}")
    print(collection.get())

    ###Test similarity search
    results = collection.query(
        query_texts="wie ist die Rechnungsadresse?",
        n_results=1
    )

    print("\nSimilarity Search Results:")
    print(results)