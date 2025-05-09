#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Azure OpenAI
---
# # AzureChatOpenAI
# 
# This guide will help you get started with AzureOpenAI [chat models](/docs/concepts/chat_models). For detailed documentation of all AzureChatOpenAI features and configurations head to the [API reference](https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.azure.AzureChatOpenAI.html).
# 
# Azure OpenAI has several chat models. You can find information about their latest models and their costs, context windows, and supported input types in the [Azure docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models).
# 
# :::info Azure OpenAI vs OpenAI
# 
# Azure OpenAI refers to OpenAI models hosted on the [Microsoft Azure platform](https://azure.microsoft.com/en-us/products/ai-services/openai-service). OpenAI also provides its own model APIs. To access OpenAI services directly, use the [ChatOpenAI integration](/docs/integrations/chat/openai/).
# 
# :::
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/azure) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [AzureChatOpenAI](https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.azure.AzureChatOpenAI.html) | [langchain-openai](https://python.langchain.com/api_reference/openai/index.html) | ❌ | beta | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-openai?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-openai?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
# 
# ## Setup
# 
# To access AzureOpenAI models you'll need to create an Azure account, create a deployment of an Azure OpenAI model, get the name and endpoint for your deployment, get an Azure OpenAI API key, and install the `langchain-openai` integration package.
# 
# ### Credentials
# 
# Head to the [Azure docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cpython-new&pivots=programming-language-python) to create your deployment and generate an API key. Once you've done this set the AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables:

# In[ ]:


import getpass
import os

if "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
        "Enter your AzureOpenAI API key: "
    )
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://YOUR-ENDPOINT.openai.azure.com/"


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# The LangChain AzureOpenAI integration lives in the `langchain-openai` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-openai')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions.
# - Replace `azure_deployment` with the name of your deployment,
# - You can find the latest supported `api_version` here: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference.

# In[2]:


from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-35-turbo",  # or your deployment
    api_version="2023-06-01-preview",  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


# ## Invocation

# In[3]:


messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg


# In[4]:


print(ai_msg.content)


# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:

# In[5]:


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
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


# ## Specifying model version
# 
# Azure OpenAI responses contain `model_name` response metadata property, which is name of the model used to generate the response. However unlike native OpenAI responses, it does not contain the specific version of the model, which is set on the deployment in Azure. E.g. it does not distinguish between `gpt-35-turbo-0125` and `gpt-35-turbo-0301`. This makes it tricky to know which version of the model was used to generate the response, which as result can lead to e.g. wrong total cost calculation with `OpenAICallbackHandler`.
# 
# To solve this problem, you can pass `model_version` parameter to `AzureChatOpenAI` class, which will be added to the model name in the llm output. This way you can easily distinguish between different versions of the model.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# In[6]:


from langchain_community.callbacks import get_openai_callback

with get_openai_callback() as cb:
    llm.invoke(messages)
    print(
        f"Total Cost (USD): ${format(cb.total_cost, '.6f')}"
    )  # without specifying the model version, flat-rate 0.002 USD per 1k input and output tokens is used


# In[7]:


llm_0301 = AzureChatOpenAI(
    azure_deployment="gpt-35-turbo",  # or your deployment
    api_version="2023-06-01-preview",  # or your api version
    model_version="0301",
)
with get_openai_callback() as cb:
    llm_0301.invoke(messages)
    print(f"Total Cost (USD): ${format(cb.total_cost, '.6f')}")


# ## API reference
# 
# For detailed documentation of all AzureChatOpenAI features and configurations head to the API reference: https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.azure.AzureChatOpenAI.html
