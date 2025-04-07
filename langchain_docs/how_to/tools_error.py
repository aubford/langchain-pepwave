#!/usr/bin/env python
# coding: utf-8

# # How to handle tool errors
# 
# :::info Prerequisites
# 
# This guide assumes familiarity with the following concepts:
# - [Chat models](/docs/concepts/chat_models)
# - [LangChain Tools](/docs/concepts/tools)
# - [How to use a model to call tools](/docs/how_to/tool_calling)
# 
# :::
# 
# [Calling tools](/docs/concepts/tool_calling/) with an LLM is generally more reliable than pure prompting, but it isn't perfect. The model may try to call a tool that doesn't exist or fail to return arguments that match the requested schema. Strategies like keeping schemas simple, reducing the number of tools you pass at once, and having good names and descriptions can help mitigate this risk, but aren't foolproof.
# 
# This guide covers some ways to build error handling into your chains to mitigate these failure modes.

# ## Setup
# 
# We'll need to install the following packages:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-core langchain-openai')


# If you'd like to trace your runs in [LangSmith](https://docs.smith.langchain.com/) uncomment and set the following environment variables:

# In[2]:


import getpass
import os

# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ## Chain
# 
# Suppose we have the following (dummy) tool and tool-calling chain. We'll make our tool intentionally convoluted to try and trip up the model.
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm"/>
# 

# In[3]:


# | echo: false
# | output: false

from langchain_openai import ChatOpenAI

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# In[4]:


# Define tool
from langchain_core.tools import tool


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> int:
    """Do something complex with a complex tool."""
    return int_arg * float_arg


llm_with_tools = llm.bind_tools(
    [complex_tool],
)

# Define chain
chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | complex_tool


# We can see that when we try to invoke this chain with even a fairly explicit input, the model fails to correctly call the tool (it forgets the `dict_arg` argument).

# In[5]:


chain.invoke(
    "use complex tool. the args are 5, 2.1, empty dictionary. don't forget dict_arg"
)


# ## Try/except tool call
# 
# The simplest way to more gracefully handle errors is to try/except the tool-calling step and return a helpful message on errors:

# In[6]:


from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig


def try_except_tool(tool_args: dict, config: RunnableConfig) -> Runnable:
    try:
        complex_tool.invoke(tool_args, config=config)
    except Exception as e:
        return f"Calling tool with arguments:\n\n{tool_args}\n\nraised the following error:\n\n{type(e)}: {e}"


chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | try_except_tool

print(
    chain.invoke(
        "use complex tool. the args are 5, 2.1, empty dictionary. don't forget dict_arg"
    )
)


# ## Fallbacks
# 
# We can also try to fallback to a better model in the event of a tool invocation error. In this case we'll fall back to an identical chain that uses `gpt-4-1106-preview` instead of `gpt-3.5-turbo`.

# In[7]:


chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | complex_tool

better_model = ChatOpenAI(model="gpt-4-1106-preview", temperature=0).bind_tools(
    [complex_tool], tool_choice="complex_tool"
)

better_chain = better_model | (lambda msg: msg.tool_calls[0]["args"]) | complex_tool

chain_with_fallback = chain.with_fallbacks([better_chain])

chain_with_fallback.invoke(
    "use complex tool. the args are 5, 2.1, empty dictionary. don't forget dict_arg"
)


# Looking at the [LangSmith trace](https://smith.langchain.com/public/00e91fc2-e1a4-4b0f-a82e-e6b3119d196c/r) for this chain run, we can see that the first chain call fails as expected and it's the fallback that succeeds.

# ## Retry with exception
# 
# To take things one step further, we can try to automatically re-run the chain with the exception passed in, so that the model may be able to correct its behavior:

# In[8]:


from langchain_core.messages import AIMessage, HumanMessage, ToolCall, ToolMessage
from langchain_core.prompts import ChatPromptTemplate


class CustomToolException(Exception):
    """Custom LangChain tool exception."""

    def __init__(self, tool_call: ToolCall, exception: Exception) -> None:
        super().__init__()
        self.tool_call = tool_call
        self.exception = exception


def tool_custom_exception(msg: AIMessage, config: RunnableConfig) -> Runnable:
    try:
        return complex_tool.invoke(msg.tool_calls[0]["args"], config=config)
    except Exception as e:
        raise CustomToolException(msg.tool_calls[0], e)


def exception_to_messages(inputs: dict) -> dict:
    exception = inputs.pop("exception")

    # Add historical messages to the original input, so the model knows that it made a mistake with the last tool call.
    messages = [
        AIMessage(content="", tool_calls=[exception.tool_call]),
        ToolMessage(
            tool_call_id=exception.tool_call["id"], content=str(exception.exception)
        ),
        HumanMessage(
            content="The last tool call raised an exception. Try calling the tool again with corrected arguments. Do not repeat mistakes."
        ),
    ]
    inputs["last_output"] = messages
    return inputs


# We add a last_output MessagesPlaceholder to our prompt which if not passed in doesn't
# affect the prompt at all, but gives us the option to insert an arbitrary list of Messages
# into the prompt if needed. We'll use this on retries to insert the error message.
prompt = ChatPromptTemplate.from_messages(
    [("human", "{input}"), ("placeholder", "{last_output}")]
)
chain = prompt | llm_with_tools | tool_custom_exception

# If the initial chain call fails, we rerun it withe the exception passed in as a message.
self_correcting_chain = chain.with_fallbacks(
    [exception_to_messages | chain], exception_key="exception"
)


# In[9]:


self_correcting_chain.invoke(
    {
        "input": "use complex tool. the args are 5, 2.1, empty dictionary. don't forget dict_arg"
    }
)


# And our chain succeeds! Looking at the [LangSmith trace](https://smith.langchain.com/public/c11e804c-e14f-4059-bd09-64766f999c14/r), we can see that indeed our initial chain still fails, and it's only on retrying that the chain succeeds.

# ## Next steps
# 
# Now you've seen some strategies how to handle tool calling errors. Next, you can learn more about how to use tools:
# 
# - Few shot prompting [with tools](/docs/how_to/tools_few_shot/)
# - Stream [tool calls](/docs/how_to/tool_streaming/)
# - Pass [runtime values to tools](/docs/how_to/tool_runtime)
# 
# You can also check out some more specific uses of tool calling:
# 
# - Getting [structured outputs](/docs/how_to/structured_output/) from models
