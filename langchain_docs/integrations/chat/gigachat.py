#!/usr/bin/env python
# coding: utf-8

# # GigaChat
# This notebook shows how to use LangChain with [GigaChat](https://developers.sber.ru/portal/products/gigachat).
# To use you need to install ```langchain_gigachat``` python package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-gigachat')


# To get GigaChat credentials you need to [create account](https://developers.sber.ru/studio/login) and [get access to API](https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart)
# 
# ## Example

# In[2]:


import os
from getpass import getpass

if "GIGACHAT_CREDENTIALS" not in os.environ:
    os.environ["GIGACHAT_CREDENTIALS"] = getpass()


# In[5]:


from langchain_gigachat import GigaChat

chat = GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_PERS")


# In[6]:


from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(
        content="You are a helpful AI that shares everything you know. Talk in English."
    ),
    HumanMessage(content="What is capital of Russia?"),
]

print(chat.invoke(messages).content)

