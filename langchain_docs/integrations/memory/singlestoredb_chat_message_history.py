#!/usr/bin/env python
# coding: utf-8

# # SingleStoreDB
# 
# This notebook goes over how to use SingleStoreDB to store chat message history.

# In[ ]:


from langchain_community.chat_message_histories import (
    SingleStoreDBChatMessageHistory,
)

history = SingleStoreDBChatMessageHistory(
    session_id="foo", host="root:pass@localhost:3306/db"
)

history.add_user_message("hi!")

history.add_ai_message("whats up?")


# In[ ]:


history.messages

