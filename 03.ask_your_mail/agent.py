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
from customllm import customllm
import langchain
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import base64
import email
from langchain.tools import format_tool_to_openai_function
import openai
import json


class Bot():
    def connect_gmail(self):
        '''
        Connects to Gmail API and returns a GmailSearch object
        '''

        # Removing token.json to force re-authentication
        # if os.path.exists("token.json"):
        #     os.remove("token.json")

        print("Connecting to Gmail API...")
        credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            client_secrets_file="credentials.json",
        )
        self.api_resource = build_resource_service(credentials=credentials)
        print("Connected to Gmail API!")

    def query_gmail(self, query) -> str:
        messages = self.api_resource.users().messages().list(userId="me", q=query,
                                                             maxResults=10).execute().get('messages', [])
        if len(messages) == 0:
            return 'No email found.'
        results = []

        # Remove duplicate threads from the results
        unique_threads = set()
        _placeholder = []
        for message in messages:
            if message['threadId'] in unique_threads:
                continue
            else:
                _placeholder.append(message)
            unique_threads.add(message['threadId'])
        messages = _placeholder

        for message in messages:
            message_id = message["id"]

            message_data = (
                self.api_resource.users()
                .messages()
                .get(userId="me", id=message_id, format="raw")
                .execute()
            )

            raw_message = base64.urlsafe_b64decode(message_data['raw'])

            email_msg = email.message_from_bytes(
                raw_message, policy=email.policy.default)

            # Extracting body from the email message
            body = email_msg.get_body(('plain'))
            if body:
                body = body.get_content()
            elif email_msg.get_body(('html')):
                body = email_msg.get_body(('html'))
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(str(body), "html.parser")
                    body = soup.get_text()
                except:
                    print('html parsing failed')
                    body = ''
            else:
                body = ''

            # Formatting the body
            if body == '':
                print('No body found. Using snippet instead.')
                body = message_data["snippet"]
            else:
                body = body[:body.find(">>>")]
                import re
                # body = re.sub(r"\r\n+", ' ', body)
                # body = re.sub(r" +", ' ', body)

            result_dict = {
                # "snippet": message_data["snippet"],
                "To": email_msg["To"],
                "From": email_msg["From"],
                "Date": email_msg["Date"],
                "Subject": email_msg["Subject"],
                "Body": body,
            }
            results.append(str(result_dict))

        return '\n------\n'.join(results)

    def _make_tool(self):
        class GmailSearchArgsSchema(BaseModel):
            # From https://support.google.com/mail/answer/7190?hl=en
            query: str = Field(
                ...,
                description="the search query string. Dont use any filters here, just the search query string.",
            )

        gmail_tool = Tool.from_function(
            func=self.query_gmail,
            name="query_gmail",
            description="Takes in a gmail query string, and returns a list of email threads, separated by '\n------\n' which match the queries.",
            args_schema=GmailSearchArgsSchema,
        )
        return gmail_tool

    def initialize_bot(self):
        template = textwrap.dedent(
            """
        Answer the question, on the basis of some relevant emails provided as context.
        Emails are seperated by '\n------\n' in the context.

        Context:
        {context}

        #####################

        Question: {question}

        #####################

        Answer:
        """)
        prompt = PromptTemplate(template=template, input_variables=[
                                "question", "context"])
        self.llm_chain = LLMChain(prompt=prompt, llm=ChatOpenAI(
            temperature=0), verbose=True)


    def convert_to_gmail_query(self, question):

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "Convert a Human input query into a meaningful gmail query"},
                {"role": "user", "content": question}
            ],
            functions=[
                {
                    "name": "search_gmail",
                    "description": "Takes in a gmail query string, and returns a list of relevant email threads.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "the search query string. Dont use any filters(like 'from:', 'to:', etc) here.",
                            },
                        },
                        "required": ["query"],
                    },
                }
            ],

            function_call={"name": "search_gmail"},  # auto is default, but we'll be explicit
        )
        print('Tokens used for query:', response['usage'])
        
        response = response['choices'][0]['message']['function_call']['arguments']
        response = json.loads(response)
        response = response['query']
        return response

    def ask(self, question, context):
        response = self.llm_chain.predict(
            question=question,
            context=context
        )
        return response
