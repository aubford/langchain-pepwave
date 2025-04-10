#!/usr/bin/env python
# coding: utf-8

# # Petals
# 
# `Petals` runs 100B+ language models at home, BitTorrent-style.
# 
# This notebook goes over how to use Langchain with [Petals](https://github.com/bigscience-workshop/petals).

# ## Install petals
# The `petals` package is required to use the Petals API. Install `petals` using `pip3 install petals`.
# 
# For Apple Silicon(M1/M2) users please follow this guide [https://github.com/bigscience-workshop/petals/issues/147#issuecomment-1365379642](https://github.com/bigscience-workshop/petals/issues/147#issuecomment-1365379642) to install petals 

# In[ ]:


get_ipython().system('pip3 install petals')


# ## Imports

# In[4]:


import os

from langchain.chains import LLMChain
from langchain_community.llms import Petals
from langchain_core.prompts import PromptTemplate


# ## Set the Environment API Key
# Make sure to get [your API key](https://huggingface.co/docs/api-inference/quicktour#get-your-api-token) from Huggingface.

# In[2]:


from getpass import getpass

HUGGINGFACE_API_KEY = getpass()


# In[5]:


os.environ["HUGGINGFACE_API_KEY"] = HUGGINGFACE_API_KEY


# ## Create the Petals instance
# You can specify different parameters such as the model name, max new tokens, temperature, etc.

# In[ ]:


# this can take several minutes to download big files!

llm = Petals(model_name="bigscience/bloom-petals")


# ## Create a Prompt Template
# We will create a prompt template for Question and Answer.

# In[ ]:


template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# ## Initiate the LLMChain

# In[ ]:


llm_chain = LLMChain(prompt=prompt, llm=llm)


# ## Run the LLMChain
# Provide a question and run the LLMChain.

# In[ ]:


question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"

llm_chain.run(question)

