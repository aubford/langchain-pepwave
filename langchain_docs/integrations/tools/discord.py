#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Discord
---
# # Discord
# 
# This notebook provides a quick overview for getting started with Discord tooling in [langchain_discord](/docs/integrations/tools/). For more details on each tool and configuration, see the docstrings in your repository or relevant doc pages.
# 
# ## Overview
# 
# ### Integration details
# 
# | Class                                | Package                                                                 | Serializable | [JS support](https://js.langchain.com/docs/integrations/tools/langchain_discord) |                                             Package latest                                              |
# | :---                                 |:------------------------------------------------------------------------| :---:        | :---:                                                                           |:-------------------------------------------------------------------------------------------------------:|
# | `DiscordReadMessages`, `DiscordSendMessage` | [langchain-discord-shikenso](https://github.com/Shikenso-Analytics/langchain-discord) | N/A          | TBD                                                                             | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-discord-shikenso?style=flat-square&label=%20) |
# 
# ### Tool features
# 
# - **`DiscordReadMessages`**: Reads messages from a specified channel.
# - **`DiscordSendMessage`**: Sends messages to a specified channel.
# 
# ## Setup
# 
# The integration is provided by the `langchain-discord-shikenso` package. Install it as follows:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --quiet -U langchain-discord-shikenso')


# ### Credentials
# 
# This integration requires you to set `DISCORD_BOT_TOKEN` as an environment variable to authenticate with the Discord API.
# 
# ```bash
# export DISCORD_BOT_TOKEN="your-bot-token"
# ```

# In[ ]:


import getpass
import os

# Example prompt to set your token if not already set:
# if not os.environ.get("DISCORD_BOT_TOKEN"):
#     os.environ["DISCORD_BOT_TOKEN"] = getpass.getpass("DISCORD Bot Token:\n")


# You can optionally set up [LangSmith](https://smith.langchain.com/) for tracing or observability:

# In[ ]:


# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass()


# ## Instantiation
# 
# Below is an example showing how to instantiate the Discord tools in `langchain_discord`. Adjust as needed for your specific usage.

# In[ ]:


from langchain_discord.tools.discord_read_messages import DiscordReadMessages
from langchain_discord.tools.discord_send_messages import DiscordSendMessage

read_tool = DiscordReadMessages()
send_tool = DiscordSendMessage()

# Example usage:
# response = read_tool({"channel_id": "1234567890", "limit": 5})
# print(response)
#
# send_result = send_tool({"message": "Hello from notebook!", "channel_id": "1234567890"})
# print(send_result)


# ## Invocation
# 
# ### Direct invocation with args
# 
# Below is a simple example of calling the tool with keyword arguments in a dictionary.

# In[ ]:


invocation_args = {"channel_id": "1234567890", "limit": 3}
response = read_tool(invocation_args)
response


# ### Invocation with ToolCall
# 
# If you have a model-generated `ToolCall`, pass it to `tool.invoke()` in the format shown below.

# In[ ]:


tool_call = {
    "args": {"channel_id": "1234567890", "limit": 2},
    "id": "1",
    "name": read_tool.name,
    "type": "tool_call",
}

tool.invoke(tool_call)


# ## Chaining
# 
# Below is a more complete example showing how you might integrate the `DiscordReadMessages` and `DiscordSendMessage` tools in a chain or agent with an LLM. This example assumes you have a function (like `create_react_agent`) that sets up a LangChain-style agent capable of calling tools when appropriate.
# 
# ```python
# # Example: Using Discord Tools in an Agent
# 
# from langgraph.prebuilt import create_react_agent
# from langchain_discord.tools.discord_read_messages import DiscordReadMessages
# from langchain_discord.tools.discord_send_messages import DiscordSendMessage
# 
# # 1. Instantiate or configure your language model
# # (Replace with your actual LLM, e.g., ChatOpenAI(temperature=0))
# llm = ...
# 
# # 2. Create instances of the Discord tools
# read_tool = DiscordReadMessages()
# send_tool = DiscordSendMessage()
# 
# # 3. Build an agent that has access to these tools
# agent_executor = create_react_agent(llm, [read_tool, send_tool])
# 
# # 4. Formulate a user query that may invoke one or both tools
# example_query = "Please read the last 5 messages in channel 1234567890"
# 
# # 5. Execute the agent in streaming mode (or however your code is structured)
# events = agent_executor.stream(
#     {"messages": [("user", example_query)]},
#     stream_mode="values",
# )
# 
# # 6. Print out the model's responses (and any tool outputs) as they arrive
# for event in events:
#     event["messages"][-1].pretty_print()
# ```

# ## API reference
# 
# See the docstrings in:
# - [discord_read_messages.py](https://github.com/Shikenso-Analytics/langchain-discord/blob/main/langchain_discord/tools/discord_read_messages.py)
# - [discord_send_messages.py](https://github.com/Shikenso-Analytics/langchain-discord/blob/main/langchain_discord/tools/discord_send_messages.py)
# - [toolkits.py](https://github.com/Shikenso-Analytics/langchain-discord/blob/main/langchain_discord/toolkits.py)
# 
# for usage details, parameters, and advanced configurations.
