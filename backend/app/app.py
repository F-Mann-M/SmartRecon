# import gradio as gr
# from agent.chat_agent import AgentManager
# from agent.tools.tools import agent_tools
# from core.llm.llm_client import local_llm
# from parsers.invoice_parser import load_and_process_pdf


# chat_agent = AgentManager(model=local_llm, tools=agent_tools)

# # create knowledge base
# load_and_process_pdf()

# demo = gr.Interface(
#     fn=chat_agent.run_agent, 
#     inputs=gr.Textbox(label="User Input"),
#     outputs=gr.Textbox(label="Model Response"),
# )

# # Launch the interface
# demo.launch(server_name="127.0.0.1", server_port= 7860)