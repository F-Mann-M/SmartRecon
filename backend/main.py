from llm.llm_client import local_llm
from agents.tools import tools
from agents.chat_agent import AgentManager
from knowledge.document_loader import load_and_process_pdf

chat_agent = AgentManager(model=local_llm, tools=tools)

# create ChromaDB
load_and_process_pdf()

# check llm connection
print("check llm connection...")
response = local_llm.invoke("test")
if response or response["content"]:
    print(type(response))
    print(response["content"])


def cli_chat_():
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break
        response = chat_agent.run_agent_stream(user_input)


if __name__ == "__main__":
    cli_chat_()


"""
content='I am here and ready to assist! What can I help you with today?' 
additional_kwargs={} 
response_metadata={
    'model': 'gemma4', 
    'created_at': '2026-07-23T14:42:27.477655Z', 
    'done': True, 'done_reason': 'stop', 
    'total_duration': 80818029334, 
    'load_duration': 69560290375, 
    'prompt_eval_count': 17, 
    'prompt_eval_duration': 385450000, 
    'eval_count': 216, 'eval_duration': 10595738000, 
    'logprobs': None, 'model_name': 'gemma4', 
    'model_provider': 'ollama'} 
id='lc_run--019f8f6c-4a5f-7bc0-8003-2129e25ef5a9-0' 
tool_calls=[] 
invalid_tool_calls=[] 
usage_metadata={
    'input_tokens': 17, 
    'output_tokens': 216, 
    'total_tokens': 233}
"""