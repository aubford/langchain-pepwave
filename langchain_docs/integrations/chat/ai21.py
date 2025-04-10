#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: AI21 Labs
---
# # ChatAI21
# 
# ## Overview
# 
# This notebook covers how to get started with AI21 chat models.
# Note that different chat models support different parameters. See the [AI21 documentation](https://docs.ai21.com/reference) to learn more about the parameters in your chosen model.
# [See all AI21's LangChain components.](https://pypi.org/project/langchain-ai21/)
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/chat/__package_name_short_snake__) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: | :---: |
# | [ChatAI21](https://python.langchain.com/api_reference/ai21/chat_models/langchain_ai21.chat_models.ChatAI21.html#langchain_ai21.chat_models.ChatAI21) | [langchain-ai21](https://python.langchain.com/api_reference/ai21/index.html) | ❌ | beta | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-ai21?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-ai21?style=flat-square&label=%20) |
# 
# ### Model features
# | [Tool calling](/docs/how_to/tool_calling) | [Structured output](/docs/how_to/structured_output/) | JSON mode | [Image input](/docs/how_to/multimodal_inputs/) | Audio input | Video input | [Token-level streaming](/docs/how_to/chat_streaming/) | Native async | [Token usage](/docs/how_to/chat_token_usage_tracking/) | [Logprobs](/docs/how_to/logprobs/) |
# | :---: | :---: | :---: | :---: |  :---: | :---: | :---: | :---: | :---: | :---: |
# | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
# 
# 
# ## Setup

# ### Credentials
# 
# We'll need to get an [AI21 API key](https://docs.ai21.com/) and set the `AI21_API_KEY` environment variable:
# 

# In[ ]:


import os
from getpass import getpass

if "AI21_API_KEY" not in os.environ:
    os.environ["AI21_API_KEY"] = getpass()


# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")


# ### Installation

# !pip install -qU langchain-ai21

# ## Instantiation
# 
# Now we can instantiate our model object and generate chat completions:

# In[ ]:


from langchain_ai21 import ChatAI21

llm = ChatAI21(model="jamba-instruct", temperature=0)


# ## Invocation

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


# # Tool Calls / Function Calling

# This example shows how to use tool calling with AI21 models:

# In[ ]:


import os
from getpass import getpass

from langchain_ai21.chat_models import ChatAI21
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool

if "AI21_API_KEY" not in os.environ:
    os.environ["AI21_API_KEY"] = getpass()


@tool
def get_weather(location: str, date: str) -> str:
    """“Provide the weather for the specified location on the given date.”"""
    if location == "New York" and date == "2024-12-05":
        return "25 celsius"
    elif location == "New York" and date == "2024-12-06":
        return "27 celsius"
    elif location == "London" and date == "2024-12-05":
        return "22 celsius"
    return "32 celsius"


llm = ChatAI21(model="jamba-1.5-mini")

llm_with_tools = llm.bind_tools([convert_to_openai_tool(get_weather)])

chat_messages = [
    SystemMessage(
        content="You are a helpful assistant. You can use the provided tools "
        "to assist with various tasks and provide accurate information"
    )
]

human_messages = [
    HumanMessage(
        content="What is the forecast for the weather in New York on December 5, 2024?"
    ),
    HumanMessage(content="And what about the 2024-12-06?"),
    HumanMessage(content="OK, thank you."),
    HumanMessage(content="What is the expected weather in London on December 5, 2024?"),
]


for human_message in human_messages:
    print(f"User: {human_message.content}")
    chat_messages.append(human_message)
    response = llm_with_tools.invoke(chat_messages)
    chat_messages.append(response)
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "get_weather":
            weather = get_weather.invoke(
                {
                    "location": tool_call["args"]["location"],
                    "date": tool_call["args"]["date"],
                }
            )
            chat_messages.append(
                ToolMessage(content=weather, tool_call_id=tool_call["id"])
            )
            llm_answer = llm_with_tools.invoke(chat_messages)
            print(f"Assistant: {llm_answer.content}")
    else:
        print(f"Assistant: {response.content}")


# ## API reference
# 
# For detailed documentation of all ChatAI21 features and configurations head to the API reference: https://python.langchain.com/api_reference/ai21/chat_models/langchain_ai21.chat_models.ChatAI21.html
