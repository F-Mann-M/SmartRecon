from fastapi import APIRouter

from core.llm.llm_client import local_llm
from agent.tools.tools import agent_tools
from agent.chat_agent import AgentManager



chat_router = APIRouter()

@chat_router.post("/chat")
def chat_with_agent(user_input: str = None):
    """
    Endpoint to interact with the agent for chat-based queries.
    """
    chat_agent = AgentManager(model=local_llm, tools=agent_tools)
    response = chat_agent.run_agent(user_input)
    return {"response": response}