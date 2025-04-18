#!/usr/bin/env python
# coding: utf-8

# # MariaDB
# 
# LangChain's MariaDB integration (langchain-mariadb) provides vector capabilities for working with MariaDB version 11.7.1 and above, distributed under the MIT license. Users can use the provided implementations as-is or customize them for specific needs.
#  Key features include:
# 
#  * Built-in vector similarity search
#  * Support for cosine and euclidean distance metrics
#  * Robust metadata filtering options
#  * Performance optimization through connection pooling
#  * Configurable table and column settings
# 
# ## Setup
# 
# Launch a MariaDB Docker container with:

# In[ ]:


get_ipython().system('docker run --name mariadb-container -e MARIADB_ROOT_PASSWORD=langchain -e MARIADB_DATABASE=langchain -p 3306:3306 -d mariadb:11.7')


# ### Installing the Package
# 
# The package uses SQLAlchemy but works best with the MariaDB connector, which requires C/C++ components:
# 

# In[ ]:


# Debian, Ubuntu
get_ipython().system('sudo apt install libmariadb3 libmariadb-dev')

# CentOS, RHEL, Rocky Linux
get_ipython().system('sudo yum install MariaDB-shared MariaDB-devel')

# Install Python connector
get_ipython().system('pip install -U mariadb')


# Then install `langchain-mariadb` package
# 

# In[ ]:


pip install -U langchain-mariadb


# VectorStore works along with an LLM model, here using `langchain-openai` as example.
# 

# In[ ]:


pip install langchain-openai
export OPENAI_API_KEY=...


# ## Initialization

# In[1]:


from langchain_core.documents import Document
from langchain_mariadb import MariaDBStore
from langchain_openai import OpenAIEmbeddings

# connection string
url = f"mariadb+mariadbconnector://myuser:mypassword@localhost/langchain"

# Initialize vector store
vectorstore = MariaDBStore(
    embeddings=OpenAIEmbeddings(),
    embedding_length=1536,
    datasource=url,
    collection_name="my_docs",
)


# ## Manage vector store
# 
# ### Adding Data
# You can add data as documents with metadata:
# 

# In[1]:


docs = [
    Document(
        page_content="there are cats in the pond",
        metadata={"id": 1, "location": "pond", "topic": "animals"},
    ),
    Document(
        page_content="ducks are also found in the pond",
        metadata={"id": 2, "location": "pond", "topic": "animals"},
    ),
    # More documents...
]
vectorstore.add_documents(docs)


# 
# Or as plain text with optional metadata:

# In[14]:


texts = [
    "a sculpture exhibit is also at the museum",
    "a new coffee shop opened on Main Street",
]
metadatas = [
    {"id": 6, "location": "museum", "topic": "art"},
    {"id": 7, "location": "Main Street", "topic": "food"},
]

vectorstore.add_texts(texts=texts, metadatas=metadatas)


# ## Query vector store

# In[15]:


# Basic similarity search
results = vectorstore.similarity_search("Hello", k=2)

# Search with metadata filtering
results = vectorstore.similarity_search("Hello", filter={"category": "greeting"})


# 
# ### Filter Options
# 
# The system supports various filtering operations on metadata:
# 
# * Equality: $eq
# * Inequality: $ne
# * Comparisons: $lt, $lte, $gt, $gte
# * List operations: $in, $nin
# * Text matching: $like, $nlike
# * Logical operations: $and, $or, $not
# 
# Example:
# 

# In[15]:


# Search with simple filter
results = vectorstore.similarity_search(
    "kitty", k=10, filter={"id": {"$in": [1, 5, 2, 9]}}
)

# Search with multiple conditions (AND)
results = vectorstore.similarity_search(
    "ducks",
    k=10,
    filter={"id": {"$in": [1, 5, 2, 9]}, "location": {"$in": ["pond", "market"]}},
)


# ## Usage for retrieval-augmented generation
# 
# TODO: document example

# ## API reference
# 
# See the repo [here](https://github.com/mariadb-corporation/langchain-mariadb) for more detail.
