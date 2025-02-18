#!/usr/bin/env python
# coding: utf-8

# # GPT4All
#
# [GPT4All](https://gpt4all.io/index.html) is a free-to-use, locally running, privacy-aware chatbot. There is no GPU or internet required. It features popular models and its own models such as GPT4All Falcon, Wizard, etc.
#
# This notebook explains how to use [GPT4All embeddings](https://docs.gpt4all.io/gpt4all_python_embedding.html#gpt4all.gpt4all.Embed4All) with LangChain.

# ## Install GPT4All's Python Bindings

# In[ ]:


get_ipython().run_line_magic("pip", "install --upgrade --quiet  gpt4all > /dev/null")


# Note: you may need to restart the kernel to use updated packages.

# In[1]:


from langchain_community.embeddings import GPT4AllEmbeddings


# In[2]:


gpt4all_embd = GPT4AllEmbeddings()


# In[3]:


text = "This is a test document."


# ## Embed the Textual Data

# In[4]:


query_result = gpt4all_embd.embed_query(text)


# With embed_documents you can embed multiple pieces of text. You can also map these embeddings with [Nomic's Atlas](https://docs.nomic.ai/index.html) to see a visual representation of your data.

# In[5]:


doc_result = gpt4all_embd.embed_documents([text])
