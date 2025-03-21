#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Moonshot
---
# # MoonshotChat
# 
# [Moonshot](https://platform.moonshot.cn/) is a Chinese startup that provides LLM service for companies and individuals.
# 
# This example goes over how to use LangChain to interact with Moonshot Inference for Chat.

# In[ ]:


import os

# Generate your api key from: https://platform.moonshot.cn/console/api-keys
os.environ["MOONSHOT_API_KEY"] = "MOONSHOT_API_KEY"


# In[ ]:


from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.messages import HumanMessage, SystemMessage


# In[ ]:


chat = MoonshotChat()
# or use a specific model
# Available models: https://platform.moonshot.cn/docs
# chat = MoonshotChat(model="moonshot-v1-128k")


# In[ ]:


messages = [
    SystemMessage(
        content="You are a helpful assistant that translates English to French."
    ),
    HumanMessage(
        content="Translate this sentence from English to French. I love programming."
    ),
]

chat.invoke(messages)

