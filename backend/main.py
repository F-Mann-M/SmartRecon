from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


local_llm = ChatOllama(
    model="gemma4",
    temperature=0.5,
)

# Invoke the local model
def invoke_local_model(user_input):
   
    response = local_llm.invoke([
        HumanMessage(content=user_input)
    ])
    return response.content
