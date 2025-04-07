#!/usr/bin/env python
# coding: utf-8

# # INVALID_TOOL_RESULTS
# 
# You are passing too many, too few, or mismatched [`ToolMessages`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.tool.ToolMessage.html#toolmessage) to a model.
# 
# When [using a model to call tools](/docs/concepts/tool_calling), the [`AIMessage`](https://api.js.langchain.com/classes/_langchain_core.messages.AIMessage.html)
# the model responds with will contain a `tool_calls` array. To continue the flow, the next messages you pass back to the model must
# be exactly one `ToolMessage` for each item in that array containing the result of that tool call. Each `ToolMessage` must have a `tool_call_id` field
# that matches one of the `tool_calls` on the `AIMessage`.
# 
# For example, given the following response from a model:

# In[2]:


from typing import List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")


@tool
def foo_tool() -> str:
    """
    A dummy tool that returns 'action complete!'
    """
    return "action complete!"


model_with_tools = model.bind_tools([foo_tool])

chat_history: List[BaseMessage] = [
    HumanMessage(content='Call tool "foo" twice with no arguments')
]

response_message = model_with_tools.invoke(chat_history)

print(response_message.tool_calls)


# Calling the model with only one tool response would result in an error:

# In[3]:


from langchain_core.messages import AIMessage, ToolMessage

tool_call = response_message.tool_calls[0]
tool_response = foo_tool.invoke(tool_call)

chat_history.append(
    AIMessage(
        content=response_message.content,
        additional_kwargs=response_message.additional_kwargs,
    )
)
chat_history.append(
    ToolMessage(content=str(tool_response), tool_call_id=tool_call.get("id"))
)

final_response = model_with_tools.invoke(chat_history)
print(final_response)


# If we add a second response, the call will succeed as expected because we now have one tool response per tool call:

# In[5]:


tool_response_2 = foo_tool.invoke(response_message.tool_calls[1])

chat_history.append(tool_response_2)

model_with_tools.invoke(chat_history)


# But if we add a duplicate, extra tool response, the call will fail again:

# In[7]:


duplicate_tool_response_2 = foo_tool.invoke(response_message.tool_calls[1])

chat_history.append(duplicate_tool_response_2)

await model_with_tools.invoke(chat_history)


# You should additionally not pass `ToolMessages` back to to a model if they are not preceded by an `AIMessage` with tool calls. For example, this will fail:

# In[8]:


model_with_tools.invoke(
    [ToolMessage(content="action completed!", tool_call_id="dummy")]
)


# See [this guide](/docs/how_to/tool_results_pass_to_model/) for more details on tool calling.
# 
# ## Troubleshooting
# 
# The following may help resolve this error:
# 
# - If you are using a custom executor rather than a prebuilt one like LangGraph's [`ToolNode`](https://langchain-ai.github.io/langgraphjs/reference/classes/langgraph_prebuilt.ToolNode.html)
#   or the legacy LangChain [AgentExecutor](/docs/how_to/agent_executor), verify that you are invoking and returning the result for one tool per tool call.
# - If you are using [few-shot tool call examples](/docs/how_to/tools_few_shot) with messages that you manually create, and you want to simulate a failure,
#   you still need to pass back a `ToolMessage` whose content indicates that failure.
# 
