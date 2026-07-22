from llm.llm_client import local_llm
from agents.tools import tools
from agents.chat_agent import AgentManager
from knowledge.document_loader import load_and_process_pdf

chat_agent = AgentManager(model=local_llm, tools=tools)

# create ChromaDB
load_and_process_pdf()

def cli_chat_():
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = chat_agent.run_agent_stream(user_input)


if __name__ == "__main__":
    cli_chat_()
