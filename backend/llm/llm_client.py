from langchain_ollama import ChatOllama

local_llm = ChatOllama(
    model="gemma4",
    temperature=0.5,
    streaming=True, 
)
