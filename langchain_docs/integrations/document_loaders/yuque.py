#!/usr/bin/env python
# coding: utf-8

# # Yuque
# 
# >[Yuque](https://www.yuque.com/) is a professional cloud-based knowledge base for team collaboration in documentation.
# 
# This notebook covers how to load documents from `Yuque`.
# 
# You can obtain the personal access token by clicking on your personal avatar in the [Personal Settings](https://www.yuque.com/settings/tokens) page.

# In[1]:


from langchain_community.document_loaders import YuqueLoader


# In[2]:


loader = YuqueLoader(access_token="<your_personal_access_token>")


# In[ ]:


docs = loader.load()

