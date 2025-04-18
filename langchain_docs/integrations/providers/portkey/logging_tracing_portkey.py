#!/usr/bin/env python
# coding: utf-8

# # Log, Trace, and Monitor
# 
# When building apps or agents using Langchain, you end up making multiple API calls to fulfill a single user request. However, these requests are not chained when you want to analyse them. With [**Portkey**](/docs/integrations/providers/portkey/), all the embeddings, completions, and other requests from a single user request will get logged and traced to a common ID, enabling you to gain full visibility of user interactions.
# 
# This notebook serves as a step-by-step guide on how to log, trace, and monitor Langchain LLM calls using `Portkey` in your Langchain app.

# First, let's import Portkey, OpenAI, and Agent tools

# In[1]:


import os

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders


# Paste your OpenAI API key below. [(You can find it here)](https://platform.openai.com/account/api-keys)

# In[5]:


os.environ["OPENAI_API_KEY"] = "..."


# ## Get Portkey API Key
# 1. Sign up for [Portkey here](https://app.portkey.ai/signup)
# 2. On your [dashboard](https://app.portkey.ai/), click on the profile icon on the bottom left, then click on "Copy API Key"
# 3. Paste it below

# In[4]:


PORTKEY_API_KEY = "..."  # Paste your Portkey API Key here


# ## Set Trace ID
# 1. Set the trace id for your request below
# 2. The Trace ID can be common for all API calls originating from a single request

# In[6]:


TRACE_ID = "uuid-trace-id"  # Set trace id here


# ## Generate Portkey Headers

# In[10]:


portkey_headers = createHeaders(
    api_key=PORTKEY_API_KEY, provider="openai", trace_id=TRACE_ID
)


# Define the prompts and the tools to use

# In[11]:


from langchain import hub
from langchain_core.tools import tool

prompt = hub.pull("hwchase17/openai-tools-agent")


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int


@tool
def exponentiate(base: int, exponent: int) -> int:
    "Exponentiate the base to the exponent power."
    return base**exponent


tools = [multiply, exponentiate]


# Run your agent as usual. The **only** change is that we will **include the above headers** in the request now.

# In[12]:


model = ChatOpenAI(
    base_url=PORTKEY_GATEWAY_URL, default_headers=portkey_headers, temperature=0
)

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(model, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke(
    {
        "input": "Take 3 to the fifth power and multiply that by thirty six, then square the result"
    }
)


# ## How Logging & Tracing Works on Portkey
# 
# **Logging**
# - Sending your request through Portkey ensures that all of the requests are logged by default
# - Each request log contains `timestamp`, `model name`, `total cost`, `request time`, `request json`, `response json`, and additional Portkey features
# 
# **[Tracing](https://portkey.ai/docs/product/observability-modern-monitoring-for-llms/traces)**
# - Trace id is passed along with each request and is visible on the logs on Portkey dashboard
# - You can also set a **distinct trace id** for each request if you want
# - You can append user feedback to a trace id as well. [More info on this here](https://portkey.ai/docs/product/observability-modern-monitoring-for-llms/feedback)
# 
# For the above request, you will be able to view the entire log trace like this
# ![View Langchain traces on Portkey](https://assets.portkey.ai/docs/agent_tracing.gif)

# ## Advanced LLMOps Features - Caching, Tagging, Retries
# 
# In addition to logging and tracing, Portkey provides more features that add production capabilities to your existing workflows:
# 
# **Caching**
# 
# Respond to previously served customers queries from cache instead of sending them again to OpenAI. Match exact strings OR semantically similar strings. Cache can save costs and reduce latencies by 20x. [Docs](https://portkey.ai/docs/product/ai-gateway-streamline-llm-integrations/cache-simple-and-semantic)
# 
# **Retries**
# 
# Automatically reprocess any unsuccessful API requests **`upto 5`** times. Uses an **`exponential backoff`** strategy, which spaces out retry attempts to prevent network overload.[Docs](https://portkey.ai/docs/product/ai-gateway-streamline-llm-integrations)
# 
# **Tagging**
# 
# Track and audit each user interaction in high detail with predefined tags. [Docs](https://portkey.ai/docs/product/observability-modern-monitoring-for-llms/metadata)
