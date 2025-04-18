#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 4
---
# # How to handle multiple queries when doing query analysis
# 
# Sometimes, a query analysis technique may allow for multiple queries to be generated. In these cases, we need to remember to run all queries and then to combine the results. We will show a simple example (using mock data) of how to do that.

# ## Setup
# #### Install dependencies

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain langchain-community langchain-openai langchain-chroma')


# #### Set environment variables
# 
# We'll use OpenAI in this example:

# In[2]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass()

# Optional, uncomment to trace runs with LangSmith. Sign up here: https://smith.langchain.com.
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ### Create Index
# 
# We will create a vectorstore over fake information.

# In[3]:


from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

texts = ["Harrison worked at Kensho", "Ankush worked at Facebook"]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_texts(
    texts,
    embeddings,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})


# ## Query analysis
# 
# We will use function calling to structure the output. We will let it return multiple queries.

# In[4]:


from typing import List, Optional

from pydantic import BaseModel, Field


class Search(BaseModel):
    """Search over a database of job records."""

    queries: List[str] = Field(
        ...,
        description="Distinct queries to search for",
    )


# In[5]:


from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

output_parser = PydanticToolsParser(tools=[Search])

system = """You have the ability to issue search queries to get information to help answer user information.

If you need to look up two distinct pieces of information, you are allowed to do that!"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(Search)
query_analyzer = {"question": RunnablePassthrough()} | prompt | structured_llm


# We can see that this allows for creating multiple queries

# In[6]:


query_analyzer.invoke("where did Harrison Work")


# In[7]:


query_analyzer.invoke("where did Harrison and ankush Work")


# ## Retrieval with query analysis
# 
# So how would we include this in a chain? One thing that will make this a lot easier is if we call our retriever asynchronously - this will let us loop over the queries and not get blocked on the response time.

# In[8]:


from langchain_core.runnables import chain


# In[9]:


@chain
async def custom_chain(question):
    response = await query_analyzer.ainvoke(question)
    docs = []
    for query in response.queries:
        new_docs = await retriever.ainvoke(query)
        docs.extend(new_docs)
    # You probably want to think about reranking or deduplicating documents here
    # But that is a separate topic
    return docs


# In[10]:


await custom_chain.ainvoke("where did Harrison Work")


# In[11]:


await custom_chain.ainvoke("where did Harrison and ankush Work")


# In[ ]:




