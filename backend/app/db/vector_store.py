from functools import lru_cache

from langchain_postgres import PGVector

from core.config import settings
from core.llm.llm_client import embedding_model


@lru_cache(maxsize=1) # get_invoice_vector_store is cached to avoid re-initializing the PGVector store multiple times
def get_invoice_vector_store() -> PGVector:
    """Build and cache the invoice PGVector store instance."""
    return PGVector(
        embeddings=embedding_model,
        collection_name="invoice",
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )
