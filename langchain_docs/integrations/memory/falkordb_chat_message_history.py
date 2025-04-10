#!/usr/bin/env python
# coding: utf-8

# # FalkorDB
# 
# <a href='https://docs.falkordb.com/' target='_blank'>FalkorDB</a> is an open-source graph database management system, renowned for its efficient management of highly connected data. Unlike traditional databases that store data in tables, FalkorDB uses a graph structure with nodes, edges, and properties to represent and store data. This design allows for high-performance queries on complex data relationships.
# 
# This notebook goes over how to use `FalkorDB` to store chat message history
# 
# **NOTE**: You can use FalkorDB locally or use FalkorDB Cloud. <a href='https://docs.falkordb.com/' target='blank'>See installation instructions</a>

# In[6]:


# For this example notebook we will be using FalkorDB locally
host = "localhost"
port = 6379


# In[8]:


from langchain_falkordb.message_history import (
    FalkorDBChatMessageHistory,
)

history = FalkorDBChatMessageHistory(host=host, port=port, session_id="session_id_1")

history.add_user_message("hi!")

history.add_ai_message("whats up?")


# In[9]:


history.messages

