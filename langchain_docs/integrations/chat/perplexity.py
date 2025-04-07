#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Perplexity
---
# # ChatPerplexity
# 
# 
# This page will help you get started with Perplexity [chat models](../../concepts/chat_models.mdx). For detailed documentation of all `ChatPerplexity` features and configurations head to the [API reference](https://python.langchain.com/api_reference/perplexity/chat_models/langchain_perplexity.chat_models.ChatPerplexity.html).
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/xai) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatPerplexity](https://python.langchain.com/api_reference/perplexity/chat_models/langchain_perplexity.chat_models.ChatPerplexity.html) | [langchain-perplexity](https://python.langchain.com/api_reference/perplexity/perplexity.html) | ❌ | beta | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-perplexity?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-perplexity?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](../../how_to/tool_calling.ipynb) | [Structured output](../../how_to/structured_output.ipynb) | JSON mode | [Image input](../../how_to/multimodal_inputs.ipynb) | Audio input | Video input | [Token-level streaming](../../how_to/chat_streaming.ipynb) | Native async | [Token usage](../../how_to/chat_token_usage_tracking.ipynb) | [Logprobs](../../how_to/logprobs.ipynb) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |
# 
# ## Setup
# 
# To access Perplexity models you'll need to create a Perplexity account, get an API key, and install the `langchain-perplexity` integration package.
# 
# ### Credentials
# 
# Head to [this page](https://www.perplexity.ai/) to sign up for Perplexity and generate an API key. Once you've done this set the `PPLX_API_KEY` environment variable:

# In[ ]:


import getpass
import os

if "PPLX_API_KEY" not in os.environ:
    os.environ["PPLX_API_KEY"] = getpass.getpass("Enter your Perplexity API key: ")


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# In[ ]:


from langchain_core.prompts import ChatPromptTemplate
from langchain_perplexity import ChatPerplexity


# The code provided assumes that your PPLX_API_KEY is set in your environment variables. If you would like to manually specify your API key and also choose a different model, you can use the following code:

# In[ ]:


chat = ChatPerplexity(
    temperature=0, pplx_api_key="YOUR_API_KEY", model="llama-3-sonar-small-32k-online"
)


# You can check a list of available models [here](https://docs.perplexity.ai/docs/model-cards). For reproducibility, we can set the API key dynamically by taking it as an input in this notebook.

# In[3]:


chat = ChatPerplexity(temperature=0, model="llama-3.1-sonar-small-128k-online")


# In[4]:


system = "You are a helpful assistant."
human = "{input}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | chat
response = chain.invoke({"input": "Why is the Higgs Boson important?"})
response.content


# You can format and structure the prompts like you would typically. In the following example, we ask the model to tell us a joke about cats.

# In[5]:


chat = ChatPerplexity(temperature=0, model="llama-3.1-sonar-small-128k-online")
prompt = ChatPromptTemplate.from_messages([("human", "Tell me a joke about {topic}")])
chain = prompt | chat
response = chain.invoke({"topic": "cats"})
response.content


# ## Using Perplexity-specific parameters through `ChatPerplexity`
# 
# You can also use Perplexity-specific parameters through the ChatPerplexity class. For example, parameters like search_domain_filter, return_images, return_related_questions or search_recency_filter using the extra_body parameter as shown below:

# In[ ]:


chat = ChatPerplexity(temperature=0.7, model="llama-3.1-sonar-small-128k-online")
response = chat.invoke(
    "Tell me a joke about cats", extra_body={"search_recency_filter": "week"}
)
response.content


# ## `ChatPerplexity` also supports streaming functionality:

# In[6]:


chat = ChatPerplexity(temperature=0.7, model="llama-3.1-sonar-small-128k-online")

for chunk in chat.stream("Give me a list of famous tourist attractions in Pakistan"):
    print(chunk.content, end="", flush=True)


# ## `ChatPerplexity` Supports Structured Outputs for Tier 3+ Users

# In[6]:


from pydantic import BaseModel


class AnswerFormat(BaseModel):
    first_name: str
    last_name: str
    year_of_birth: int
    num_seasons_in_nba: int


chat = ChatPerplexity(temperature=0.7, model="sonar-pro")
structured_chat = chat.with_structured_output(AnswerFormat)
response = structured_chat.invoke(
    "Tell me about Michael Jordan. Return your answer "
    "as JSON with keys first_name (str), last_name (str), "
    "year_of_birth (int), and num_seasons_in_nba (int)."
)
response

