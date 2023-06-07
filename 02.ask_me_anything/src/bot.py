"""
The main bot file.
"""

import textwrap
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.callbacks import get_openai_callback
from openai.error import AuthenticationError

class Bot:
    """
    The bot class.
    """
    def __init__(self, vectorstore):
        self.llm = OpenAI(temperature=0, max_tokens=100, verbose=True)
        self.chain = None
        self._feed_data(vectorstore)

    def _feed_data(self, vectorstore):
        """
        Creating a RetrievalQA chain with the vectorstore.
        """

        # Using the LLMChain to make your own prompt.
        prompt = PromptTemplate(template=textwrap.dedent("""
        Provided some context and a question, answer the question based on the context.
        Do not hallucinate. If you dont know, say so.
        #####

        Context:
        {context}

        Question:
        {question}"""), input_variables=['context', 'question'])

        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type='stuff', retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"verbose": True, "prompt": prompt})

    def ask(self, question):
        """
        Asking the bot a question.
        """
        with get_openai_callback() as callback:
            try:
                response = self.chain.run(question)
            except AuthenticationError:
                response = "Invalid API key."
            print(callback)

        return response
