#!/usr/bin/env python
# coding: utf-8

# # AwaDB
# 
# >[AwaDB](https://github.com/awa-ai/awadb) is an AI Native database for the search and storage of embedding vectors used by LLM Applications.
# 
# This notebook explains how to use `AwaEmbeddings` in LangChain.

# In[1]:


# pip install awadb


# ## import the library

# In[2]:


from langchain_community.embeddings import AwaEmbeddings


# In[3]:


Embedding = AwaEmbeddings()


# # Set embedding model
# Users can use `Embedding.set_model()` to specify the embedding model. \
# The input of this function is a string which represents the model's name. \
# The list of currently supported models can be obtained [here](https://github.com/awa-ai/awadb) \ \ 
# 
# The **default model** is `all-mpnet-base-v2`, it can be used without setting.

# In[4]:


text = "our embedding test"

Embedding.set_model("all-mpnet-base-v2")


# In[5]:


res_query = Embedding.embed_query("The test information")
res_document = Embedding.embed_documents(["test1", "another test"])

