#!/usr/bin/env python
# coding: utf-8

# # Telegram
# 
# This notebook shows how to use the Telegram chat loader. This class helps map exported Telegram conversations to LangChain chat messages.
# 
# The process has three steps:
# 1. Export  the chat .txt file by copying chats from the Telegram app and pasting them in a file on your local computer
# 2. Create the `TelegramChatLoader` with the file path pointed to the json file or directory of JSON files
# 3. Call `loader.load()` (or `loader.lazy_load()`) to perform the conversion. Optionally use `merge_chat_runs` to combine message from the same sender in sequence, and/or `map_ai_messages` to convert messages from the specified sender to the "AIMessage" class.
# 
# ## 1. Create message dump
# 
# Currently (2023/08/23) this loader best supports json files in the format generated by exporting your chat history from the [Telegram Desktop App](https://desktop.telegram.org/).
# 
# **Important:** There are 'lite' versions of telegram such as "Telegram for MacOS" that lack the export functionality. Please make sure you use the correct app to export the file.
# 
# To make the export:
# 1. Download and open telegram desktop
# 2. Select a conversation
# 3. Navigate to the conversation settings (currently the three dots in the top right corner)
# 4. Click "Export Chat History"
# 5. Unselect photos and other media. Select "Machine-readable JSON" format to export.
# 
# An example is below: 

# In[1]:


get_ipython().run_cell_magic('writefile', 'telegram_conversation.json', '{\n "name": "Jiminy",\n "type": "personal_chat",\n "id": 5965280513,\n "messages": [\n  {\n   "id": 1,\n   "type": "message",\n   "date": "2023-08-23T13:11:23",\n   "date_unixtime": "1692821483",\n   "from": "Jiminy Cricket",\n   "from_id": "user123450513",\n   "text": "You better trust your conscience",\n   "text_entities": [\n    {\n     "type": "plain",\n     "text": "You better trust your conscience"\n    }\n   ]\n  },\n  {\n   "id": 2,\n   "type": "message",\n   "date": "2023-08-23T13:13:20",\n   "date_unixtime": "1692821600",\n   "from": "Batman & Robin",\n   "from_id": "user6565661032",\n   "text": "What did you just say?",\n   "text_entities": [\n    {\n     "type": "plain",\n     "text": "What did you just say?"\n    }\n   ]\n  }\n ]\n}\n')


# ## 2. Create the Chat Loader
# 
# All that's required is the file path. You can optionally specify the user name that maps to an ai message as well an configure whether to merge message runs.

# In[2]:


from langchain_community.chat_loaders.telegram import TelegramChatLoader


# In[3]:


loader = TelegramChatLoader(
    path="./telegram_conversation.json",
)


# ## 3. Load messages
# 
# The `load()` (or `lazy_load`) methods return a list of "ChatSessions" that currently just contain a list of messages per loaded conversation.

# In[4]:


from typing import List

from langchain_community.chat_loaders.utils import (
    map_ai_messages,
    merge_chat_runs,
)
from langchain_core.chat_sessions import ChatSession

raw_messages = loader.lazy_load()
# Merge consecutive messages from the same sender into a single message
merged_messages = merge_chat_runs(raw_messages)
# Convert messages from "Jiminy Cricket" to AI messages
messages: List[ChatSession] = list(
    map_ai_messages(merged_messages, sender="Jiminy Cricket")
)


# ### Next Steps
# 
# You can then use these messages how you see fit, such as fine-tuning a model, few-shot example selection, or directly make predictions for the next message  

# In[5]:


from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

for chunk in llm.stream(messages[0]["messages"]):
    print(chunk.content, end="", flush=True)

