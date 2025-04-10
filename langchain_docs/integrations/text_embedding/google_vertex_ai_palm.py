#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Google Vertex AI
keywords: [Vertex AI, vertexai , Google Cloud, embeddings]
---
# # Google Vertex AI Embeddings
# 
# This will help you get started with Google Vertex AI Embeddings models using LangChain. For detailed documentation on `Google Vertex AI Embeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/google_vertexai/embeddings/langchain_google_vertexai.embeddings.VertexAIEmbeddings.html).
# 
# ## Overview
# ### Integration details
# 
# | Provider | Package |
# |:--------:|:-------:|
# | [Google](https://python.langchain.com/docs/integrations/providers/google/) | [langchain-google-vertexai](https://python.langchain.com/api_reference/google_vertexai/embeddings/langchain_google_vertexai.embeddings.VertexAIEmbeddings.html) |
# 
# ## Setup
# 
# To access Google Vertex AI Embeddings models you'll need to
# - Create a Google Cloud account
# - Install the `langchain-google-vertexai` integration package.
# 
# 
# 
# 
# ### Credentials
# 
# 
# Head to [Google Cloud](https://cloud.google.com/free/) to sign up to create an account. Once you've done this set the GOOGLE_APPLICATION_CREDENTIALS environment variable:
# 
# For more information, see:
# 
# https://cloud.google.com/docs/authentication/application-default-credentials#GAC
# https://googleapis.dev/python/google-auth/latest/reference/google.auth.html#module-google.auth

# **OPTIONAL : Authenticate your notebook environment (Colab only)**
# 
# If you're running this notebook on Google Colab, run the cell below to authenticate your environment.

# In[ ]:


import sys

if "google.colab" in sys.modules:
    from google.colab import auth

    auth.authenticate_user()


# **Set Google Cloud project information and initialize Vertex AI SDK**
# 
# To get started using Vertex AI, you must have an existing Google Cloud project and [enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
# 
# Learn more about [setting up a project and a development environment](https://cloud.google.com/vertex-ai/docs/start/cloud-environment).

# In[ ]:


PROJECT_ID = "[your-project-id]"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}

import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain Google Vertex AI Embeddings integration lives in the `langchain-google-vertexai` package:

# In[4]:


get_ipython().run_line_magic('pip', 'install -qU langchain-google-vertexai')


# ## Instantiation
# 
# Now we can instantiate our model object and generate embeddings:
# >Check the list of [Supported Models](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings#supported-models)

# In[2]:


from langchain_google_vertexai import VertexAIEmbeddings

# Initialize the a specific Embeddings Model version
embeddings = VertexAIEmbeddings(model_name="text-embedding-004")


# ## Indexing and Retrieval
# 
# Embedding models are often used in retrieval-augmented generation (RAG) flows, both as part of indexing data as well as later retrieving it. For more detailed instructions, please see our [RAG tutorials](/docs/tutorials/).
# 
# Below, see how to index and retrieve data using the `embeddings` object we initialized above. In this example, we will index and retrieve a sample document in the `InMemoryVectorStore`.

# In[3]:


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

# In[4]:


single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector


# ### Embed multiple texts
# 
# You can embed multiple texts with `embed_documents`:

# In[5]:


text2 = (
    "LangGraph is a library for building stateful, multi-actor applications with LLMs"
)
two_vectors = embeddings.embed_documents([text, text2])
for vector in two_vectors:
    print(str(vector)[:100])  # Show the first 100 characters of the vector


# ## API Reference
# 
# For detailed documentation on `Google Vertex AI Embeddings
# ` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/google_vertexai/embeddings/langchain_google_vertexai.embeddings.VertexAIEmbeddings.html).
# 
