#!/usr/bin/env python
# coding: utf-8

# # NVIDIA
# 
# This will help you getting started with NVIDIA [models](/docs/concepts/text_llms). For detailed documentation of all `NVIDIA` features and configurations head to the [API reference](https://python.langchain.com/api_reference/nvidia_ai_endpoints/llms/langchain_nvidia_ai_endpoints.chat_models.NVIDIA.html).
# 
# ## Overview
# The `langchain-nvidia-ai-endpoints` package contains LangChain integrations building applications with models on 
# NVIDIA NIM inference microservice. These models are optimized by NVIDIA to deliver the best performance on NVIDIA 
# accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single 
# command on NVIDIA accelerated infrastructure.
# 
# NVIDIA hosted deployments of NIMs are available to test on the [NVIDIA API catalog](https://build.nvidia.com/). After testing, 
# NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud, 
# giving enterprises ownership and full control of their IP and AI application.
# 
# NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog. 
# At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.
# 
# This example goes over how to use LangChain to interact with NVIDIA supported via the `NVIDIA` class.
# 
# For more information on accessing the llm models through this api, check out the [NVIDIA](https://python.langchain.com/docs/integrations/llms/nvidia_ai_endpoints/) documentation.
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [NVIDIA](https://python.langchain.com/api_reference/nvidia_ai_endpoints/llms/langchain_nvidia_ai_endpoints.chat_models.ChatNVIDIA.html) | [langchain_nvidia_ai_endpoints](https://python.langchain.com/api_reference/nvidia_ai_endpoints/index.html) | ✅ | beta | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain_nvidia_ai_endpoints?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain_nvidia_ai_endpoints?style=flat-square&label=%20) |
# 
# ### Model features
# | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | 
# 
# ## Setup
# 
# **To get started:**
# 
# 1. Create a free account with [NVIDIA](https://build.nvidia.com/), which hosts NVIDIA AI Foundation models.
# 
# 2. Click on your model of choice.
# 
# 3. Under `Input` select the `Python` tab, and click `Get API Key`. Then click `Generate Key`.
# 
# 4. Copy and save the generated key as `NVIDIA_API_KEY`. From there, you should have access to the endpoints.
# 
# ### Credentials
# 

# In[1]:


import getpass
import os

if not os.getenv("NVIDIA_API_KEY"):
    # Note: the API key should start with "nvapi-"
    os.environ["NVIDIA_API_KEY"] = getpass.getpass("Enter your NVIDIA API key: ")


# ### Installation
# 
# The LangChain NVIDIA AI Endpoints integration lives in the `langchain_nvidia_ai_endpoints` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-nvidia-ai-endpoints')


# ## Instantiation
# 
# See [LLM](/docs/how_to#llms) for full functionality.

# In[3]:


from langchain_nvidia_ai_endpoints import NVIDIA


# In[ ]:


llm = NVIDIA().bind(max_tokens=256)
llm


# ## Invocation

# In[5]:


prompt = "# Function that does quicksort written in Rust without comments:"


# In[ ]:


print(llm.invoke(prompt))


# ## Stream, Batch, and Async
# 
# These models natively support streaming, and as is the case with all LangChain LLMs they expose a batch method to handle concurrent requests, as well as async methods for invoke, stream, and batch. Below are a few examples.

# In[ ]:


for chunk in llm.stream(prompt):
    print(chunk, end="", flush=True)


# In[ ]:


llm.batch([prompt])


# In[ ]:


await llm.ainvoke(prompt)


# In[ ]:


async for chunk in llm.astream(prompt):
    print(chunk, end="", flush=True)


# In[ ]:


await llm.abatch([prompt])


# In[ ]:


async for chunk in llm.astream_log(prompt):
    print(chunk)


# In[ ]:


response = llm.invoke(
    "X_train, y_train, X_test, y_test = train_test_split(X, y, test_size=0.1) #Train a logistic regression model, predict the labels on the test set and compute the accuracy score"
)
print(response)


# ## Supported models
# 
# Querying `available_models` will still give you all of the other models offered by your API credentials.

# In[ ]:


NVIDIA.get_available_models()
# llm.get_available_models()


# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:

# In[ ]:


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)


# ## API reference
# 
# For detailed documentation of all `NVIDIA` features and configurations head to the API reference: https://python.langchain.com/api_reference/nvidia_ai_endpoints/llms/langchain_nvidia_ai_endpoints.llms.NVIDIA.html

# 
