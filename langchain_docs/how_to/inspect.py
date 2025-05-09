#!/usr/bin/env python
# coding: utf-8

# # How to inspect runnables
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [LangChain Expression Language (LCEL)](/docs/concepts/lcel)
# - [Chaining runnables](/docs/how_to/sequence/)
# 
# :::
# 
# Once you create a runnable with [LangChain Expression Language](/docs/concepts/lcel), you may often want to inspect it to get a better sense for what is going on. This notebook covers some methods for doing so.
# 
# This guide shows some ways you can programmatically introspect the internal steps of chains. If you are instead interested in debugging issues in your chain, see [this section](/docs/how_to/debugging) instead.
# 
# First, let's create an example chain. We will create one that does retrieval:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain-openai faiss-cpu tiktoken')


# In[2]:


from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

vectorstore = FAISS.from_texts(
    ["harrison worked at kensho"], embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()

template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

model = ChatOpenAI()

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)


# ## Get a graph
# 
# You can use the `get_graph()` method to get a graph representation of the runnable:

# In[ ]:


chain.get_graph()


# ## Print a graph
# 
# While that is not super legible, you can use the `print_ascii()` method to show that graph in a way that's easier to understand:

# In[5]:


chain.get_graph().print_ascii()


# ## Get the prompts
# 
# You may want to see just the prompts that are used in a chain with the `get_prompts()` method:

# In[6]:


chain.get_prompts()


# ## Next steps
# 
# You've now learned how to introspect your composed LCEL chains.
# 
# Next, check out the other how-to guides on runnables in this section, or the related how-to guide on [debugging your chains](/docs/how_to/debugging).

# In[ ]:




