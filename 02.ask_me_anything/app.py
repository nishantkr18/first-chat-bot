"""
Streamlit main app file.
"""

import os
import streamlit as st
from src.process_data import process_data
from src.bot import Bot
import streamlit_scrollable_textbox as stx

st.title("Ask me anything!")

# Asking for API key.
api_key = st.text_input('OpenAI api key:', key='api_key', type='password')

if api_key != '':
    # Sets api key as environment variable.
    os.environ['OPENAI_API_KEY'] = api_key
    print(api_key)
    agent = Bot()

# Relevant data.
relevant_data = st.text_input('Enter relevant data:', key='relevant_data')

if relevant_data != '':
    stx.scrollableTextbox(relevant_data.split('\n'), height = 150)

    with st.spinner("Processing data..."):
        vector_store = process_data(relevant_data)
        agent.feed_data(vector_store)  # Feeding data to bot.

        # Asking for question.
        question = st.text_input('Enter your question:', key='question')

        if question != '':
            # Getting relevant documents.
            response = agent.ask(question)

            # Printing relevant documents.
            st.write(response)
