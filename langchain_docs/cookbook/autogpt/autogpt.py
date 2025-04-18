#!/usr/bin/env python
# coding: utf-8

# # AutoGPT
# 
# Implementation of https://github.com/Significant-Gravitas/Auto-GPT but with LangChain primitives (LLMs, PromptTemplates, VectorStores, Embeddings, Tools)

# ## Set up tools
# 
# We'll set up an AutoGPT with a search tool, and write-file tool, and a read-file tool

# In[2]:


from langchain.agents import Tool
from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.utilities import SerpAPIWrapper

search = SerpAPIWrapper()
tools = [
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    WriteFileTool(),
    ReadFileTool(),
]


# ## Set up memory
# 
# The memory here is used for the agents intermediate steps

# In[3]:


from langchain.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


# In[4]:


# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty
import faiss

embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})


# ## Setup model and AutoGPT
# 
# Initialize everything! We will use ChatOpenAI model

# In[5]:


from langchain_experimental.autonomous_agents import AutoGPT
from langchain_openai import ChatOpenAI


# In[6]:


agent = AutoGPT.from_llm_and_tools(
    ai_name="Tom",
    ai_role="Assistant",
    tools=tools,
    llm=ChatOpenAI(temperature=0),
    memory=vectorstore.as_retriever(),
)
# Set verbose to be true
agent.chain.verbose = True


# ## Run an example
# 
# Here we will make it write a weather report for SF

# In[ ]:


agent.run(["write a weather report for SF today"])


# ## Chat History Memory
# 
# In addition to the memory that holds the agent immediate steps, we also have a chat history memory. By default, the agent will use 'ChatMessageHistory' and it can be changed. This is useful when you want to use a different type of memory for example 'FileChatHistoryMemory'

# In[ ]:


from langchain_community.chat_message_histories import FileChatMessageHistory

agent = AutoGPT.from_llm_and_tools(
    ai_name="Tom",
    ai_role="Assistant",
    tools=tools,
    llm=ChatOpenAI(temperature=0),
    memory=vectorstore.as_retriever(),
    chat_history_memory=FileChatMessageHistory("chat_history.txt"),
)


# 
