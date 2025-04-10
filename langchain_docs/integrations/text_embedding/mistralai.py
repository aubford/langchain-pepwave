#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: MistralAI
---
# # MistralAIEmbeddings
# 
# This will help you get started with MistralAI embedding models using LangChain. For detailed documentation on `MistralAIEmbeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/mistralai/embeddings/langchain_mistralai.embeddings.MistralAIEmbeddings.html).
# 
# ## Overview
# ### Integration details
# 
# import { ItemTable } from "@theme/FeatureTables";
# 
# <ItemTable category="text_embedding" item="MistralAI" />
# 
# ## Setup
# 
# To access MistralAI embedding models you'll need to create a/an MistralAI account, get an API key, and install the `langchain-mistralai` integration package.
# 
# ### Credentials
# 
# Head to [https://console.mistral.ai/](https://console.mistral.ai/) to sign up to MistralAI and generate an API key. Once you've done this set the MISTRALAI_API_KEY environment variable:

# In[1]:


import getpass
import os

if not os.getenv("MISTRALAI_API_KEY"):
    os.environ["MISTRALAI_API_KEY"] = getpass.getpass("Enter your MistralAI API key: ")


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[2]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain MistralAI integration lives in the `langchain-mistralai` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-mistralai')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[4]:


from langchain_mistralai import MistralAIEmbeddings

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
)


# ## Indexing and Retrieval
# 
# Embedding models are often used in retrieval-augmented generation (RAG) flows, both as part of indexing data as well as later retrieving it. For more detailed instructions, please see our [RAG tutorials](/docs/tutorials/).
# 
# Below, see how to index and retrieve data using the `embeddings` object we initialized above. In this example, we will index and retrieve a sample document in the `InMemoryVectorStore`.

# In[5]:


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

# In[6]:


single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector


# ### Embed multiple texts
# 
# You can embed multiple texts with `embed_documents`:

# In[7]:


text2 = (
    "LangGraph is a library for building stateful, multi-actor applications with LLMs"
)
two_vectors = embeddings.embed_documents([text, text2])
for vector in two_vectors:
    print(str(vector)[:100])  # Show the first 100 characters of the vector


# ## API Reference
# 
# For detailed documentation on `MistralAIEmbeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/mistralai/embeddings/langchain_mistralai.embeddings.MistralAIEmbeddings.html).
# 
