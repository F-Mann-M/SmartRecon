import gradio as gr
from agents.chat_agent import AgentManager
from agents.tools import tools
from llm.llm_client import local_llm

chat_agent = AgentManager(model=local_llm, tools=tools)

# Define the interface
demo = gr.Interface(
    fn=chat_agent.run_agent, 
    inputs=gr.Textbox(label="User Input"),
    outputs=gr.Textbox(label="Model Response"),
)

# Launch the interface
demo.launch(server_name="127.0.0.1", server_port= 7860)