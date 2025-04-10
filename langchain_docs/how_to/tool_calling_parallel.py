#!/usr/bin/env python
# coding: utf-8

# # How to disable parallel tool calling
# 
# :::info OpenAI-specific
# 
# This API is currently only supported by OpenAI.
# 
# :::
# 
# OpenAI tool calling performs tool calling in parallel by default. That means that if we ask a question like "What is the weather in Tokyo, New York, and Chicago?" and we have a tool for getting the weather, it will call the tool 3 times in parallel. We can force it to call only a single tool once by using the ``parallel_tool_call`` parameter.

# First let's set up our tools and model:

# In[ ]:


from langchain_core.tools import tool


@tool
def add(a: int, b: int) -> int:
    """Adds a and b."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b


tools = [add, multiply]


# In[ ]:


import os
from getpass import getpass

from langchain_openai import ChatOpenAI

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# Now let's show a quick example of how disabling parallel tool calls work:

# In[ ]:


llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
llm_with_tools.invoke("Please call the first tool two times").tool_calls


# As we can see, even though we explicitly told the model to call a tool twice, by disabling parallel tool calls the model was constrained to only calling one.

# 
