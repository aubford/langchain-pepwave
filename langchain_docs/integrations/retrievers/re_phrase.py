#!/usr/bin/env python
# coding: utf-8

# # RePhraseQuery
# 
# `RePhraseQuery` is a simple retriever that applies an LLM between the user input and the query passed by the retriever.
# 
# It can be used to pre-process the user input in any way.
# 
# ## Example
# 
# ### Setting up
# 
# Create a vector store.

# In[2]:


import logging

from langchain.retrievers import RePhraseQueryRetriever
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# In[1]:


logging.basicConfig()
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)

loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())


# ### Using the default prompt
# 
# The default prompt used in the `from_llm` classmethod:
# 
# ```
# DEFAULT_TEMPLATE = """You are an assistant tasked with taking a natural language \
# query from a user and converting it into a query for a vectorstore. \
# In this process, you strip out information that is not relevant for \
# the retrieval task. Here is the user query: {question}"""
# ```

# In[4]:


llm = ChatOpenAI(temperature=0)
retriever_from_llm = RePhraseQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(), llm=llm
)


# In[5]:


docs = retriever_from_llm.invoke(
    "Hi I'm Lance. What are the approaches to Task Decomposition?"
)


# In[6]:


docs = retriever_from_llm.invoke(
    "I live in San Francisco. What are the Types of Memory?"
)


# ### Custom prompt

# In[7]:


from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an assistant tasked with taking a natural languge query from a user
    and converting it into a query for a vectorstore. In the process, strip out all 
    information that is not relevant for the retrieval task and return a new, simplified
    question for vectorstore retrieval. The new user query should be in pirate speech.
    Here is the user query: {question} """,
)
llm = ChatOpenAI(temperature=0)
llm_chain = LLMChain(llm=llm, prompt=QUERY_PROMPT)


# In[8]:


retriever_from_llm_chain = RePhraseQueryRetriever(
    retriever=vectorstore.as_retriever(), llm_chain=llm_chain
)


# In[9]:


docs = retriever_from_llm_chain.invoke(
    "Hi I'm Lance. What is Maximum Inner Product Search?"
)

