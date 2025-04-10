#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Xinference
---
# # ChatXinference
# 
# [Xinference](https://github.com/xorbitsai/inference) is a powerful and versatile library designed to serve LLMs, 
# speech recognition models, and multimodal models, even on your laptop. It supports a variety of models compatible with GGML, such as chatglm, baichuan, whisper, vicuna, orca, and many others.
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support] | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | ChatXinference| langchain-xinference | ✅ | ❌ | ✅ | ✅ | ✅ |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling/) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: |:----------------------------------------------------:| :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ |                          ✅                           | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
# 
# ## Setup
# 
# Install `Xinference` through PyPI:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  "xinference[all]"')


# ### Deploy Xinference Locally or in a Distributed Cluster.
# 
# For local deployment, run `xinference`. 
# 
# To deploy Xinference in a cluster, first start an Xinference supervisor using the `xinference-supervisor`. You can also use the option -p to specify the port and -H to specify the host. The default port is 8080 and the default host is 0.0.0.0.
# 
# Then, start the Xinference workers using `xinference-worker` on each server you want to run them on. 
# 
# You can consult the README file from [Xinference](https://github.com/xorbitsai/inference) for more information.
# ### Wrapper
# 
# To use Xinference with LangChain, you need to first launch a model. You can use command line interface (CLI) to do so:

# In[13]:


get_ipython().run_line_magic('xinference', 'launch -n vicuna-v1.3 -f ggmlv3 -q q4_0')


# A model UID is returned for you to use. Now you can use Xinference with LangChain:

# ## Installation
# 
# The LangChain Xinference integration lives in the `langchain-xinference` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-xinference')


# Make sure you're using the latest Xinference version for structured outputs.

# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:
# 

# In[9]:


from langchain_xinference.chat_models import ChatXinference

llm = ChatXinference(
    server_url="your_server_url", model_uid="7167b2b0-2a04-11ee-83f0-d29396a3f064"
)

llm.invoke(
    "Q: where can we visit in the capital of France?",
    config={"max_tokens": 1024},
)


# ## Invocation

# In[10]:


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_xinference.chat_models import ChatXinference

llm = ChatXinference(
    server_url="your_server_url", model_uid="7167b2b0-2a04-11ee-83f0-d29396a3f064"
)

system_message = "You are a helpful assistant that translates English to French. Translate the user sentence."
human_message = "I love programming."

llm.invoke([HumanMessage(content=human_message), SystemMessage(content=system_message)])


# ## Chaining
# 
# We can [chain](/docs/how_to/sequence/) our model with a prompt template like so:

# In[12]:


from langchain.prompts import PromptTemplate
from langchain_xinference.chat_models import ChatXinference

prompt = PromptTemplate(
    input=["country"], template="Q: where can we visit in the capital of {country}? A:"
)

llm = ChatXinference(
    server_url="your_server_url", model_uid="7167b2b0-2a04-11ee-83f0-d29396a3f064"
)

chain = prompt | llm
chain.invoke(input={"country": "France"})
chain.stream(input={"country": "France"})


# ## API reference
# 
# For detailed documentation of all ChatXinference features and configurations head to the API reference: https://github.com/TheSongg/langchain-xinference
