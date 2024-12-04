# Importing gradio for UI and requests for collecting responses from server
import gradio as gr
import requests


# Function to send user message to endpoint and collect output from chatbot
def chatbotMessage(message, history):
    response = requests.get("http://127.0.0.1:8000/ask?question=" + message)
    return response.text

# CSS and gradio UI for interacting with Chatbot
css = """
#col { height: calc(100vh - 112px - 16px) !important; }
"""
with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col"):
        chat = gr.ChatInterface(
            fn=chatbotMessage,
            type="messages",
            title="KleinPenny Property Expert",
            description="Describe the type of property that you would want (number of beds, number of baths, nearby restaurants)",
            theme="ocean"
        )

demo.queue()
demo.launch()