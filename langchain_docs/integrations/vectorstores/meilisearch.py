#!/usr/bin/env python
# coding: utf-8

# # Meilisearch
# 
# > [Meilisearch](https://meilisearch.com) is an open-source, lightning-fast, and hyper relevant search engine. It comes with great defaults to help developers build snappy search experiences. 
# >
# > You can [self-host Meilisearch](https://www.meilisearch.com/docs/learn/getting_started/installation#local-installation) or run on [Meilisearch Cloud](https://www.meilisearch.com/pricing).
# 
# Meilisearch v1.3 supports vector search. This page guides you through integrating Meilisearch as a vector store and using it to perform vector search.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration

# ## Setup
# 
# ### Launching a Meilisearch instance
# 
# You will need a running Meilisearch instance to use as your vector store. You can run [Meilisearch in local](https://www.meilisearch.com/docs/learn/getting_started/installation#local-installation) or create a [Meilisearch Cloud](https://cloud.meilisearch.com/) account.
# 
# As of Meilisearch v1.3, vector storage is an experimental feature. After launching your Meilisearch instance, you need to **enable vector storage**. For self-hosted Meilisearch, read the docs on [enabling experimental features](https://www.meilisearch.com/docs/learn/experimental/overview). On **Meilisearch Cloud**, enable _Vector Store_ via your project _Settings_ page.
# 
# You should now have a running Meilisearch instance with vector storage enabled. 🎉
# 
# ### Credentials
# 
# To interact with your Meilisearch instance, the Meilisearch SDK needs a host (URL of your instance) and an API key.
# 
# **Host**
# 
# - In **local**, the default host is `localhost:7700`
# - On **Meilisearch Cloud**, find the host in your project _Settings_ page
# 
# **API keys**
# 
# Meilisearch instance provides you with three API keys out of the box: 
# - A `MASTER KEY` — it should only be used to create your Meilisearch instance
# - A `ADMIN KEY` — use it only server-side to update your database and its settings
# - A `SEARCH KEY` — a key that you can safely share in front-end applications
# 
# You can create [additional API keys](https://www.meilisearch.com/docs/learn/security/master_api_keys) as needed.

# ### Installing dependencies
# 
# This guide uses the [Meilisearch Python SDK](https://github.com/meilisearch/meilisearch-python). You can install it by running:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  meilisearch')


# For more information, refer to the [Meilisearch Python SDK documentation](https://meilisearch.github.io/meilisearch-python/).

# ## Examples
# 
# There are multiple ways to initialize the Meilisearch vector store: providing a Meilisearch client or the _URL_ and _API key_ as needed. In our examples, the credentials will be loaded from the environment.
# 
# You can make environment variables available in your Notebook environment by using `os` and `getpass`. You can use this technique for all the following examples.

# In[ ]:


import getpass
import os

if "MEILI_HTTP_ADDR" not in os.environ:
    os.environ["MEILI_HTTP_ADDR"] = getpass.getpass(
        "Meilisearch HTTP address and port:"
    )
if "MEILI_MASTER_KEY" not in os.environ:
    os.environ["MEILI_MASTER_KEY"] = getpass.getpass("Meilisearch API Key:")


# We want to use OpenAIEmbeddings so we have to get the OpenAI API Key.

# In[ ]:


if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# ### Adding text and embeddings
# 
# This example adds text to the Meilisearch vector database without having to initialize a Meilisearch vector store.

# In[ ]:


from langchain_community.vectorstores import Meilisearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

embeddings = OpenAIEmbeddings()
embedders = {
    "default": {
        "source": "userProvided",
        "dimensions": 1536,
    }
}
embedder_name = "default"


# In[ ]:


with open("../../how_to/state_of_the_union.txt") as f:
    state_of_the_union = f.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(state_of_the_union)


# In[ ]:


# Use Meilisearch vector store to store texts & associated embeddings as vector
vector_store = Meilisearch.from_texts(
    texts=texts, embedding=embeddings, embedders=embedders, embedder_name=embedder_name
)


# Behind the scenes, Meilisearch will convert the text to multiple vectors. This will bring us to the same result as the following example.

# ### Adding documents and embeddings
# 
# In this example, we'll use Langchain TextSplitter to split the text in multiple documents. Then, we'll store these documents along with their embeddings.

# In[ ]:


from langchain_community.document_loaders import TextLoader

# Load text
loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# Create documents
docs = text_splitter.split_documents(documents)

# Import documents & embeddings in the vector store
vector_store = Meilisearch.from_documents(
    documents=documents,
    embedding=embeddings,
    embedders=embedders,
    embedder_name=embedder_name,
)

# Search in our vector store
query = "What did the president say about Ketanji Brown Jackson"
docs = vector_store.similarity_search(query, embedder_name=embedder_name)
print(docs[0].page_content)


# ## Add documents by creating a Meilisearch Vectorstore

# In this approach, we create a vector store object and add documents to it.

# In[ ]:


import meilisearch
from langchain_community.vectorstores import Meilisearch

client = meilisearch.Client(url="http://127.0.0.1:7700", api_key="***")
vector_store = Meilisearch(
    embedding=embeddings,
    embedders=embedders,
    client=client,
    index_name="langchain_demo",
    text_key="text",
)
vector_store.add_documents(documents)


# ## Similarity Search with score
# 
# This specific method allows you to return the documents and the distance score of the query to them. `embedder_name` is the name of the embedder that should be used for semantic search, defaults to "default".

# In[ ]:


docs_and_scores = vector_store.similarity_search_with_score(
    query, embedder_name=embedder_name
)
docs_and_scores[0]


# ## Similarity Search by vector
# `embedder_name` is the name of the embedder that should be used for semantic search, defaults to "default".

# In[ ]:


embedding_vector = embeddings.embed_query(query)
docs_and_scores = vector_store.similarity_search_by_vector(
    embedding_vector, embedder_name=embedder_name
)
docs_and_scores[0]


# ## Additional resources
# 
# Documentation
# - [Meilisearch](https://www.meilisearch.com/docs/)
# - [Meilisearch Python SDK](https://python-sdk.meilisearch.com)
# 
# Open-source repositories
# - [Meilisearch repository](https://github.com/meilisearch/meilisearch)
# - [Meilisearch Python SDK](https://github.com/meilisearch/meilisearch-python)
