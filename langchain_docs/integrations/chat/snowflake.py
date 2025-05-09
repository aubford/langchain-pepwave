#!/usr/bin/env python
# coding: utf-8

# # Snowflake Cortex
# 
# [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions) gives you instant access to industry-leading large language models (LLMs) trained by researchers at companies like Mistral, Reka, Meta, and Google, including [Snowflake Arctic](https://www.snowflake.com/en/data-cloud/arctic/), an open enterprise-grade model developed by Snowflake.
# 
# This example goes over how to use LangChain to interact with Snowflake Cortex.

# ### Installation and setup
# 
# We start by installing the `snowflake-snowpark-python` library, using the command below. Then we configure the credentials for connecting to Snowflake, as environment variables or pass them directly.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet snowflake-snowpark-python')


# In[1]:


import getpass
import os

# First step is to set up the environment variables, to connect to Snowflake,
# you can also pass these snowflake credentials while instantiating the model

if os.environ.get("SNOWFLAKE_ACCOUNT") is None:
    os.environ["SNOWFLAKE_ACCOUNT"] = getpass.getpass("Account: ")

if os.environ.get("SNOWFLAKE_USERNAME") is None:
    os.environ["SNOWFLAKE_USERNAME"] = getpass.getpass("Username: ")

if os.environ.get("SNOWFLAKE_PASSWORD") is None:
    os.environ["SNOWFLAKE_PASSWORD"] = getpass.getpass("Password: ")

if os.environ.get("SNOWFLAKE_DATABASE") is None:
    os.environ["SNOWFLAKE_DATABASE"] = getpass.getpass("Database: ")

if os.environ.get("SNOWFLAKE_SCHEMA") is None:
    os.environ["SNOWFLAKE_SCHEMA"] = getpass.getpass("Schema: ")

if os.environ.get("SNOWFLAKE_WAREHOUSE") is None:
    os.environ["SNOWFLAKE_WAREHOUSE"] = getpass.getpass("Warehouse: ")

if os.environ.get("SNOWFLAKE_ROLE") is None:
    os.environ["SNOWFLAKE_ROLE"] = getpass.getpass("Role: ")


# In[ ]:


from langchain_community.chat_models import ChatSnowflakeCortex
from langchain_core.messages import HumanMessage, SystemMessage

# By default, we'll be using the cortex provided model: `mistral-large`, with function: `complete`
chat = ChatSnowflakeCortex()


# The above cell assumes that your Snowflake credentials are set in your environment variables. If you would rather manually specify them, use the following code:
# 
# ```python
# chat = ChatSnowflakeCortex(
#     # Change the default cortex model and function
#     model="mistral-large",
#     cortex_function="complete",
# 
#     # Change the default generation parameters
#     temperature=0,
#     max_tokens=10,
#     top_p=0.95,
# 
#     # Specify your Snowflake Credentials
#     account="YOUR_SNOWFLAKE_ACCOUNT",
#     username="YOUR_SNOWFLAKE_USERNAME",
#     password="YOUR_SNOWFLAKE_PASSWORD",
#     database="YOUR_SNOWFLAKE_DATABASE",
#     schema="YOUR_SNOWFLAKE_SCHEMA",
#     role="YOUR_SNOWFLAKE_ROLE",
#     warehouse="YOUR_SNOWFLAKE_WAREHOUSE"
# )
# ```

# ### Calling the chat model
# We can now call the chat model using the `invoke` or `stream` methods.

# messages = [
#     SystemMessage(content="You are a friendly assistant."),
#     HumanMessage(content="What are large language models?"),
# ]
# chat.invoke(messages)

# ### Stream

# In[ ]:


# Sample input prompt
messages = [
    SystemMessage(content="You are a friendly assistant."),
    HumanMessage(content="What are large language models?"),
]

# Invoke the stream method and print each chunk as it arrives
print("Stream Method Response:")
for chunk in chat._stream(messages):
    print(chunk.message.content)

