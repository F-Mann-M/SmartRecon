
from core.llm.llm_client import local_llm
from agent.tools.tools import agent_tools
from agent.chat_agent import AgentManager
from parsers.invoice_parser import load_and_process_pdf
from db.session import Base, engine
from parsers.bank_parser import process_statement_folder

chat_agent = AgentManager(model=local_llm, tools=agent_tools)


# create Tables
Base.metadata.create_all(engine)

# loads pdf and stores in PGVector store
load_and_process_pdf()

# loads bank statements from a directory, parses them, and stores in PostgreSQL
process_statement_folder()

# # check llm connection
# print("check llm connection...")
# response = local_llm.invoke("test LLM connection")
# if response or response.content:
#     print(type(response))
#     print(response.content)
    

def cli_chat_():
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = chat_agent.run_agent_stream(user_input)


if __name__ == "__main__":
    cli_chat_()
