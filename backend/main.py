import langchain

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# load local model from LM Studio
local_llm = ChatOpenAI(
    base_url="http://127.0.0.1:1234/v1/chat",
    api_key="lm_studio",  # Dummy key 
    model="google/gemma-4-e4b",  # the model lm studio is serving
)

# Invoke the local model
while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "bye"]:
        break
    response = local_llm.invoke([
        HumanMessage(content=user_input)
    ])
    print(response.content)