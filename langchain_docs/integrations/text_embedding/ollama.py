#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Ollama
---
# # OllamaEmbeddings
# 
# This will help you get started with Ollama embedding models using LangChain. For detailed documentation on `OllamaEmbeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/ollama/embeddings/langchain_ollama.embeddings.OllamaEmbeddings.html).
# 
# ## Overview
# ### Integration details
# 
# import { ItemTable } from "@theme/FeatureTables";
# 
# <ItemTable category="text_embedding" item="Ollama" />
# 
# ## Setup
# 
# First, follow [these instructions](https://github.com/jmorganca/ollama) to set up and run a local Ollama instance:
# 
# * [Download](https://ollama.ai/download) and install Ollama onto the available supported platforms (including Windows Subsystem for Linux)
# * Fetch available LLM model via `ollama pull <name-of-model>`
#     * View a list of available models via the [model library](https://ollama.ai/library)
#     * e.g., `ollama pull llama3`
# * This will download the default tagged version of the model. Typically, the default points to the latest, smallest sized-parameter model.
# 
# > On Mac, the models will be download to `~/.ollama/models`
# >
# > On Linux (or WSL), the models will be stored at `/usr/share/ollama/.ollama/models`
# 
# * Specify the exact version of the model of interest as such `ollama pull vicuna:13b-v1.5-16k-q4_0` (View the [various tags for the `Vicuna`](https://ollama.ai/library/vicuna/tags) model in this instance)
# * To view all pulled models, use `ollama list`
# * To chat directly with a model from the command line, use `ollama run <name-of-model>`
# * View the [Ollama documentation](https://github.com/jmorganca/ollama) for more commands. Run `ollama help` in the terminal to see available commands too.
# 
# 
# ### Credentials
# 
# There is no built-in auth mechanism for Ollama.

# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[1]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain Ollama integration lives in the `langchain-ollama` package:

# In[2]:


get_ipython().run_line_magic('pip', 'install -qU langchain-ollama')


# ## Instantiation
# 
# Now we can instantiate our model object and generate embeddings:

# In[3]:


from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="llama3",
)


# ## Indexing and Retrieval
# 
# Embedding models are often used in retrieval-augmented generation (RAG) flows, both as part of indexing data as well as later retrieving it. For more detailed instructions, please see our [RAG tutorials](/docs/tutorials/).
# 
# Below, see how to index and retrieve data using the `embeddings` object we initialized above. In this example, we will index and retrieve a sample document in the `InMemoryVectorStore`.

# In[4]:


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

# In[5]:


single_vector = embeddings.embed_query(text)
print(str(single_vector)[:100])  # Show the first 100 characters of the vector


# ### Embed multiple texts
# 
# You can embed multiple texts with `embed_documents`:

# In[6]:


text2 = (
    "LangGraph is a library for building stateful, multi-actor applications with LLMs"
)
two_vectors = embeddings.embed_documents([text, text2])
for vector in two_vectors:
    print(str(vector)[:100])  # Show the first 100 characters of the vector


# ## API Reference
# 
# For detailed documentation on `OllamaEmbeddings` features and configuration options, please refer to the [API reference](https://python.langchain.com/api_reference/ollama/embeddings/langchain_ollama.embeddings.OllamaEmbeddings.html).
# 
