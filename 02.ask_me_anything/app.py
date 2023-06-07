"""
Streamlit main app file.
"""

import os
import streamlit as st
from src.process_data import process_data
from src.bot import Bot
import streamlit_scrollable_textbox as stx


def setup():
    """
    Setup function.
    """
    # Asking for API key.
    api_key = st.text_input('OpenAI api key:', key='api_key', type='password')

    if api_key:
        # Sets api key as environment variable.
        os.environ['OPENAI_API_KEY'] = api_key
        print(api_key)

    # Asking for relevant data.
    relevant_data = st.text_input('Enter relevant data:', key='relevant_data')
    if relevant_data:
        stx.scrollableTextbox(relevant_data.split('\n'), height = 150)
        with st.spinner("Processing data..."):
            vector_store = process_data(relevant_data)
            agent = Bot(vector_store)  # Feeding data to bot.
        if st.button('Ask a question'):
            st.session_state['agent'] = agent
            st.experimental_rerun()



def main():
    """
    Main function.
    """
    st.title("Ask me anything!")

    if st.session_state.get('agent') is None:
        setup()
    else:
        # Asking for question.
        question = st.text_input('Enter your question:', key='question')

        if question:
            with st.spinner("Thinking..."):
                response = st.session_state.agent.ask(question)

                # Printing relevant documents.
                st.write(response)

                if st.button('Restart app'):
                    del st.session_state['agent']
                    st.experimental_rerun()

if __name__ == '__main__':
    main()
