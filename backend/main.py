from llm.llm_client import local_llm
from agents.tools import tools
from agents.chat_agent import AgentManager
from knowledge.document_loader import load_and_process_pdf
from knowledge.retriver import answer_question_with_rag

chat_agent = AgentManager(model=local_llm, tools=tools)

# create ChromaDB
load_and_process_pdf()

# test similarity search
print("\n\nTest Similarity search")
answer = answer_question_with_rag("wie lauted die Rechnungsadresse?")
print(answer)

def cli_chat_():
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = chat_agent.run_agent_stream(user_input)


if __name__ == "__main__":
    cli_chat_()
