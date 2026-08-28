
from core.llm.llm_client import chat_llm, structured_llm
from agent.tools.tools import agent_tools
from agent.chat_agent import AgentManager
from parsers.invoice_parser import load_and_process_pdf
from parsers.bank_parser import process_statement_folder


def cli_chat_():
    chat_agent = AgentManager(model=structured_llm, tools=agent_tools)
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = chat_agent.run_agent_stream(user_input)


if __name__ == "__main__":
    # check if the bot is running in terminal (debugging)
    cli_chat_()