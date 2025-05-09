#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: SambaNovaCloud
---
# # SambaNovaCloudEmbeddings
# 
# This will help you getting started with SambaNovaCloud embedding models using LangChain. For detailed documentation on `SambaNovaCloudEmbeddings` features and configuration options, please refer to the [API reference](https://docs.sambanova.ai/cloud/docs/get-started/overview).
# 
# **[SambaNova](https://sambanova.ai/)'s** [SambaNova Cloud](https://cloud.sambanova.ai/) is a platform for performing inference with open-source models
# 
# ## Overview
# ### Integration details
# 
# | Provider | Package |
# |:--------:|:-------:|
# | [SambaNova](/docs/integrations/providers/sambanova/) | [langchain-sambanova](https://python.langchain.com/docs/integrations/providers/sambanova/) |
# 
# ## Setup
# 
# To access ChatSambaNovaCloud models you will need to create a [SambaNovaCloud](https://cloud.sambanova.ai/) account, get an API key, install the `langchain_sambanova` integration package.
# 
# ```bash
# pip install langchain-sambanova
# ```
# 
# ### Credentials
# 
# Get an API Key from [cloud.sambanova.ai](https://cloud.sambanova.ai/apis) and add it to your environment variables:
# 
# ``` bash
# export SAMBANOVA_API_KEY="your-api-key-here"
# ```

# In[ ]:


import getpass
import os

if not os.getenv("SAMBANOVA_API_KEY"):
    os.environ["SAMBANOVA_API_KEY"] = getpass.getpass("Enter your SambaNova API key: ")


# If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain SambaNova integration lives in the `langchain-sambanova` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-sambanova')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[ ]:


from langchain_sambanova import SambaNovaCloudEmbeddings

embeddings = SambaNovaCloudEmbeddings(
    model="E5-Mistral-7B-Instruct",
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
retrieved_documents = retriever.invoke("What is LangChain?")

# show the retrieved document's content
retrieved_documents[0].page_content


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


# ## API Reference
# 
# For detailed documentation on `SambaNovaCloud` features and configuration options, please refer to the [API reference](https://docs.sambanova.ai/cloud/docs/get-started/overview).
# 
