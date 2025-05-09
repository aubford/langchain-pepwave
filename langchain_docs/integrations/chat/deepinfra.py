#!/usr/bin/env python
# coding: utf-8

# # DeepInfra
# 
# [DeepInfra](https://deepinfra.com/?utm_source=langchain) is a serverless inference as a service that provides access to a [variety of LLMs](https://deepinfra.com/models?utm_source=langchain) and [embeddings models](https://deepinfra.com/models?type=embeddings&utm_source=langchain). This notebook goes over how to use LangChain with DeepInfra for chat models.
# 
# ## Set the Environment API Key
# Make sure to get your API key from DeepInfra. You have to [Login](https://deepinfra.com/login?from=%2Fdash) and get a new token.
# 
# You are given a 1 hour free of serverless GPU compute to test different models. (see [here](https://github.com/deepinfra/deepctl#deepctl))
# You can print your token with `deepctl auth token`

# In[ ]:


# get a new token: https://deepinfra.com/login?from=%2Fdash

import os
from getpass import getpass

from langchain_community.chat_models import ChatDeepInfra
from langchain_core.messages import HumanMessage

DEEPINFRA_API_TOKEN = getpass()

# or pass deepinfra_api_token parameter to the ChatDeepInfra constructor
os.environ["DEEPINFRA_API_TOKEN"] = DEEPINFRA_API_TOKEN

chat = ChatDeepInfra(model="meta-llama/Llama-2-7b-chat-hf")

messages = [
    HumanMessage(
        content="Translate this sentence from English to French. I love programming."
    )
]
chat.invoke(messages)


# ## `ChatDeepInfra` also supports async and streaming functionality:

# In[ ]:


from langchain_core.callbacks import StreamingStdOutCallbackHandler


# In[ ]:


await chat.agenerate([messages])


# In[ ]:


chat = ChatDeepInfra(
    streaming=True,
    verbose=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)
chat.invoke(messages)


# # Tool Calling
# 
# DeepInfra currently supports only invoke and async invoke tool calling.
# 
# For a complete list of models that support tool calling, please refer to our [tool calling documentation](https://deepinfra.com/docs/advanced/function_calling).

# In[ ]:


import asyncio

from dotenv import find_dotenv, load_dotenv
from langchain_community.chat_models import ChatDeepInfra
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel

model_name = "meta-llama/Meta-Llama-3-70B-Instruct"

_ = load_dotenv(find_dotenv())


# Langchain tool
@tool
def foo(something):
    """
    Called when foo
    """
    pass


# Pydantic class
class Bar(BaseModel):
    """
    Called when Bar
    """

    pass


llm = ChatDeepInfra(model=model_name)
tools = [foo, Bar]
llm_with_tools = llm.bind_tools(tools)
messages = [
    HumanMessage("Foo and bar, please."),
]

response = llm_with_tools.invoke(messages)
print(response.tool_calls)
# [{'name': 'foo', 'args': {'something': None}, 'id': 'call_Mi4N4wAtW89OlbizFE1aDxDj'}, {'name': 'Bar', 'args': {}, 'id': 'call_daiE0mW454j2O1KVbmET4s2r'}]


async def call_ainvoke():
    result = await llm_with_tools.ainvoke(messages)
    print(result.tool_calls)


# Async call
asyncio.run(call_ainvoke())
# [{'name': 'foo', 'args': {'something': None}, 'id': 'call_ZH7FetmgSot4LHcMU6CEb8tI'}, {'name': 'Bar', 'args': {}, 'id': 'call_2MQhDifAJVoijZEvH8PeFSVB'}]

