from langchain_ollama import ChatOllama, OllamaEmbeddings


local_llm = ChatOllama(
    model="gemma4",
    temperature=0.5,
    streaming=True,
    # num_predict=500
)


local_embeddings = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="embeddinggemma"
)