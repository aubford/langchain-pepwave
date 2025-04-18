#!/usr/bin/env python
# coding: utf-8

# # OpenLM
# [OpenLM](https://github.com/r2d4/openlm) is a zero-dependency OpenAI-compatible LLM provider that can call different inference endpoints directly via HTTP. 
# 
# 
# It implements the OpenAI Completion class so that it can be used as a drop-in replacement for the OpenAI API. This changeset utilizes BaseOpenAI for minimal added code.
# 
# This examples goes over how to use LangChain to interact with both OpenAI and HuggingFace. You'll need API keys from both.

# ### Setup
# Install dependencies and set API keys.

# In[1]:


# Uncomment to install openlm and openai if you haven't already

get_ipython().run_line_magic('pip', 'install --upgrade --quiet  openlm')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-openai')


# In[2]:


import os
from getpass import getpass

# Check if OPENAI_API_KEY environment variable is set
if "OPENAI_API_KEY" not in os.environ:
    print("Enter your OpenAI API key:")
    os.environ["OPENAI_API_KEY"] = getpass()

# Check if HF_API_TOKEN environment variable is set
if "HF_API_TOKEN" not in os.environ:
    print("Enter your HuggingFace Hub API key:")
    os.environ["HF_API_TOKEN"] = getpass()


# ### Using LangChain with OpenLM
# 
# Here we're going to call two models in an LLMChain, `text-davinci-003` from OpenAI and `gpt2` on HuggingFace.

# In[4]:


from langchain.chains import LLMChain
from langchain_community.llms import OpenLM
from langchain_core.prompts import PromptTemplate


# In[5]:


question = "What is the capital of France?"
template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)

for model in ["text-davinci-003", "huggingface.co/gpt2"]:
    llm = OpenLM(model=model)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    result = llm_chain.run(question)
    print(
        """Model: {}
Result: {}""".format(model, result)
    )

