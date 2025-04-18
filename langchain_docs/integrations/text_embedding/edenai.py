#!/usr/bin/env python
# coding: utf-8

# # EDEN AI

# Eden AI is revolutionizing the AI landscape by uniting the best AI providers, empowering users to unlock limitless possibilities and tap into the true potential of artificial intelligence. With an all-in-one comprehensive and hassle-free platform, it allows users to deploy AI features to production lightning fast, enabling effortless access to the full breadth of AI capabilities via a single API. (website: https://edenai.co/)

# This example goes over how to use LangChain to interact with Eden AI embedding models
# 
# -----------------------------------------------------------------------------------
# 

# Accessing the EDENAI's API requires an API key, 
# 
# which you can get by creating an account https://app.edenai.run/user/register  and heading here https://app.edenai.run/admin/account/settings
# 
# Once we have a key we'll want to set it as an environment variable by running:
# 
# ```shell
# export EDENAI_API_KEY="..."
# ```
# 

# If you'd prefer not to set an environment variable you can pass the key in directly via the edenai_api_key named parameter
# 
#  when initiating the EdenAI embedding class:
# 
# 

# In[1]:


from langchain_community.embeddings.edenai import EdenAiEmbeddings


# In[12]:


embeddings = EdenAiEmbeddings(edenai_api_key="...", provider="...")


# ## Calling a model
# 

# The EdenAI API brings together various providers.
# 
# To access a specific model, you can simply use the "provider" when calling.
# 

# In[13]:


embeddings = EdenAiEmbeddings(provider="openai")


# In[14]:


docs = ["It's raining right now", "cats are cute"]
document_result = embeddings.embed_documents(docs)


# In[15]:


query = "my umbrella is broken"
query_result = embeddings.embed_query(query)


# In[16]:


import numpy as np

query_numpy = np.array(query_result)
for doc_res, doc in zip(document_result, docs):
    document_numpy = np.array(doc_res)
    similarity = np.dot(query_numpy, document_numpy) / (
        np.linalg.norm(query_numpy) * np.linalg.norm(document_numpy)
    )
    print(f'Cosine similarity between "{doc}" and query: {similarity}')

