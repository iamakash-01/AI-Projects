import os
from dotenv import load_dotenv
from typing import Generator
import streamlit as st
from groq import Groq
import re

# load the api key
load_dotenv()
client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
    )

# web app design
st.set_page_config("Ultron Bot", page_icon="🤖", layout="wide")
st.subheader("A Bot from the Future", divider="rainbow")

# initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
        # Add a default message if none exist
        st.session_state.messages.append({"role": "system", "content": "You are a helpful assistant."})

if len(st.session_state.messages) == 1:  # Only system message exists
        st.session_state.messages.append({"role": "user", "content": "Hello! How can I get help?"})

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# define the model
model = "llama-3.3-70b-versatile"

# display the chat history
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# response generation
def generate_chat_response(chat_completion) -> Generator[str, None, None]: 
    for chunk in chat_completion :
        if chunk.choices[0].delta.content: 
            yield chunk.choices[0].delta.content

# user questions
if prompt := st.chat_input("Ask me anything : "): 
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar = "👤"):
        st.markdown(prompt)

# fetch the Groq API
try :
    chat_completion = client.chat.completions.create(
        model = model,
        messages = [
            {
                "role": m["role"] if m["role"] != "bot" else "assistant", 
                "content": m["content"]
            }
            for m in st.session_state.messages
        ],
        stream = True
    ) 

    # generate the response
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_responses = ""
        for chunk in generate_chat_response(chat_completion) :
            full_responses += chunk
            response_placeholder.markdown(full_responses)

    # append the full response
    st.session_state.messages.append(
            {"role": "assistant", "content": full_responses}
        )

# exception case
except Exception as e:
    st.error(f"An error occurred: {e}", icon="😢")
    full_responses = []