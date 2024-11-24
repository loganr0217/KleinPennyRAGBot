import requests
from bs4 import BeautifulSoup
import bs4
import os

# Importing necessary langchain modules
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Importing langsmith Client for communication
from langsmith import Client

# Getting keys from secrets file
from mySecrets import Secrets

# Setting up OpenAPI key, PineCone API, LangChain API
os.environ["OPENAI_API_KEY"] = Secrets.OPENAI_API_KEY
os.environ['PINECONE_API_KEY'] = Secrets.PINECONE_API_KEY
os.environ["LANGCHAIN_API_KEY"] = Secrets.LANGCHAIN_API_KEY

# Setting up pinecone index
from pinecone import Pinecone, ServerlessSpec
pinecone_index = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index_name = "klein-penny-index"

# Initializing client
client = Client()

# Gets full list of property links from KleinPenny
def getKleinPennyData():
    # Getting main listing page
    url = "https://kleinpennyrentals.com/list"
    propertyListingPage = requests.get(url)
    propertyListingSoup = BeautifulSoup(propertyListingPage.content, "html.parser")

    propertyLinks = [] # Array to hold links to property pages

    # Getting all properties in the main listing page
    properties = propertyListingSoup.find_all("td", {"class": "views-field-title"})

    baseURL = "https://kleinpennyrentals.com"
    # Looping through to get each property link
    for property in properties:
        link = property.find_all("a")[0]["href"]
        propertyLinks.append(baseURL + link)

    return propertyLinks

# Load the property data into index in PINECONE --> returns vectorstore
def loadAndChunkPropertyData(propertyLinks):
    # Load, chunk and index the contents of the property sites
    loader = WebBaseLoader(web_paths=propertyLinks)
    vectorStore = -1

    # Creates new pinecone index to put vectors into
    pinecone_index.create_index(
        name=index_name,
        dimension=1536, # Replace with your model dimensions
        metric="cosine", # Replace with your model metric
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )

    # Loading documents from the sites
    docs = loader.load()
    
    # Splitting the text and creating the vector store with PineCone
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = PineconeVectorStore.from_documents(
        splits,
        index_name=index_name,
        embedding=OpenAIEmbeddings()
    )

    return vectorstore


allIndexes = [i["name"] for i in pinecone_index.list_indexes()]
# Searching to see if user has index for klein-penny setup and setting it up if not
if index_name not in allIndexes:
    # Runs and initializes the index
    propertyLinks = getKleinPennyData()
    res = loadAndChunkPropertyData(propertyLinks)
    if res != -1:
        print("\n\nSuccessfully setup index with data\n\n")
    else:
        print("\n\nError setting up index\n\n")
else:
    print("\n\nAn index already exists --> you can move on to server setup\n\n")

