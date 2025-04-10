#!/usr/bin/env python
# coding: utf-8

# # Writer LLM
# 
# [Writer](https://writer.com/) is a platform to generate different language content.
# 
# This example goes over how to use LangChain to interact with `Writer` [models](https://dev.writer.com/docs/models).
# 
# ## Setup
# 
# To access Writer models you'll need to create a Writer account, get an API key, and install the `writer-sdk` and `langchain-community` packages.
# 
# ### Credentials
# 
# Head to [Writer AI Studio](https://app.writer.com/aistudio/signup?utm_campaign=devrel) to sign up to OpenAI and generate an API key. Once you've done this set the WRITER_API_KEY environment variable:

# In[1]:


import getpass
import os

if not os.environ.get("WRITER_API_KEY"):
    os.environ["WRITER_API_KEY"] = getpass.getpass("Enter your Writer API key:")


# ## Installation
# 
# The LangChain Writer integration lives in the `langchain-community` package:

# In[2]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community writer-sdk')


# Now we can initialize our model object to interact with writer LLMs

# In[3]:


from langchain_community.llms import Writer as WriterLLM

llm = WriterLLM(
    temperature=0.7,
    max_tokens=1000,
    # other params...
)


# ## Invocation

# In[ ]:


response_text = llm.invoke(input="Write a poem")


# In[ ]:


print(response_text)


# ## Streaming

# In[ ]:


stream_response = llm.stream(input="Tell me a fairytale")


# In[ ]:


for chunk in stream_response:
    print(chunk, end="")


# ## Async
# 
# Writer support asynchronous calls via **ainvoke()** and **astream()** methods

# ## API reference
# 
# For detailed documentation of all Writer features, head to our [API reference](https://dev.writer.com/api-guides/api-reference/completion-api/text-generation#text-generation).
