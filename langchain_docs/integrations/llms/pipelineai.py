#!/usr/bin/env python
# coding: utf-8

# # PipelineAI
# 
# >[PipelineAI](https://pipeline.ai) allows you to run your ML models at scale in the cloud. It also provides API access to [several LLM models](https://pipeline.ai).
# 
# This notebook goes over how to use Langchain with [PipelineAI](https://docs.pipeline.ai/docs).
# 
# ## PipelineAI example
# 
# [This example shows how PipelineAI integrated with LangChain](https://docs.pipeline.ai/docs/langchain) and it is created by PipelineAI.

# ## Setup
# The `pipeline-ai` library is required to use the `PipelineAI` API, AKA `Pipeline Cloud`. Install `pipeline-ai` using `pip install pipeline-ai`.

# In[ ]:


# Install the package
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  pipeline-ai')


# ## Example
# 
# ### Imports

# In[ ]:


import os

from langchain_community.llms import PipelineAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


# ### Set the Environment API Key
# Make sure to get your API key from PipelineAI. Check out the [cloud quickstart guide](https://docs.pipeline.ai/docs/cloud-quickstart). You'll be given a 30 day free trial with 10 hours of serverless GPU compute to test different models.

# In[ ]:


os.environ["PIPELINE_API_KEY"] = "YOUR_API_KEY_HERE"


# ## Create the PipelineAI instance
# When instantiating PipelineAI, you need to specify the id or tag of the pipeline you want to use, e.g. `pipeline_key = "public/gpt-j:base"`. You then have the option of passing additional pipeline-specific keyword arguments:

# In[ ]:


llm = PipelineAI(pipeline_key="YOUR_PIPELINE_KEY", pipeline_kwargs={...})


# ### Create a Prompt Template
# We will create a prompt template for Question and Answer.

# In[ ]:


template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)


# ### Initiate the LLMChain

# In[ ]:


llm_chain = prompt | llm | StrOutputParser()


# ### Run the LLMChain
# Provide a question and run the LLMChain.

# In[ ]:


question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"

llm_chain.invoke(question)

