#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: AzureAIChatCompletionsModel
---
# # AzureAIChatCompletionsModel
# 
# This will help you getting started with AzureAIChatCompletionsModel [chat models](/docs/concepts/chat_models). For detailed documentation of all AzureAIChatCompletionsModel features and configurations head to the [API reference](https://python.langchain.com/api_reference/azure_ai/chat_models/langchain_azure_ai.chat_models.AzureAIChatCompletionsModel.html)
# 
# The AzureAIChatCompletionsModel class uses the Azure AI Foundry SDK. AI Foundry has several chat models including AzureOpenAI, Cohere, Llama, Phi-3/4, and DeepSeek-R1 to name a few. You can find information about their latest models and their costs, context windows, and supported input types in the [Azure docs](https://learn.microsoft.com/azure/ai-studio/how-to/model-catalog-overview).
# 
# 
# ## Overview
# ### Integration details
# 
# 
# | Class | Package | Local | Serializable | [JS support](https://v03.api.js.langchain.com/classes/_langchain_openai.AzureChatOpenAI.html) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [AzureAIChatCompletionsModel](https://python.langchain.com/api_reference/azure_ai/chat_models/langchain_azure_ai.chat_models.AzureAIChatCompletionsModel.html) | [langchain-azure-ai](https://python.langchain.com/api_reference/langchain_azure_ai/index.html) | ❌ | ✅ | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-azure-ai?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-azure-ai?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅| 
# 
# ## Setup
# 
# To access AzureAIChatCompletionsModel models you'll need to create an [Azure account](https://azure.microsoft.com/pricing/purchase-options/azure-account), get an API key, and install the `langchain-azure-ai` integration package.
# 
# ### Credentials
# 
# 
# Head to the [Azure docs](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python) to see how to create your deployment and generate an API key. Once your model is deployed you click the 'get endpoint' button in AI Foundry. This will show you your endpoint and api key. Once you've done this set the AZURE_INFERENCE_CREDENTIAL and AZURE_INFERENCE_ENDPOINT environment variables:

# In[1]:


import getpass
import os

if not os.getenv("AZURE_INFERENCE_CREDENTIAL"):
    os.environ["AZURE_INFERENCE_CREDENTIAL"] = getpass.getpass(
        "Enter your AzureAIChatCompletionsModel API key: "
    )

if not os.getenv("AZURE_INFERENCE_ENDPOINT"):
    os.environ["AZURE_INFERENCE_ENDPOINT"] = getpass.getpass(
        "Enter your model endpoint: "
    )


# If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain AzureAIChatCompletionsModel integration lives in the `langchain-azure-ai` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-azure-ai')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[2]:


from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

llm = AzureAIChatCompletionsModel(
    model_name="gpt-4",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
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
# For detailed documentation of all AzureAIChatCompletionsModel features and configurations head to the API reference: https://python.langchain.com/api_reference/azure_ai/chat_models/langchain_azure_ai.chat_models.AzureAIChatCompletionsModel.html
