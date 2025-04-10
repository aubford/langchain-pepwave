#!/usr/bin/env python
# coding: utf-8

# # PromptLayer OpenAI
# 
# `PromptLayer` is the first platform that allows you to track, manage, and share your GPT prompt engineering. `PromptLayer` acts a middleware between your code and `OpenAI’s` python library.
# 
# `PromptLayer` records all your `OpenAI API` requests, allowing you to search and explore request history in the `PromptLayer` dashboard.
# 
# 
# This example showcases how to connect to [PromptLayer](https://www.promptlayer.com) to start recording your OpenAI requests.
# 
# Another example is [here](/docs/integrations/providers/promptlayer).

# ## Install PromptLayer
# The `promptlayer` package is required to use PromptLayer with OpenAI. Install `promptlayer` using pip.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  promptlayer')


# ## Imports

# In[3]:


import os

import promptlayer
from langchain_community.llms import PromptLayerOpenAI


# ## Set the Environment API Key
# You can create a PromptLayer API Key at [www.promptlayer.com](https://www.promptlayer.com) by clicking the settings cog in the navbar.
# 
# Set it as an environment variable called `PROMPTLAYER_API_KEY`.
# 
# You also need an OpenAI Key, called `OPENAI_API_KEY`.

# In[2]:


from getpass import getpass

PROMPTLAYER_API_KEY = getpass()


# In[9]:


os.environ["PROMPTLAYER_API_KEY"] = PROMPTLAYER_API_KEY


# In[6]:


from getpass import getpass

OPENAI_API_KEY = getpass()


# In[7]:


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# ## Use the PromptLayerOpenAI LLM like normal
# *You can optionally pass in `pl_tags` to track your requests with PromptLayer's tagging feature.*

# In[ ]:


llm = PromptLayerOpenAI(pl_tags=["langchain"])
llm("I am a cat and I want")


# **The above request should now appear on your [PromptLayer dashboard](https://www.promptlayer.com).**

# ## Using PromptLayer Track
# If you would like to use any of the [PromptLayer tracking features](https://magniv.notion.site/Track-4deee1b1f7a34c1680d085f82567dab9), you need to pass the argument `return_pl_id` when instantiating the PromptLayer LLM to get the request id.  

# In[ ]:


llm = PromptLayerOpenAI(return_pl_id=True)
llm_results = llm.generate(["Tell me a joke"])

for res in llm_results.generations:
    pl_request_id = res[0].generation_info["pl_request_id"]
    promptlayer.track.score(request_id=pl_request_id, score=100)


# Using this allows you to track the performance of your model in the PromptLayer dashboard. If you are using a prompt template, you can attach a template to a request as well.
# Overall, this gives you the opportunity to track the performance of different templates and models in the PromptLayer dashboard.
