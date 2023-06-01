import openai
import streamlit as st
import os

# To use .env file
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("API_KEY")

st.title("Ask me anything!")

input = st.text_input("Enter your question here", key="prompt")

# Checks if input is empty
if st.session_state.prompt:
    with st.spinner("Thinking..."):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Q: {st.session_state.prompt}\nA:",
                temperature=0.9,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=["\n"],
            )
            st.write(response.choices[0].text)
            with st.expander("Full Response"):
                st.write(response)
        except Exception as e:
            st.write("error: ", e)
