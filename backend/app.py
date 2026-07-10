import gradio as gr
from main import run_agent


# Define the interface
demo = gr.Interface(
    fn=run_agent, # Function to invoke the local model
    inputs=gr.Textbox(label="User Input"), # Input textbox for user input
    outputs=gr.Textbox(label="Model Response"), # Output textbox for model response
)

# Launch the interface
demo.launch(server_name="127.0.0.1", server_port= 7860)