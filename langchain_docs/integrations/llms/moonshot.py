#!/usr/bin/env python
# coding: utf-8

# # MoonshotChat
# 
# [Moonshot](https://platform.moonshot.cn/) is a Chinese startup that provides LLM service for companies and individuals.
# 
# This example goes over how to use LangChain to interact with Moonshot.

# In[33]:


from langchain_community.llms.moonshot import Moonshot


# In[ ]:


import os

# Generate your api key from: https://platform.moonshot.cn/console/api-keys
os.environ["MOONSHOT_API_KEY"] = "MOONSHOT_API_KEY"


# In[34]:


llm = Moonshot()
# or use a specific model
# Available models: https://platform.moonshot.cn/docs
# llm = Moonshot(model="moonshot-v1-128k")


# In[ ]:


# Prompt the model
llm.invoke("What is the difference between panda and bear?")

