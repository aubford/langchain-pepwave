#!/usr/bin/env python
# coding: utf-8

# # Dappier AI

# **Dappier: Powering AI with Dynamic, Real-Time Data Models**
# 
# Dappier offers a cutting-edge platform that grants developers immediate access to a wide array of real-time data models spanning news, entertainment, finance, market data, weather, and beyond. With our pre-trained data models, you can supercharge your AI applications, ensuring they deliver precise, up-to-date responses and minimize inaccuracies.
# 
# Dappier data models help you build next-gen LLM apps with trusted, up-to-date content from the world's leading brands. Unleash your creativity and enhance any GPT App or AI workflow with actionable, proprietary, data through a simple API. Augment your AI with proprietary data from trusted sources is the best way to ensure factual, up-to-date, responses with fewer hallucinations no matter the question.
# 
# For Developers, By Developers
# Designed with developers in mind, Dappier simplifies the journey from data integration to monetization, providing clear, straightforward paths to deploy and earn from your AI models. Experience the future of monetization infrastructure for the new internet at **https://dappier.com/**.

# This example goes over how to use LangChain to interact with Dappier AI models
# 
# -----------------------------------------------------------------------------------

# To use one of our Dappier AI Data Models, you will need an API key. Please visit Dappier Platform (https://platform.dappier.com/) to log in and create an API key in your profile.
# 
# 
# You can find more details on the API reference : https://docs.dappier.com/introduction

# To work with our Dappier Chat Model you can pass the key directly through the parameter named dappier_api_key when initiating the class
# or set as an environment variable.
# 
# ```bash
# export DAPPIER_API_KEY="..."
# ```
# 

# In[2]:


from langchain_community.chat_models.dappier import ChatDappierAI
from langchain_core.messages import HumanMessage


# In[7]:


chat = ChatDappierAI(
    dappier_endpoint="https://api.dappier.com/app/datamodelconversation",
    dappier_model="dm_01hpsxyfm2fwdt2zet9cg6fdxt",
    dappier_api_key="...",
)


# In[8]:


messages = [HumanMessage(content="Who won the super bowl in 2024?")]
chat.invoke(messages)


# In[9]:


await chat.ainvoke(messages)


# In[ ]:





# In[ ]:




