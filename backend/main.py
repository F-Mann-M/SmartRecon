from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver



local_llm = ChatOllama(
    model="gemma4",
    temperature=0.5,
    streaming=True, 
)

# Agent Tools

@tool
def calculator(expression: str) -> str:
    """A simple calculator that can add, subtract, multiply, or divide two numbers.
    Input should be a mathematical expression like '2 + 2' or '15 / 3'."""
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"
    
# Tool List
tools = [ calculator]

# Agent
agent = create_agent(
    model=local_llm,
    tools=tools,
    checkpointer=InMemorySaver()
)

# Stream Events
config = {"configurable": {"thread_id": str(uuid7())}} # set a unique thread_id for the session


# Invoke Agent
def run_agent(user_input):
    try:
        stream = agent.stream_events(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            version="v3",
        )
    except Exception as e:
        print(f"Error invoking the model: {e}")
        return "Error invoking the model. Please try again."

    # Process the stream events and print them in real-time
    for kind, item in stream.interleave("messages", "tool_calls"): # interleave the messages and tool calls for real-time processing
        if kind == "messages":
            for token in item.text:
                print(token, end="", flush=True)

        elif kind == "tool_calls":
            print(f"\nTool Execution: {item.tool_name}({item.input})")
            for delta in item.output:
                print(delta, end="", flush=True)
            print(f"\nTool Result: {item.output}\n")
    
    final_state = stream.output  


def cli_chat_():
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = run_agent(user_input)
       

if __name__ == "__main__":
    cli_chat_()
