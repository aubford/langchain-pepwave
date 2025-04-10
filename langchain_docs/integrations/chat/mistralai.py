#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: MistralAI
---
# # ChatMistralAI
# 
# This will help you getting started with Mistral [chat models](/docs/concepts/chat_models). For detailed documentation of all `ChatMistralAI` features and configurations head to the [API reference](https://python.langchain.com/api_reference/mistralai/chat_models/langchain_mistralai.chat_models.ChatMistralAI.html). The `ChatMistralAI` class is built on top of the [Mistral API](https://docs.mistral.ai/api/). For a list of all the models supported by Mistral, check out [this page](https://docs.mistral.ai/getting-started/models/).
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/mistral) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatMistralAI](https://python.langchain.com/api_reference/mistralai/chat_models/langchain_mistralai.chat_models.ChatMistralAI.html) | [langchain_mistralai](https://python.langchain.com/api_reference/mistralai/index.html) | ❌ | beta | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain_mistralai?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain_mistralai?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
# 
# ## Setup
# 
# 
# To access `ChatMistralAI` models you'll need to create a Mistral account, get an API key, and install the `langchain_mistralai` integration package.
# 
# ### Credentials
# 
# 
# A valid [API key](https://console.mistral.ai/api-keys/) is needed to communicate with the API. Once you've done this set the MISTRAL_API_KEY environment variable:

# In[ ]:


import getpass
import os

if "MISTRAL_API_KEY" not in os.environ:
    os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your Mistral API key: ")


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# The LangChain Mistral integration lives in the `langchain_mistralai` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain_mistralai')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[5]:


from langchain_mistralai import ChatMistralAI

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
    # other params...
)


# ## Invocation

# In[6]:


messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg


# In[7]:


print(ai_msg.content)


# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:

# In[8]:


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


# ## API reference
# 
# Head to the [API reference](https://python.langchain.com/api_reference/mistralai/chat_models/langchain_mistralai.chat_models.ChatMistralAI.html) for detailed documentation of all attributes and methods.
