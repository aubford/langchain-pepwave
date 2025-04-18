#!/usr/bin/env python
# coding: utf-8

# # Together AI
# 
# [Together AI](https://www.together.ai/) offers an API to query [50+ leading open-source models](https://docs.together.ai/docs/inference-models) in a couple lines of code.
# 
# This example goes over how to use LangChain to interact with Together AI models.

# ## Installation

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade langchain-together')


# ## Environment
# 
# To use Together AI, you'll need an API key which you can find here:
# https://api.together.ai/settings/api-keys. This can be passed in as an init param
# ``together_api_key`` or set as environment variable ``TOGETHER_API_KEY``.
# 

# ## Example

# In[ ]:


# Querying chat models with Together AI

from langchain_together import ChatTogether

# choose from our 50+ models here: https://docs.together.ai/docs/inference-models
chat = ChatTogether(
    # together_api_key="YOUR_API_KEY",
    model="meta-llama/Llama-3-70b-chat-hf",
)

# stream the response back from the model
for m in chat.stream("Tell me fun things to do in NYC"):
    print(m.content, end="", flush=True)

# if you don't want to do streaming, you can use the invoke method
# chat.invoke("Tell me fun things to do in NYC")


# In[ ]:


# Querying code and language models with Together AI

from langchain_together import Together

llm = Together(
    model="codellama/CodeLlama-70b-Python-hf",
    # together_api_key="..."
)

print(llm.invoke("def bubble_sort(): "))

