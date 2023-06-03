"""
Generates output based on user input using OpenAI's Davinci engine.
"""

import os
import openai
import streamlit as st
from openai import error

# To use .env file
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("API_KEY")

st.title("Ask me anything!")

text_input = st.text_input(
    '', key="prompt", placeholder="Enter your question here", label_visibility="collapsed")

# Checks if input is empty
if text_input != '':
    with st.spinner("Thinking..."):
        try:
            response = openai.Completion.create(
                engine="text-davinci-001",
                prompt=f"Q: {text_input}\nA:",
                temperature=0.9,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            st.write(response.choices[0].text)
            with st.expander("Full Response"):
                st.write(response)
        except error.OpenAIError as e:
            st.write("An issue with OpenAI has occured:", e)
