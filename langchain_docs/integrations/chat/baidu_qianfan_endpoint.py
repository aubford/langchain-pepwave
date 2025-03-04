#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Baidu Qianfan
---
# # QianfanChatEndpoint
# 
# Baidu AI Cloud Qianfan Platform is a one-stop large model development and service operation platform for enterprise developers. Qianfan not only provides including the model of Wenxin Yiyan (ERNIE-Bot) and the third-party open-source models, but also provides various AI development tools and the whole set of development environment, which facilitates customers to use and develop large model applications easily.
# 
# Basically, those model are split into the following type:
# 
# - Embedding
# - Chat
# - Completion
# 
# In this notebook, we will introduce how to use langchain with [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html) mainly in `Chat` corresponding
#  to the package `langchain/chat_models` in langchain:
# 
# 
# ## API Initialization
# 
# To use the LLM services based on Baidu Qianfan, you have to initialize these parameters:
# 
# You could either choose to init the AK,SK in environment variables or init params:
# 
# ```base
# export QIANFAN_AK=XXX
# export QIANFAN_SK=XXX
# ```
# 
# ## Current supported models:
# 
# - ERNIE-Bot-turbo (default models)
# - ERNIE-Bot
# - BLOOMZ-7B
# - Llama-2-7b-chat
# - Llama-2-13b-chat
# - Llama-2-70b-chat
# - Qianfan-BLOOMZ-7B-compressed
# - Qianfan-Chinese-Llama-2-7B
# - ChatGLM2-6B-32K
# - AquilaChat-7B

# ## Set up

# In[1]:


"""For basic init and call"""
import os

from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.language_models.chat_models import HumanMessage

os.environ["QIANFAN_AK"] = "Your_api_key"
os.environ["QIANFAN_SK"] = "You_secret_Key"


# ## Usage

# In[2]:


chat = QianfanChatEndpoint(streaming=True)
messages = [HumanMessage(content="Hello")]
chat.invoke(messages)


# In[3]:


await chat.ainvoke(messages)


# In[4]:


chat.batch([messages])


# ### Streaming

# In[5]:


try:
    for chunk in chat.stream(messages):
        print(chunk.content, end="", flush=True)
except TypeError as e:
    print("")


# ## Use different models in Qianfan
# 
# The default model is ERNIE-Bot-turbo, in the case you want to deploy your own model based on Ernie Bot or third-party open-source model, you could follow these steps:
# 
# 1. (Optional, if the model are included in the default models, skip it) Deploy your model in Qianfan Console, get your own customized deploy endpoint.
# 2. Set up the field called `endpoint` in the initialization:

# In[6]:


chatBot = QianfanChatEndpoint(
    streaming=True,
    model="ERNIE-Bot",
)

messages = [HumanMessage(content="Hello")]
chatBot.invoke(messages)


# ## Model Params:
# 
# For now, only `ERNIE-Bot` and `ERNIE-Bot-turbo` support model params below, we might support more models in the future.
# 
# - temperature
# - top_p
# - penalty_score
# 

# In[7]:


chat.invoke(
    [HumanMessage(content="Hello")],
    **{"top_p": 0.4, "temperature": 0.1, "penalty_score": 1},
)

