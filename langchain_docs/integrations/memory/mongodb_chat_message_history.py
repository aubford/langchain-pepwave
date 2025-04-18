#!/usr/bin/env python
# coding: utf-8

# # MongoDB
# 
# >`MongoDB` is a source-available cross-platform document-oriented database program. Classified as a NoSQL database program, `MongoDB` uses `JSON`-like documents with optional schemas.
# >
# >`MongoDB` is developed by MongoDB Inc. and licensed under the Server Side Public License (SSPL). - [Wikipedia](https://en.wikipedia.org/wiki/MongoDB)
# 
# This notebook goes over how to use the `MongoDBChatMessageHistory` class to store chat message history in a Mongodb database.
# 

# ## Setup
# 
# The integration lives in the `langchain-mongodb` package, so we need to install that.
# 
# ```bash
# pip install -U --quiet langchain-mongodb
# ```

# It's also helpful (but not needed) to set up [LangSmith](https://smith.langchain.com/) for best-in-class observability

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ## Usage
# 
# To use the storage you need to provide only 2 things:
# 
# 1. Session Id - a unique identifier of the session, like user name, email, chat id etc.
# 2. Connection string - a string that specifies the database connection. It will be passed to MongoDB create_engine function.
# 
# If you want to customize where the chat histories go, you can also pass:
# 1. *database_name* - name of the database to use
# 1. *collection_name* - collection to use within that database

# In[3]:


from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory

chat_message_history = MongoDBChatMessageHistory(
    session_id="test_session",
    connection_string="mongodb://mongo_user:password123@mongo:27017",
    database_name="my_db",
    collection_name="chat_histories",
)

chat_message_history.add_user_message("Hello")
chat_message_history.add_ai_message("Hi")


# In[4]:


chat_message_history.messages


# ## Chaining
# 
# We can easily combine this message history class with [LCEL Runnables](/docs/how_to/message_history)
# 
# To do this we will want to use OpenAI, so we need to install that.  You will also need to set the OPENAI_API_KEY environment variable to your OpenAI key.
# 

# In[5]:


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


# In[16]:


import os

assert os.environ[
    "OPENAI_API_KEY"
], "Set the OPENAI_API_KEY environment variable with your OpenAI API key."


# In[10]:


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI()


# In[11]:


chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string="mongodb://mongo_user:password123@mongo:27017",
        database_name="my_db",
        collection_name="chat_histories",
    ),
    input_messages_key="question",
    history_messages_key="history",
)


# In[12]:


# This is where we configure the session id
config = {"configurable": {"session_id": "<SESSION_ID>"}}


# In[13]:


chain_with_history.invoke({"question": "Hi! I'm bob"}, config=config)


# In[14]:


chain_with_history.invoke({"question": "Whats my name"}, config=config)

