#!/usr/bin/env python
# coding: utf-8

# # WhatsApp Chat
# 
# >[WhatsApp](https://www.whatsapp.com/) (also called `WhatsApp Messenger`) is a freeware, cross-platform, centralized instant messaging (IM) and voice-over-IP (VoIP) service. It allows users to send text and voice messages, make voice and video calls, and share images, documents, user locations, and other content.
# 
# This notebook covers how to load data from the `WhatsApp Chats` into a format that can be ingested into LangChain.

# In[1]:


from langchain_community.document_loaders import WhatsAppChatLoader


# In[2]:


loader = WhatsAppChatLoader("example_data/whatsapp_chat.txt")


# In[ ]:


loader.load()

