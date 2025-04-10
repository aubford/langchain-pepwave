#!/usr/bin/env python
# coding: utf-8

# # Anyscale
# 
# [Anyscale](https://www.anyscale.com/) is a fully-managed [Ray](https://www.ray.io/) platform, on which you can build, deploy, and manage scalable AI and Python applications
# 
# This example goes over how to use LangChain to interact with [Anyscale Endpoint](https://app.endpoints.anyscale.com/). 

# In[ ]:


##Installing the langchain packages needed to use the integration
get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# In[ ]:


ANYSCALE_API_BASE = "..."
ANYSCALE_API_KEY = "..."
ANYSCALE_MODEL_NAME = "..."


# In[ ]:


import os

os.environ["ANYSCALE_API_BASE"] = ANYSCALE_API_BASE
os.environ["ANYSCALE_API_KEY"] = ANYSCALE_API_KEY


# In[ ]:


from langchain.chains import LLMChain
from langchain_community.llms import Anyscale
from langchain_core.prompts import PromptTemplate


# In[ ]:


template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# In[ ]:


llm = Anyscale(model_name=ANYSCALE_MODEL_NAME)


# In[ ]:


llm_chain = prompt | llm


# In[ ]:


question = "When was George Washington president?"

llm_chain.invoke({"question": question})


# With Ray, we can distribute the queries without asynchronized implementation. This not only applies to Anyscale LLM model, but to any other Langchain LLM models which do not have `_acall` or `_agenerate` implemented

# In[ ]:


prompt_list = [
    "When was George Washington president?",
    "Explain to me the difference between nuclear fission and fusion.",
    "Give me a list of 5 science fiction books I should read next.",
    "Explain the difference between Spark and Ray.",
    "Suggest some fun holiday ideas.",
    "Tell a joke.",
    "What is 2+2?",
    "Explain what is machine learning like I am five years old.",
    "Explain what is artifical intelligence.",
]


# In[ ]:


import ray


@ray.remote(num_cpus=0.1)
def send_query(llm, prompt):
    resp = llm.invoke(prompt)
    return resp


futures = [send_query.remote(llm, prompt) for prompt in prompt_list]
results = ray.get(futures)

