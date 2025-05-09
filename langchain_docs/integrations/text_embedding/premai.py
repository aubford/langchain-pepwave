#!/usr/bin/env python
# coding: utf-8

# # PremAI
# 
# [PremAI](https://premai.io/) is an all-in-one platform that simplifies the creation of robust, production-ready applications powered by Generative AI. By streamlining the development process, PremAI allows you to concentrate on enhancing user experience and driving overall growth for your application. You can quickly start using our platform [here](https://docs.premai.io/quick-start).
# 
# ### Installation and setup
# 
# We start by installing `langchain` and `premai-sdk`. You can type the following command to install:
# 
# ```bash
# pip install premai langchain
# ```
# 
# Before proceeding further, please make sure that you have made an account on PremAI and already created a project. If not, please refer to the [quick start](https://docs.premai.io/introduction) guide to get started with the PremAI platform. Create your first project and grab your API key.

# ## PremEmbeddings
# 
# In this section we are going to dicuss how we can get access to different embedding model using `PremEmbeddings` with LangChain. Lets start by importing our modules and setting our API Key. 

# In[1]:


# Let's start by doing some imports and define our embedding object

from langchain_community.embeddings import PremAIEmbeddings


# Once we imported our required modules, let's setup our client. For now let's assume that our `project_id` is `8`. But make sure you use your project-id, otherwise it will throw error.
# 
# > Note: Setting `model_name` argument in mandatory for PremAIEmbeddings unlike [ChatPremAI.](https://python.langchain.com/v0.1/docs/integrations/chat/premai/)

# In[2]:


import getpass
import os

if os.environ.get("PREMAI_API_KEY") is None:
    os.environ["PREMAI_API_KEY"] = getpass.getpass("PremAI API Key:")


# In[3]:


model = "text-embedding-3-large"
embedder = PremAIEmbeddings(project_id=8, model=model)


# We support lots of state of the art embedding models. You can view our list of supported LLMs and embedding models [here](https://docs.premai.io/get-started/supported-models). For now let's go for `text-embedding-3-large` model for this example.

# In[4]:


query = "Hello, this is a test query"
query_result = embedder.embed_query(query)

# Let's print the first five elements of the query embedding vector

print(query_result[:5])


# Finally let's embed a document

# In[5]:


documents = ["This is document1", "This is document2", "This is document3"]

doc_result = embedder.embed_documents(documents)

# Similar to previous result, let's print the first five element
# of the first document vector

print(doc_result[0][:5])

