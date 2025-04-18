#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Databricks
---
# # DatabricksVectorSearch
# 
# [Databricks Vector Search](https://docs.databricks.com/en/generative-ai/vector-search.html) is a serverless similarity search engine that allows you to store a vector representation of your data, including metadata, in a vector database. With Vector Search, you can create auto-updating vector search indexes from Delta tables managed by Unity Catalog and query them with a simple API to return the most similar vectors.
# 
# This notebook shows how to use LangChain with Databricks Vector Search.

# ## Setup
# 
# To access Databricks models you'll need to create a Databricks account, set up credentials (only if you are outside Databricks workspace), and install required packages.
# 
# ### Credentials (only if you are outside Databricks)
# 
# If you are running LangChain app inside Databricks, you can skip this step.
# 
# Otherwise, you need manually set the Databricks workspace hostname and personal access token to `DATABRICKS_HOST` and `DATABRICKS_TOKEN` environment variables, respectively. See [Authentication Documentation](https://docs.databricks.com/en/dev-tools/auth/index.html#databricks-personal-access-tokens) for how to get an access token.

# In[1]:


import getpass
import os

os.environ["DATABRICKS_HOST"] = "https://your-databricks-workspace"
if "DATABRICKS_TOKEN" not in os.environ:
    os.environ["DATABRICKS_TOKEN"] = getpass.getpass(
        "Enter your Databricks access token: "
    )


# ### Installation
# 
# The LangChain Databricks integration lives in the `databricks-langchain` package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU databricks-langchain')


# ### Create a Vector Search Endpoint and Index (if you haven't already)
# 
# In this section, we will create a Databricks Vector Search endpoint and an index using the client SDK.
# 
# If you already have an endpoint and an index, you can skip the section and go straight to "Instantiation" section.

# First, instantiate the Databricks VectorSearch client:

# In[ ]:


from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()


# Next, we will create a new VectorSearch endpoint.

# In[14]:


endpoint_name = "<your-endpoint-name>"

client.create_endpoint(name=endpoint_name, endpoint_type="STANDARD")


# Lastly, we will create an index that can be queried on the endpoint. There are two types of indexes in Databricks Vector Search and the `DatabricksVectorSearch` class support both use cases.
# 
# * **Delta Sync Index** automatically syncs with a source Delta Table, automatically and incrementally updating the index as the underlying data in the Delta Table changes.
# 
# * **Direct Vector Access Index** supports direct read and write of vectors and metadata. The user is responsible for updating this table using the REST API or the Python SDK.
# 
# Also for delta-sync index, you can choose to use Databricks-managed embeddings or self-managed embeddings (via LangChain embeddings classes).

# The following code creates a **direct-access** index. Please refer to the [Databricks documentation](https://docs.databricks.com/en/generative-ai/create-query-vector-search.html) for the instruction to create the other type of indexes.

# In[ ]:


index_name = "<your-index-name>"  # Format: "<catalog>.<schema>.<index-name>"

index = client.create_direct_access_index(
    endpoint_name=endpoint_name,
    index_name=index_name,
    primary_key="id",
    # Dimension of the embeddings. Please change according to the embedding model you are using.
    embedding_dimension=3072,
    # A column to store the embedding vectors for the text data
    embedding_vector_column="text_vector",
    schema={
        "id": "string",
        "text": "string",
        "text_vector": "array<float>",
        # Optional metadata columns
        "source": "string",
    },
)

index.describe()


# ## Instantiation
# 
# The instantiation of `DatabricksVectorSearch` is a bit different depending on whether your index uses Databricks-managed embeddings or self-managed embeddings i.e. LangChain Embeddings object of your choice.

# If you are using a delta-sync index with Databricks-managed embeddings:

# In[ ]:


from databricks_langchain import DatabricksVectorSearch

vector_store = DatabricksVectorSearch(
    endpoint=endpoint_name,
    index_name=index_name,
)


# If you are using a direct-access index or a delta-sync index with self-managed embeddings,
# you also need to provide the embedding model and text column in your source table to
# use for the embeddings:
# 
# import EmbeddingTabs from "@theme/EmbeddingTabs";
# 
# <EmbeddingTabs/>
# 

# In[ ]:


# | output: false
# | echo: false
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


# In[ ]:


vector_store = DatabricksVectorSearch(
    endpoint=endpoint_name,
    index_name=index_name,
    embedding=embeddings,
    # The column name in the index that contains the text data to be embedded
    text_column="document_content",
)


# ## Manage vector store
# 
# ### Add items to vector store
# 
# Note: Adding items to vector store via `add_documents` method is only supported for a **direct-access** index.

# In[20]:


from langchain_core.documents import Document

document_1 = Document(page_content="foo", metadata={"source": "https://example.com"})

document_2 = Document(page_content="bar", metadata={"source": "https://example.com"})

document_3 = Document(page_content="baz", metadata={"source": "https://example.com"})

documents = [document_1, document_2, document_3]

vector_store.add_documents(documents=documents, ids=["1", "2", "3"])


# ### Delete items from vector store
# 
# Note: Deleting items to vector store via `delete` method is only supported for a **direct-access** index.

# In[21]:


vector_store.delete(ids=["3"])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Query directly
# 
# Performing a simple similarity search can be done as follows:

# In[23]:


results = vector_store.similarity_search(
    query="thud", k=1, filter={"source": "https://example.com"}
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


# Note: By default, similarity search only returns the primary key and text column. If you want to retrieve the custom metadata associated with the document, pass the additional columns in the `columns` parameter when initializing the vector store.

# In[35]:


vector_store = DatabricksVectorSearch(
    endpoint=endpoint_name,
    index_name=index_name,
    embedding=embeddings,
    text_column="text",
    columns=["source"],
)

results = vector_store.similarity_search(query="thud", k=1)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


# If you want to execute a similarity search and receive the corresponding scores you can run:

# In[36]:


results = vector_store.similarity_search_with_score(
    query="thud", k=1, filter={"source": "https://example.com"}
)
for doc, score in results:
    print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")


# ### Query by turning into retriever
# 
# You can also transform the vector store into a retriever for easier usage in your chains. 

# In[37]:


retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1})
retriever.invoke("thud")


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/retrieval)

# ## API reference
# 
# For detailed documentation of all DatabricksVectorSearch features and configurations head to the API reference: https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_langchain.html#databricks_langchain.DatabricksVectorSearch
