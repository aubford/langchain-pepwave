#!/usr/bin/env python
# coding: utf-8

# # TextEmbed - Embedding Inference Server
# 
# TextEmbed is a high-throughput, low-latency REST API designed for serving vector embeddings. It supports a wide range of sentence-transformer models and frameworks, making it suitable for various applications in natural language processing.
# 
# ## Features
# 
# - **High Throughput & Low Latency:** Designed to handle a large number of requests efficiently.
# - **Flexible Model Support:** Works with various sentence-transformer models.
# - **Scalable:** Easily integrates into larger systems and scales with demand.
# - **Batch Processing:** Supports batch processing for better and faster inference.
# - **OpenAI Compatible REST API Endpoint:** Provides an OpenAI compatible REST API endpoint.
# - **Single Line Command Deployment:** Deploy multiple models via a single command for efficient deployment.
# - **Support for Embedding Formats:** Supports binary, float16, and float32 embeddings formats for faster retrieval.
# 
# ## Getting Started
# 
# ### Prerequisites
# 
# Ensure you have Python 3.10 or higher installed. You will also need to install the required dependencies.

# ## Installation via PyPI
# 
# 1. **Install the required dependencies:**
# 
#     ```bash
#     pip install -U textembed
#     ```
# 
# 2. **Start the TextEmbed server with your desired models:**
# 
#     ```bash
#     python -m textembed.server --models sentence-transformers/all-MiniLM-L12-v2 --workers 4 --api-key TextEmbed 
#     ```
# 
# For more information, please read the [documentation](https://github.com/kevaldekivadiya2415/textembed/blob/main/docs/setup.md).

# ### Import

# In[2]:


from langchain_community.embeddings import TextEmbedEmbeddings


# In[11]:


embeddings = TextEmbedEmbeddings(
    model="sentence-transformers/all-MiniLM-L12-v2",
    api_url="http://0.0.0.0:8000/v1",
    api_key="TextEmbed",
)


# ### Embed your documents

# In[23]:


# Define a list of documents
documents = [
    "Data science involves extracting insights from data.",
    "Artificial intelligence is transforming various industries.",
    "Cloud computing provides scalable computing resources over the internet.",
    "Big data analytics helps in understanding large datasets.",
    "India has a diverse cultural heritage.",
]

# Define a query
query = "What is the cultural heritage of India?"


# In[24]:


# Embed all documents
document_embeddings = embeddings.embed_documents(documents)

# Embed the query
query_embedding = embeddings.embed_query(query)


# In[25]:


# Compute Similarity
import numpy as np

scores = np.array(document_embeddings) @ np.array(query_embedding).T
dict(zip(documents, scores))


# In[ ]:




