#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Databricks
---
# # DatabricksEmbeddings
# 
# > [Databricks](https://www.databricks.com/) Lakehouse Platform unifies data, analytics, and AI on one platform.
# 
# This notebook provides a quick overview for getting started with Databricks [embedding models](/docs/concepts/embedding_models). For detailed documentation of all `DatabricksEmbeddings` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.databricks.DatabricksEmbeddings.html).
# 
# 
# 
# ## Overview
# ### Integration details
# 
# | Class | Package |
# | :--- | :--- |
# | [DatabricksEmbeddings](https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.databricks.DatabricksEmbeddings.html) | [databricks-langchain](https://python.langchain.com/docs/integrations/providers/databricks/) |
# 
# ### Supported Methods
# 
# `DatabricksEmbeddings` supports all methods of `Embeddings` class including async APIs.
# 
# 
# ### Endpoint Requirement
# 
# The serving endpoint `DatabricksEmbeddings` wraps must have OpenAI-compatible embedding input/output format ([reference](https://mlflow.org/docs/latest/llms/deployments/index.html#embeddings)). As long as the input format is compatible, `DatabricksEmbeddings` can be used for any endpoint type hosted on [Databricks Model Serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html):
# 
# 1. Foundation Models - Curated list of state-of-the-art foundation models such as BAAI General Embedding (BGE). These endpoint are ready to use in your Databricks workspace without any set up.
# 2. Custom Models - You can also deploy custom embedding models to a serving endpoint via MLflow with
# your choice of framework such as LangChain, Pytorch, Transformers, etc.
# 3. External Models - Databricks endpoints can serve models that are hosted outside Databricks as a proxy, such as proprietary model service like OpenAI text-embedding-3.
# 
# 
# ## Setup
# 
# To access Databricks models you'll need to create a Databricks account, set up credentials (only if you are outside Databricks workspace), and install required packages.
# 
# ### Credentials (only if you are outside Databricks)
# 
# If you are running LangChain app inside Databricks, you can skip this step.
# 
# Otherwise, you need manually set the Databricks workspace hostname and personal access token to `DATABRICKS_HOST` and `DATABRICKS_TOKEN` environment variables, respectively. See [Authentication Documentation](https://docs.databricks.com/en/dev-tools/auth/index.html#databricks-personal-access-tokens) for how to get an access token.

# In[ ]:


import getpass
import os

os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"
if "DATABRICKS_TOKEN" not in os.environ:
    os.environ["DATABRICKS_TOKEN"] = getpass.getpass(
        "Enter your Databricks access token: "
    )


# ### Installation
# 
# The LangChain Databricks integration lives in the `databricks-langchain` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU databricks-langchain')


# ## Instantiation

# In[ ]:


from databricks_langchain import DatabricksEmbeddings

embeddings = DatabricksEmbeddings(
    endpoint="databricks-bge-large-en",
    # Specify parameters for embedding queries and documents if needed
    # query_params={...},
    # document_params={...},
)


# ## Indexing and Retrieval
# 
# Embedding models are often used in retrieval-augmented generation (RAG) flows, both as part of indexing data as well as later retrieving it. For more detailed instructions, please see our [RAG tutorials](/docs/tutorials/).
# 
# Below, see how to index and retrieve data using the `embeddings` object we initialized above. In this example, we will index and retrieve a sample document in the `InMemoryVectorStore`.

# In[ ]:


# Create a vector store with a sample text
from langchain_core.vectorstores import InMemoryVectorStore

text = "LangChain is the framework for building context-aware reasoning applications"

vectorstore = InMemoryVectorStore.from_texts(
    [text],
    embedding=embeddings,
)

# Use the vectorstore as a retriever
retriever = vectorstore.as_retriever()

# Retrieve the most similar text
retrieved_document = retriever.invoke("What is LangChain?")

# show the retrieved document's content
retrieved_document[0].page_content


# ## Direct Usage
# 
# Under the hood, the vectorstore and retriever implementations are calling `embeddings.embed_documents(...)` and `embeddings.embed_query(...)` to create embeddings for the text(s) used in `from_texts` and retrieval `invoke` operations, respectively.
# 
# You can directly call these methods to get embeddings for your own use cases.
# 
# ### Embed single texts
# 
# You can embed single texts or documents with `embed_query`:

# In[ ]:


single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector


# ### Embed multiple texts
# 
# You can embed multiple texts with `embed_documents`:

# In[ ]:


text2 = (
    "LangGraph is a library for building stateful, multi-actor applications with LLMs"
)
two_vectors = embeddings.embed_documents([text, text2])
for vector in two_vectors:
    print(str(vector)[:100])  # Show the first 100 characters of the vector


# ### Async Usage
# 
# You can also use `aembed_query` and `aembed_documents` for producing embeddings asynchronously:
# 

# In[ ]:


import asyncio


async def async_example():
    single_vector = await embeddings.aembed_query(text)
    print(str(single_vector)[:100])  # Show the first 100 characters of the vector


asyncio.run(async_example())


# ## API Reference
# 
# For detailed documentation on `DatabricksEmbeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.databricks.DatabricksEmbeddings.html).
# 
