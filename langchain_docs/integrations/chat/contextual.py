#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: ContextualAI
---
# # ChatContextual
# 
# This will help you getting started with Contextual AI's Grounded Language Model [chat models](/docs/concepts/chat_models/).
# 
# To learn more about Contextual AI, please visit our [documentation](https://docs.contextual.ai/).
# 
# This integration requires the `contextual-client` Python SDK. Learn more about it [here](https://github.com/ContextualAI/contextual-client-python).
# 
# ## Overview
# 
# This integration invokes Contextual AI's Grounded Language Model.
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatContextual](https://github.com/ContextualAI//langchain-contextual) | [langchain-contextual](https://pypi.org/project/langchain-contextual/) | ❌ | beta | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-contextual?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-contextual?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 
# 
# ## Setup
# 
# To access Contextual models you'll need to create a Contextual AI account, get an API key, and install the `langchain-contextual` integration package.
# 
# ### Credentials
# 
# Head to [app.contextual.ai](https://app.contextual.ai) to sign up to Contextual and generate an API key. Once you've done this set the CONTEXTUAL_AI_API_KEY environment variable:
# 

# In[ ]:


import getpass
import os

if not os.getenv("CONTEXTUAL_AI_API_KEY"):
    os.environ["CONTEXTUAL_AI_API_KEY"] = getpass.getpass(
        "Enter your Contextual API key: "
    )


# If you want to get automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation
# 
# The LangChain Contextual integration lives in the `langchain-contextual` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-contextual')


# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions.
# 
# The chat client can be instantiated with these following additional settings:
# 
# | Parameter | Type | Description | Default |
# |-----------|------|-------------|---------|
# | temperature | Optional[float] | The sampling temperature, which affects the randomness in the response. Note that higher temperature values can reduce groundedness. | 0 |
# | top_p | Optional[float] | A parameter for nucleus sampling, an alternative to temperature which also affects the randomness of the response. Note that higher top_p values can reduce groundedness. | 0.9 |
# | max_new_tokens | Optional[int] | The maximum number of tokens that the model can generate in the response. Minimum is 1 and maximum is 2048. | 1024 |

# In[ ]:


from langchain_contextual import ChatContextual

llm = ChatContextual(
    model="v1",  # defaults to `v1`
    api_key="",
    temperature=0,  # defaults to 0
    top_p=0.9,  # defaults to 0.9
    max_new_tokens=1024,  # defaults to 1024
)


# ## Invocation
# 
# The Contextual Grounded Language Model accepts additional `kwargs` when calling the `ChatContextual.invoke` method.
# 
# These additional inputs are:
# 
# | Parameter | Type | Description |
# |-----------|------|-------------|
# | knowledge | list[str] | Required: A list of strings of knowledge sources the grounded language model can use when generating a response. |
# | system_prompt | Optional[str] | Optional: Instructions the model should follow when generating responses. Note that we do not guarantee that the model follows these instructions exactly. |
# | avoid_commentary | Optional[bool] | Optional (Defaults to `False`): Flag to indicate whether the model should avoid providing additional commentary in responses. Commentary is conversational in nature and does not contain verifiable claims; therefore, commentary is not strictly grounded in available context. However, commentary may provide useful context which improves the helpfulness of responses. |

# In[ ]:


# include a system prompt (optional)
system_prompt = "You are a helpful assistant that uses all of the provided knowledge to answer the user's query to the best of your ability."

# provide your own knowledge from your knowledge-base here in an array of string
knowledge = [
    "There are 2 types of dogs in the world: good dogs and best dogs.",
    "There are 2 types of cats in the world: good cats and best cats.",
]

# create your message
messages = [
    ("human", "What type of cats are there in the world and what are the types?"),
]

# invoke the GLM by providing the knowledge strings, optional system prompt
# if you want to turn off the GLM's commentary, pass True to the `avoid_commentary` argument
ai_msg = llm.invoke(
    messages, knowledge=knowledge, system_prompt=system_prompt, avoid_commentary=True
)

print(ai_msg.content)


# ## Chaining
# 
# We can chain the Contextual Model with output parsers.

# In[ ]:


from langchain_core.output_parsers import StrOutputParser

chain = llm | StrOutputParser

chain.invoke(
    messages, knowledge=knowledge, systemp_prompt=system_prompt, avoid_commentary=True
)


# ## API reference
# 
# For detailed documentation of all ChatContextual features and configurations head to the Github page: https://github.com/ContextualAI//langchain-contextual
