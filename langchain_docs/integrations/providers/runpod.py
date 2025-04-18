#!/usr/bin/env python
# coding: utf-8

# # Runpod
# 
# [RunPod](https://www.runpod.io/) provides GPU cloud infrastructure, including Serverless endpoints optimized for deploying and scaling AI models.
# 
# This guide covers how to use the `langchain-runpod` integration package to connect LangChain applications to models hosted on [RunPod Serverless](https://www.runpod.io/serverless-gpu).
# 
# The integration offers interfaces for both standard Language Models (LLMs) and Chat Models.

# ## Intstallation
# 
# Install the dedicated partner package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-runpod')


# ## Setup
# ### 1. Deploy an Endpoint on RunPod
# - Navigate to your [RunPod Serverless Console](https://www.runpod.io/console/serverless/user/endpoints).
# - Create a \"New Endpoint\", selecting an appropriate GPU and template (e.g., vLLM, TGI, text-generation-webui) compatible with your model and the expected input/output format (see component guides or the package [README](https://github.com/runpod/langchain-runpod)).
# - Configure settings and deploy.
# - **Crucially, copy the Endpoint ID** after deployment.

# ### 2. Set API Credentials
# The integration needs your RunPod API Key and the Endpoint ID. Set them as environment variables for secure access:

# In[ ]:


import getpass
import os

os.environ["RUNPOD_API_KEY"] = getpass.getpass("Enter your RunPod API Key: ")
os.environ["RUNPOD_ENDPOINT_ID"] = input("Enter your RunPod Endpoint ID: ")


# *(Optional)* If using different endpoints for LLM and Chat models, you might need to set `RUNPOD_CHAT_ENDPOINT_ID` or pass the ID directly during initialization.

# ## Components
# This package provides two main components:

# ### 1. LLM
# 
# For interacting with standard text completion models.
# 
# See the [RunPod LLM Integration Guide](/docs/integrations/llms/runpod) for detailed usage

# In[ ]:


from langchain_runpod import RunPod

# Example initialization (uses environment variables)
llm = RunPod(model_kwargs={"max_new_tokens": 100})  # Add generation params here

# Example Invocation
try:
    response = llm.invoke("Write a short poem about the cloud.")
    print(response)
except Exception as e:
    print(
        f"Error invoking LLM: {e}. Ensure endpoint ID and API key are correct and endpoint is active."
    )


# ### 2. Chat Model
# 
# For interacting with conversational models.
# 
# See the [RunPod Chat Model Integration Guide](/docs/integrations/chat/runpod) for detailed usage and feature support.

# In[ ]:


from langchain_core.messages import HumanMessage
from langchain_runpod import ChatRunPod

# Example initialization (uses environment variables)
chat = ChatRunPod(model_kwargs={"temperature": 0.8})  # Add generation params here

# Example Invocation
try:
    response = chat.invoke(
        [HumanMessage(content="Explain RunPod Serverless in one sentence.")]
    )
    print(response.content)
except Exception as e:
    print(
        f"Error invoking Chat Model: {e}. Ensure endpoint ID and API key are correct and endpoint is active."
    )

