#!/usr/bin/env python
# coding: utf-8

# # OctoAI
# 
# [OctoAI](https://docs.octoai.cloud/docs) offers easy access to efficient compute and enables users to integrate their choice of AI models into applications. The `OctoAI` compute service helps you run, tune, and scale AI applications easily.
# 
# This example goes over how to use LangChain to interact with `OctoAI` [LLM endpoints](https://octoai.cloud/templates)
# 
# ## Setup
# 
# To run our example app, there are two simple steps to take:
# 
# 1. Get an API Token from [your OctoAI account page](https://octoai.cloud/settings).
#    
# 2. Paste your API key in in the code cell below.
# 
# Note: If you want to use a different LLM model, you can containerize the model and make a custom OctoAI endpoint yourself, by following [Build a Container from Python](https://octo.ai/docs/bring-your-own-model/advanced-build-a-container-from-scratch-in-python) and [Create a Custom Endpoint from a Container](https://octo.ai/docs/bring-your-own-model/create-custom-endpoints-from-a-container/create-custom-endpoints-from-a-container) and then updating your `OCTOAI_API_BASE` environment variable.
# 

# In[6]:


import os

os.environ["OCTOAI_API_TOKEN"] = "OCTOAI_API_TOKEN"


# In[7]:


from langchain.chains import LLMChain
from langchain_community.llms.octoai_endpoint import OctoAIEndpoint
from langchain_core.prompts import PromptTemplate


# ## Example

# In[8]:


template = """Below is an instruction that describes a task. Write a response that appropriately completes the request.\n Instruction:\n{question}\n Response: """
prompt = PromptTemplate.from_template(template)


# In[9]:


llm = OctoAIEndpoint(
    model_name="llama-2-13b-chat-fp16",
    max_tokens=200,
    presence_penalty=0,
    temperature=0.1,
    top_p=0.9,
)


# In[ ]:


question = "Who was Leonardo da Vinci?"

chain = prompt | llm

print(chain.invoke(question))


# Leonardo da Vinci was a true Renaissance man. He was born in 1452 in Vinci, Italy and was known for his work in various fields, including art, science, engineering, and mathematics. He is considered one of the greatest painters of all time, and his most famous works include the Mona Lisa and The Last Supper. In addition to his art, da Vinci made significant contributions to engineering and anatomy, and his designs for machines and inventions were centuries ahead of his time. He is also known for his extensive journals and drawings, which provide valuable insights into his thoughts and ideas. Da Vinci's legacy continues to inspire and influence artists, scientists, and thinkers around the world today.
