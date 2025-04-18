#!/usr/bin/env python
# coding: utf-8

# # Pinecone
# 
# >[Pinecone](https://docs.pinecone.io/docs/overview) is a vector database with broad functionality.
# 
# This notebook shows how to use functionality related to the `Pinecone` vector database.
# 
# ## Setup
# 
# To use the `PineconeVectorStore` you first need to install the partner package, as well as the other packages used throughout this notebook.

# In[ ]:


pip install -qU langchain-pinecone pinecone-notebooks


# Migration note: if you are migrating from the `langchain_community.vectorstores` implementation of Pinecone, you may need to remove your `pinecone-client` v2 dependency before installing `langchain-pinecone`, which relies on `pinecone-client` v3.

# ### Credentials
# 
# Create a new Pinecone account, or sign into your existing one, and create an API key to use in this notebook.

# In[4]:


import getpass
import os

from pinecone import Pinecone, ServerlessSpec

if not os.getenv("PINECONE_API_KEY"):
    os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_api_key)


# If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[5]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ## Initialization
# 
# Before initializing our vector store, let's connect to a Pinecone index. If one named `index_name` doesn't exist, it will be created.

# In[12]:


import time

index_name = "langchain-test-index"  # change if desired

existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)


# Now that our Pinecone index is setup, we can initialize our vector store. 
# 
# import EmbeddingTabs from "@theme/EmbeddingTabs";
# 
# <EmbeddingTabs/>
# 

# In[13]:


# | output: false
# | echo: false
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


# In[14]:


from langchain_pinecone import PineconeVectorStore

vector_store = PineconeVectorStore(index=index, embedding=embeddings)


# ## Manage vector store
# 
# Once you have created your vector store, we can interact with it by adding and deleting different items.
# 
# ### Add items to vector store
# 
# We can add items to our vector store by using the `add_documents` function.

# In[15]:


from uuid import uuid4

from langchain_core.documents import Document

document_1 = Document(
    page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

document_3 = Document(
    page_content="Building an exciting new project with LangChain - come check it out!",
    metadata={"source": "tweet"},
)

document_4 = Document(
    page_content="Robbers broke into the city bank and stole $1 million in cash.",
    metadata={"source": "news"},
)

document_5 = Document(
    page_content="Wow! That was an amazing movie. I can't wait to see it again.",
    metadata={"source": "tweet"},
)

document_6 = Document(
    page_content="Is the new iPhone worth the price? Read this review to find out.",
    metadata={"source": "website"},
)

document_7 = Document(
    page_content="The top 10 soccer players in the world right now.",
    metadata={"source": "website"},
)

document_8 = Document(
    page_content="LangGraph is the best framework for building stateful, agentic applications!",
    metadata={"source": "tweet"},
)

document_9 = Document(
    page_content="The stock market is down 500 points today due to fears of a recession.",
    metadata={"source": "news"},
)

document_10 = Document(
    page_content="I have a bad feeling I am going to get deleted :(",
    metadata={"source": "tweet"},
)

documents = [
    document_1,
    document_2,
    document_3,
    document_4,
    document_5,
    document_6,
    document_7,
    document_8,
    document_9,
    document_10,
]
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store.add_documents(documents=documents, ids=uuids)


# ### Delete items from vector store

# In[16]:


vector_store.delete(ids=[uuids[-1]])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Query directly
# 
# Performing a simple similarity search can be done as follows:

# In[17]:


results = vector_store.similarity_search(
    "LangChain provides abstractions to make working with LLMs easy",
    k=2,
    filter={"source": "tweet"},
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")


# #### Similarity search with score
# 
# You can also search with score:

# In[18]:


results = vector_store.similarity_search_with_score(
    "Will it be hot tomorrow?", k=1, filter={"source": "news"}
)
for res, score in results:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")


# #### Other search methods
# 
# There are more search methods (such as MMR) not listed in this notebook, to find all of them be sure to read the [API reference](https://python.langchain.com/api_reference/pinecone/vectorstores/langchain_pinecone.vectorstores.PineconeVectorStore.html).
# 
# ### Query by turning into retriever
# 
# You can also transform the vector store into a retriever for easier usage in your chains.

# In[19]:


retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 1, "score_threshold": 0.5},
)
retriever.invoke("Stealing from the bank is a crime", filter={"source": "news"})


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/retrieval)

# ## API reference
# 
# For detailed documentation of all __ModuleName__VectorStore features and configurations head to the API reference: https://python.langchain.com/api_reference/pinecone/vectorstores/langchain_pinecone.vectorstores.PineconeVectorStore.html
