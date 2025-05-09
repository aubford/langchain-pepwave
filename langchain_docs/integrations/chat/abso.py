#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Abso
---
# # ChatAbso
# 
# This will help you getting started with ChatAbso [chat models](https://python.langchain.com/docs/concepts/chat_models/). For detailed documentation of all ChatAbso features and configurations head to the [API reference](https://python.langchain.com/api_reference/en/latest/chat_models/langchain_abso.chat_models.ChatAbso.html).
# 
# - You can find the full documentation for the Abso router [here] (https://abso.ai)
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/abso) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatAbso](https://python.langchain.com/api_reference/en/latest/chat_models/langchain_abso.chat_models.ChatAbso.html) | [langchain-abso](https://python.langchain.com/api_reference/en/latest/abso_api_reference.html) | ❌ | ❌ | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-abso?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-abso?style=flat-square&label=%20) |
# 
# ## Setup
# To access ChatAbso models you'll need to create an OpenAI account, get an API key, and install the `langchain-abso` integration package.
# 
# ### Credentials
# 
# - TODO: Update with relevant info.
# 
# Head to (TODO: link) to sign up to ChatAbso and generate an API key. Once you've done this set the ABSO_API_KEY environment variable:

# In[ ]:


import getpass
import os

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


# ### Installation
# 
# The LangChain ChatAbso integration lives in the `langchain-abso` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-abso')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[ ]:


from langchain_abso import ChatAbso

llm = ChatAbso(fast_model="gpt-4o", slow_model="o3-mini")


# ## Invocation
# 

# In[ ]:


messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg


# In[ ]:


print(ai_msg.content)


# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:
# 

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
# For detailed documentation of all ChatAbso features and configurations head to the API reference: https://python.langchain.com/api_reference/en/latest/chat_models/langchain_abso.chat_models.ChatAbso.html
