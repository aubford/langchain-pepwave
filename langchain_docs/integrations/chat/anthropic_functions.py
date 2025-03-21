#!/usr/bin/env python
# coding: utf-8
---
sidebar_class_name: hidden
---
# # [Deprecated] Experimental Anthropic Tools Wrapper
# 
# :::warning
# 
# The Anthropic API officially supports tool-calling so this workaround is no longer needed. Please use [ChatAnthropic](/docs/integrations/chat/anthropic) with `langchain-anthropic>=0.1.15`.
# 
# :::
# 
# This notebook shows how to use an experimental wrapper around Anthropic that gives it tool calling and structured output capabilities. It follows Anthropic's guide [here](https://docs.anthropic.com/claude/docs/functions-external-tools)
# 
# The wrapper is available from the `langchain-anthropic` package, and it also requires the optional dependency `defusedxml` for parsing XML output from the llm.
# 
# Note: this is a beta feature that will be replaced by Anthropic's formal implementation of tool calling, but it is useful for testing and experimentation in the meantime.

# In[1]:


get_ipython().run_line_magic('pip', 'install -qU langchain-anthropic defusedxml')
from langchain_anthropic.experimental import ChatAnthropicTools


# ## Tool Binding
# 
# `ChatAnthropicTools` exposes a `bind_tools` method that allows you to pass in Pydantic models or BaseTools to the llm.

# In[3]:


from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int


model = ChatAnthropicTools(model="claude-3-opus-20240229").bind_tools(tools=[Person])
model.invoke("I am a 27 year old named Erick")


# ## Structured Output
# 
# `ChatAnthropicTools` also implements the [`with_structured_output` spec](/docs/how_to/structured_output) for extracting values. Note: this may not be as stable as with models that explicitly offer tool calling.

# In[4]:


chain = ChatAnthropicTools(model="claude-3-opus-20240229").with_structured_output(
    Person
)
chain.invoke("I am a 27 year old named Erick")

