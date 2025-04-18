#!/usr/bin/env python
# coding: utf-8

# # Context
# 
# >[Context](https://context.ai/) provides user analytics for LLM-powered products and features.
# 
# With `Context`, you can start understanding your users and improving their experiences in less than 30 minutes.
# 

# In this guide we will show you how to integrate with Context.

# ## Installation and Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain langchain-openai langchain-community context-python')


# ### Getting API Credentials
# 
# To get your Context API token:
# 
# 1. Go to the settings page within your Context account (https://with.context.ai/settings).
# 2. Generate a new API Token.
# 3. Store this token somewhere secure.

# ### Setup Context
# 
# To use the `ContextCallbackHandler`, import the handler from Langchain and instantiate it with your Context API token.
# 
# Ensure you have installed the `context-python` package before using the handler.

# In[1]:


from langchain_community.callbacks.context_callback import ContextCallbackHandler


# In[3]:


import os

token = os.environ["CONTEXT_API_TOKEN"]

context_callback = ContextCallbackHandler(token)


# ## Usage
# ### Context callback within a chat model
# 
# The Context callback handler can be used to directly record transcripts between users and AI assistants.

# In[4]:


import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

token = os.environ["CONTEXT_API_TOKEN"]

chat = ChatOpenAI(
    headers={"user_id": "123"}, temperature=0, callbacks=[ContextCallbackHandler(token)]
)

messages = [
    SystemMessage(
        content="You are a helpful assistant that translates English to French."
    ),
    HumanMessage(content="I love programming."),
]

print(chat(messages))


# ### Context callback within Chains
# 
# The Context callback handler can also be used to record the inputs and outputs of chains. Note that intermediate steps of the chain are not recorded - only the starting inputs and final outputs.
# 
# __Note:__ Ensure that you pass the same context object to the chat model and the chain.
# 
# Wrong:
# > ```python
# > chat = ChatOpenAI(temperature=0.9, callbacks=[ContextCallbackHandler(token)])
# > chain = LLMChain(llm=chat, prompt=chat_prompt_template, callbacks=[ContextCallbackHandler(token)])
# > ```
# 
# Correct:
# >```python
# >handler = ContextCallbackHandler(token)
# >chat = ChatOpenAI(temperature=0.9, callbacks=[callback])
# >chain = LLMChain(llm=chat, prompt=chat_prompt_template, callbacks=[callback])
# >```
# 

# In[ ]:


import os

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

token = os.environ["CONTEXT_API_TOKEN"]

human_message_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="What is a good name for a company that makes {product}?",
        input_variables=["product"],
    )
)
chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])
callback = ContextCallbackHandler(token)
chat = ChatOpenAI(temperature=0.9, callbacks=[callback])
chain = LLMChain(llm=chat, prompt=chat_prompt_template, callbacks=[callback])
print(chain.run("colorful socks"))

