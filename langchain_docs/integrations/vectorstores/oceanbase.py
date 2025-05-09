#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Oceanbase
---
# # OceanbaseVectorStore
# 
# This notebook covers how to get started with the Oceanbase vector store.

# ## Setup
# 
# To access Oceanbase vector stores you'll need to deploy a standalone OceanBase server:
%docker run --name=ob433 -e MODE=mini -e OB_SERVER_IP=127.0.0.1 -p 2881:2881 -d quay.io/oceanbase/oceanbase-ce:4.3.3.1-101000012024102216
# And install the `langchain-oceanbase` integration package.
%pip install -qU "langchain-oceanbase"
# Check the connection to OceanBase and set the memory usage ratio for vector data:

# In[14]:


from pyobvector import ObVecClient

tmp_client = ObVecClient()
tmp_client.perform_raw_text_sql("ALTER SYSTEM ob_vector_memory_limit_percentage = 30")


# ## Initialization
# 
# Configure the API key of the embedded model. Here we use `DashScopeEmbeddings` as an example. When deploying `Oceanbase` with a Docker image as described above, simply follow the script below to set the `host`, `port`, `user`, `password`, and `database name`. For other deployment methods, set these parameters according to the actual situation.
%pip install dashscope
# In[15]:


import os

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_oceanbase.vectorstores import OceanbaseVectorStore

DASHSCOPE_API = os.environ.get("DASHSCOPE_API_KEY", "")
connection_args = {
    "host": "127.0.0.1",
    "port": "2881",
    "user": "root@test",
    "password": "",
    "db_name": "test",
}

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1", dashscope_api_key=DASHSCOPE_API
)

vector_store = OceanbaseVectorStore(
    embedding_function=embeddings,
    table_name="langchain_vector",
    connection_args=connection_args,
    vidx_metric_type="l2",
    drop_old=True,
)


# ## Manage vector store
# 
# ### Add items to vector store
# 
# - TODO: Edit and then run code cell to generate output

# In[16]:


from langchain_core.documents import Document

document_1 = Document(page_content="foo", metadata={"source": "https://foo.com"})
document_2 = Document(page_content="bar", metadata={"source": "https://bar.com"})
document_3 = Document(page_content="baz", metadata={"source": "https://baz.com"})

documents = [document_1, document_2, document_3]

vector_store.add_documents(documents=documents, ids=["1", "2", "3"])


# ### Update items in vector store

# In[17]:


updated_document = Document(
    page_content="qux", metadata={"source": "https://another-example.com"}
)

vector_store.add_documents(documents=[updated_document], ids=["1"])


# ### Delete items from vector store

# In[18]:


vector_store.delete(ids=["3"])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Query directly
# 
# Performing a simple similarity search can be done as follows:

# In[19]:


results = vector_store.similarity_search(
    query="thud", k=1, filter={"source": "https://another-example.com"}
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


# If you want to execute a similarity search and receive the corresponding scores you can run:

# In[20]:


results = vector_store.similarity_search_with_score(
    query="thud", k=1, filter={"source": "https://example.com"}
)
for doc, score in results:
    print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")


# ### Query by turning into retriever
# 
# You can also transform the vector store into a retriever for easier usage in your chains. 

# In[21]:


retriever = vector_store.as_retriever(search_kwargs={"k": 1})
retriever.invoke("thud")


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/#retrieval)

# ## API reference
# 
# For detailed documentation of all OceanbaseVectorStore features and configurations head to the API reference: https://python.langchain.com/docs/integrations/vectorstores/oceanbase
