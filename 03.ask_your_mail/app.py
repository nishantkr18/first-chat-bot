from langchain.tools import Tool
from pydantic import BaseModel, Field
from langchain import PromptTemplate, LLMChain
from langchain.agents.agent_toolkits import GmailToolkit
from langchain.tools.gmail.utils import build_resource_service, get_gmail_credentials
import streamlit as st
import textwrap
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from typing import List
from langchain.tools.gmail import GmailSearch
import os
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import get_openai_callback
import langchain
from agent import Bot
import base64
import email
import streamlit_scrollable_textbox as stx

import openai


def main():
    load_dotenv()
    langchain.debug = True

    st.title("Ask questions to your emails!")

    if st.session_state.get('process_stage') is None:
        api_key = st.text_input('OpenAI api key:', key='api_key', type='password')
        if st.button('Set api key'):
            # Sets api key as environment variable.
            os.environ['OPENAI_API_KEY'] = api_key
            openai.api_key = api_key

        if st.button('Connect to Gmail!'):
            st.session_state['process_stage'] = 'lets_start'
            st.experimental_rerun()

    elif st.session_state.get('process_stage') == 'lets_start':
        with st.spinner():
            bot = Bot()
            try:
                bot.connect_gmail()
                bot.initialize_bot()
                st.session_state['process_stage'] = 'connected_to_gmail'
                st.session_state['bot'] = bot
                st.success('Authorized!')
            except Exception as e:
                st.write(f'Could not connect to Gmail API: {e}')

    if st.session_state.get('process_stage') == 'connected_to_gmail':
        question = st.text_input('Ask a question to your emails',
                                 value="When were Jonathan Sanabria's miners plugged in?")
        if st.button('Ask!'):
            with st.spinner():
                with get_openai_callback() as cb:
                    query = st.session_state['bot'].convert_to_gmail_query(question)
                    with st.expander('Query used to fetch emails'):
                        st.write(query)
                    relevant_data = st.session_state['bot'].query_gmail(query)
                    with st.expander('Reference emails'):
                        stx.scrollableTextbox(relevant_data, height=300)
                    response = st.session_state['bot'].ask(question, relevant_data)
                    print(cb)
                st.write(response)
                st.balloons()


if __name__ == "__main__":
    main()
#    bot = Bot()
#    bot.connect_gmail()
#    bot.initialize_bot()
#    bot.convert_to_gmail_query('When were Jonathan Sanabria\'s miners plugged in?')
