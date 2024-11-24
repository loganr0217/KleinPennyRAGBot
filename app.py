# Importing flask for setting up basic server
from flask import Flask, request
from flask_cors import CORS

# Importing requests, BeautifulSoup for scraping property site
import requests
from bs4 import BeautifulSoup
import bs4
import getpass
import os

# Importing necessary langchain modules
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importing langsmith Client for communication
from langsmith import Client

# Getting keys from secrets file
from mySecrets import Secrets

# Setting up pinecone index
from pinecone import Pinecone, ServerlessSpec

# Setting up OpenAPI key, PineCone API, LangChain API
os.environ["OPENAI_API_KEY"] = Secrets.OPENAI_API_KEY
os.environ['PINECONE_API_KEY'] = Secrets.PINECONE_API_KEY
os.environ["LANGCHAIN_API_KEY"] = Secrets.LANGCHAIN_API_KEY

# Initializing client and flask app
client = Client()
app = Flask(__name__)
CORS(app)


# Choosing llm model --> using 4o-mini 
llm = ChatOpenAI(model="gpt-4o-mini")

# Connecting to pinecone and using vectorstore as retriever
pinecone_index = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index_name = "klein-penny-index"
vectorstore = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the sites
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 5, "lambda_mult": 0.5},
)

# Creates new question using previous ones
system_prompt_with_history = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
prompt_with_history = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_with_history),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)
# Retriever with history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, prompt_with_history
)

# Using custom prompt to get property info
system_prompt = (
    "You are given a list of documents (each associated with a property) and their associated descriptions, titles, and other information as context. "
    "Use the following pieces of retrieved context to give properties that match the user's question."
    "If you don't know the answer, say that you "
    "don't know. If you use any information from the context, list its metadata in your answer." 
    ""
    "\n\n"
    "Context: {context}"
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

# Creating chain so we can grab source from context
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

chat_history = []

# Endpoint to ask question to chatbot
@app.route("/ask")
def askQuestion():
    question = request.args.get('question', default='null', type=str)

    response = rag_chain.invoke({"input": question, "chat_history": chat_history})

    # Formatting answer so it can be returned
    fullAnswer = response["answer"] + "\n\nYou can check out more related properties here: \n"
    for found in response["context"]:
        fullAnswer += found.metadata["title"] + ": " + found.metadata["source"] + "\n"

    return fullAnswer

# Endpoint to ask question to chatbot and get answer, context, titles
@app.route("/askFull")
def askQuestionFullResponse():
    question = request.args.get('question', default='null', type=str)

    # Using rag_chain to get answer and context
    response = rag_chain.invoke({"input": question, "chat_history": chat_history})

    currentContext = [str(i) for i in response["context"]]
    currentTitles = [i.metadata["title"] for i in response["context"]]

    # Formatting answer so it can be returned
    fullAnswer = response["answer"] + "\n\nYou can check out more related properties here: \n"
    for found in response["context"]:
        fullAnswer += found.metadata["title"] + ": " + found.metadata["source"] + "\n"

    return [fullAnswer, currentContext, currentTitles]




if __name__ == "__main__":
    app.run(port=8000, debug=True)