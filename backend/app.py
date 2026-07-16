import gradio as gr
from agents.chat_agent import AgentManager
from agents.tools import tools
from llm.llm_client import local_llm
# from main import load_pdf

chat_agent = AgentManager(model=local_llm, tools=tools)


# # Define the interface
# with gr.Blocks() as demo:
#     gr.Markdown("## SmartRecon Chat Interface")

#     with gr.Row():
#         with gr.Column():
#             file_input = gr.File(label="Upload PDF", file_types=[".pdf"])
#             load_button = gr.Button("Load PDF")
        
#         with gr.Column():
#             pdf_content = gr.Textbox(label="PDF Content", placeholder="Loaded PDF content will appear here...", interactive=False)
    
#     with gr.Row():
#         with gr.Column():
#             user_input = gr.Textbox(label="User Input", placeholder="Type your message here...")
#             send_button = gr.Button("Send")
        
#         with gr.Column():
#             model_response = gr.Textbox(label="Model Response", placeholder="Model's response will appear here...", interactive=False)
    
#     send_button.click(
#         fn=chat_agent.run_agent,
#         inputs=user_input,
#         outputs=model_response
#     )


demo = gr.Interface(
    fn=chat_agent.run_agent, 
    inputs=gr.Textbox(label="User Input"),
    outputs=gr.Textbox(label="Model Response"),
)

# Launch the interface
demo.launch(server_name="127.0.0.1", server_port= 7860)