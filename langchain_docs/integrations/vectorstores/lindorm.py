#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Lindorm
---
# # LindormVectorStore
# 
# This notebook covers how to get started with the Lindorm vector store.

# ## Setup
# 
# To access Lindorm vector stores you'll need to create a Lindorm account, get the ak/sk, and install the `langchain-lindorm-integration` integration package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU "langchain-lindorm-integration"')


# ### Credentials
# 
# Head to [here](https://help.aliyun.com/document_detail/2773369.html?spm=a2c4g.11186623.help-menu-172543.d_2_5_0.2a383f96gr5N3M&scm=20140722.H_2773369._.OR_help-T_cn~zh-V_1) to sign up to Lindorm and generate the ak/sk.

# In[1]:


import os


class Config:
    SEARCH_ENDPOINT = os.environ.get("SEARCH_ENDPOINT", "SEARCH_ENDPOINT")
    SEARCH_USERNAME = os.environ.get("SEARCH_USERNAME", "root")
    SEARCH_PWD = os.environ.get("SEARCH_PASSWORD", "<PASSWORD>")
    AI_LLM_ENDPOINT = os.environ.get("AI_ENDPOINT", "<AI_ENDPOINT>")
    AI_USERNAME = os.environ.get("AI_USERNAME", "root")
    AI_PWD = os.environ.get("AI_PASSWORD", "<PASSWORD>")
    AI_DEFAULT_EMBEDDING_MODEL = "bge_m3_model"  # set to your model


# ## Initialization
# 
# here we use the embedding model deployed on Lindorm AI Service.

# In[2]:


from langchain_lindorm_integration.embeddings import LindormAIEmbeddings
from langchain_lindorm_integration.vectorstores import LindormVectorStore

embeddings = LindormAIEmbeddings(
    endpoint=Config.AI_LLM_ENDPOINT,
    username=Config.AI_USERNAME,
    password=Config.AI_PWD,
    model_name=Config.AI_DEFAULT_EMBEDDING_MODEL,
)

index = "test_index"
vector = embeddings.embed_query("hello word")
dimension = len(vector)
vector_store = LindormVectorStore(
    lindorm_search_url=Config.SEARCH_ENDPOINT,
    embedding=embeddings,
    http_auth=(Config.SEARCH_USERNAME, Config.SEARCH_PWD),
    dimension=dimension,
    embeddings=embeddings,
    index_name=index,
)


# ## Manage vector store
# 
# ### Add items to vector store
# 

# In[3]:


from langchain_core.documents import Document

document_1 = Document(page_content="foo", metadata={"source": "https://example.com"})

document_2 = Document(page_content="bar", metadata={"source": "https://example.com"})

document_3 = Document(page_content="baz", metadata={"source": "https://example.com"})

documents = [document_1, document_2, document_3]

vector_store.add_documents(documents=documents, ids=["1", "2", "3"])


# ### Delete items from vector store
# 

# In[5]:


vector_store.delete(ids=["3"])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Query directly
# 
# Performing a simple similarity search can be done as follows:

# In[8]:


results = vector_store.similarity_search(query="thud", k=1)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


# If you want to execute a similarity search and receive the corresponding scores you can run:
# 

# In[9]:


results = vector_store.similarity_search_with_score(query="thud", k=1)
for doc, score in results:
    print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/#retrieval)

# ## API reference
# 
# For detailed documentation of all LindormVectorStore features and configurations head to [the API reference](https://pypi.org/project/langchain-lindorm-integration/).
