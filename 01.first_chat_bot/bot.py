"""
Generates output based on user input using OpenAI's Davinci engine.
"""

import openai
import streamlit as st
from openai import error

st.title("Ask me anything!")

# Asking for API key.
api_key = st.text_input('api_key', key='api_key', placeholder='Enter your OpenAI key',
                        type='password', label_visibility="collapsed")

if api_key:
    # Sets api key as environment variable.
    openai.api_key = api_key
    st.success('API key set successfully! Now you can ask questions', icon='🔑')
    print(api_key)

text_input = st.text_input(
    'prompt', key="prompt", placeholder="Enter your question here", label_visibility="collapsed")

# Checks if input is empty
if text_input:
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
