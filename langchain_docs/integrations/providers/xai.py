#!/usr/bin/env python
# coding: utf-8

# # xAI
# 
# [xAI](https://console.x.ai) offers an API to interact with Grok models.
# 
# This example goes over how to use LangChain to interact with xAI models.

# ## Installation

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade langchain-xai')


# ## Environment
# 
# To use xAI, you'll need to [create an API key](https://console.x.ai/). The API key can be passed in as an init param ``xai_api_key`` or set as environment variable ``XAI_API_KEY``.

# ## Example

# In[ ]:


# Querying chat models with xAI

from langchain_xai import ChatXAI

chat = ChatXAI(
    # xai_api_key="YOUR_API_KEY",
    model="grok-beta",
)

# stream the response back from the model
for m in chat.stream("Tell me fun things to do in NYC"):
    print(m.content, end="", flush=True)

# if you don't want to do streaming, you can use the invoke method
# chat.invoke("Tell me fun things to do in NYC")

