#!/usr/bin/env python
# coding: utf-8

# # Kinetica Vectorstore based Retriever
# 
# >[Kinetica](https://www.kinetica.com/) is a database with integrated support for vector similarity search
# 
# It supports:
# - exact and approximate nearest neighbor search
# - L2 distance, inner product, and cosine distance
# 
# This notebook shows how to use a retriever based on Kinetica vector store (`Kinetica`).

# In[ ]:


# Please ensure that this connector is installed in your working environment.
get_ipython().run_line_magic('pip', 'install gpudb==7.2.0.9')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[2]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# In[ ]:


## Loading Environment Variables
from dotenv import load_dotenv

load_dotenv()


# In[5]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import (
    Kinetica,
    KineticaSettings,
)
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# In[6]:


# Kinetica needs the connection to the database.
# This is how to set it up.
HOST = os.getenv("KINETICA_HOST", "http://127.0.0.1:9191")
USERNAME = os.getenv("KINETICA_USERNAME", "")
PASSWORD = os.getenv("KINETICA_PASSWORD", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def create_config() -> KineticaSettings:
    return KineticaSettings(host=HOST, username=USERNAME, password=PASSWORD)


# ## Create Retriever from vector store

# In[ ]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

# The Kinetica Module will try to create a table with the name of the collection.
# So, make sure that the collection name is unique and the user has the permission to create a table.

COLLECTION_NAME = "state_of_the_union_test"
connection = create_config()

db = Kinetica.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    config=connection,
)

# create retriever from the vector store
retriever = db.as_retriever(search_kwargs={"k": 2})


# ## Search with retriever

# In[ ]:


result = retriever.get_relevant_documents(
    "What did the president say about Ketanji Brown Jackson"
)
print(docs[0].page_content)

