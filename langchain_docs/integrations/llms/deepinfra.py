#!/usr/bin/env python
# coding: utf-8

# # DeepInfra
# 
# [DeepInfra](https://deepinfra.com/?utm_source=langchain) is a serverless inference as a service that provides access to a [variety of LLMs](https://deepinfra.com/models?utm_source=langchain) and [embeddings models](https://deepinfra.com/models?type=embeddings&utm_source=langchain). This notebook goes over how to use LangChain with DeepInfra for language models.

# ## Set the Environment API Key
# Make sure to get your API key from DeepInfra. You have to [Login](https://deepinfra.com/login?from=%2Fdash) and get a new token.
# 
# You are given a 1 hour free of serverless GPU compute to test different models. (see [here](https://github.com/deepinfra/deepctl#deepctl))
# You can print your token with `deepctl auth token`

# In[6]:


# get a new token: https://deepinfra.com/login?from=%2Fdash

from getpass import getpass

DEEPINFRA_API_TOKEN = getpass()


# In[7]:


import os

os.environ["DEEPINFRA_API_TOKEN"] = DEEPINFRA_API_TOKEN


# ## Create the DeepInfra instance
# You can also use our open-source [deepctl tool](https://github.com/deepinfra/deepctl#deepctl) to manage your model deployments. You can view a list of available parameters [here](https://deepinfra.com/databricks/dolly-v2-12b#API).

# In[18]:


from langchain_community.llms import DeepInfra

llm = DeepInfra(model_id="meta-llama/Llama-2-70b-chat-hf")
llm.model_kwargs = {
    "temperature": 0.7,
    "repetition_penalty": 1.2,
    "max_new_tokens": 250,
    "top_p": 0.9,
}


# In[14]:


# run inferences directly via wrapper
llm("Who let the dogs out?")


# In[15]:


# run streaming inference
for chunk in llm.stream("Who let the dogs out?"):
    print(chunk)


# ## Create a Prompt Template
# We will create a prompt template for Question and Answer.

# In[16]:


from langchain_core.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# ## Initiate the LLMChain

# In[21]:


from langchain.chains import LLMChain

llm_chain = LLMChain(prompt=prompt, llm=llm)


# ## Run the LLMChain
# Provide a question and run the LLMChain.

# In[22]:


question = "Can penguins reach the North pole?"

llm_chain.run(question)


# In[ ]:




