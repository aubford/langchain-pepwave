#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: IBM watsonx.ai
---
# # IBM watsonx.ai
# 
# >WatsonxToolkit is a wrapper for IBM [watsonx.ai](https://www.ibm.com/products/watsonx-ai) Toolkit.
# 
# This example shows how to use `watsonx.ai` Toolkit using `LangChain`.

# ## Overview
# 
# ### Integration details
# 
# | Class | Package | Serializable | [JS support](https://js.langchain.com/docs/integrations/toolkits/ibm/) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: | :---: | :---: |
# | [WatsonxToolkit](https://python.langchain.com/api_reference/ibm/toolkit/langchain_ibm.toolkit.WatsonxToolkit.html) | [langchain-ibm](https://python.langchain.com/api_reference/ibm/index.html) | ❌ | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-ibm?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain-ibm?style=flat-square&label=%20) |

# ## Setup
# 
# To access IBM watsonx.ai toolkit you'll need to create an IBM watsonx.ai account, get an API key, and install the `langchain-ibm` integration package.
# 
# ### Credentials
# 
# This cell defines the WML credentials required to work with watsonx Toolkit.
# 
# **Action:** Provide the IBM Cloud user API key. For details, see
# [documentation](https://cloud.ibm.com/docs/account?topic=account-userapikey&interface=ui).

# In[1]:


import os
from getpass import getpass

watsonx_api_key = getpass()
os.environ["WATSONX_APIKEY"] = watsonx_api_key


# Additionaly you are able to pass additional secrets as an environment variable. 

# In[ ]:


import os

os.environ["WATSONX_URL"] = "your service instance url"
os.environ["WATSONX_TOKEN"] = "your token for accessing the service instance"


# ### Installation
# 
# The LangChain IBM integration lives in the `langchain-ibm` package:

# In[ ]:


get_ipython().system('pip install -qU langchain-ibm')


# ## Instantiation
# 

# Initialize the `WatsonxToolkit` class.
# 
# 

# In[2]:


from langchain_ibm import WatsonxToolkit

watsonx_toolkit = WatsonxToolkit(
    url="https://us-south.ml.cloud.ibm.com",
)


# For certain requirements, there is an option to pass the IBM's [`APIClient`](https://ibm.github.io/watsonx-ai-python-sdk/base.html#apiclient) object into the `WatsonxToolkit` class.

# In[ ]:


from ibm_watsonx_ai import APIClient

api_client = APIClient(...)

watsonx_toolkit = WatsonxToolkit(
    watsonx_client=api_client,
)


# ## Tools
# 

# ### Get all tools
# It is possible to get all available tools as a list of `WatsonxTool` objects.

# In[ ]:


watsonx_toolkit.get_tools()


# ### Get a tool
# You can also get a specific `WatsonxTool` by name.

# In[4]:


google_search = watsonx_toolkit.get_tool(tool_name="GoogleSearch")


# ## Invocation

# ### Invoke the tool with a simple input

# In[5]:


search_result = google_search.invoke(input="IBM")
search_result


# To fetch a list of received results, you can execute the below cell.

# In[ ]:


import json

output = json.loads(search_result.get("output"))
output


# ### Invoke the tool with a configuration

# To check if a tool has a config schema and view its properties you can look at the tool's `tool_config_schema`.
# 
# In this example, the tool has a config schema that contains `maxResults` parameter to set maximum number of results to be returned.

# In[7]:


google_search.tool_config_schema


# To set `tool_config` parameters, you need to use `set_tool_config()` method and pass correct `dict` according to above `tool_config_schema`.

# In[8]:


import json

config = {"maxResults": 3}
google_search.set_tool_config(config)

search_result = google_search.invoke(input="IBM")
output = json.loads(search_result.get("output"))


# There is supposed to be maximum 3 results.

# In[9]:


print(len(output))


# ### Invoke the tool with an input schema
# 
# We need to get another tool (with an input schema) for the example purpose.

# In[10]:


weather_tool = watsonx_toolkit.get_tool("Weather")


# To check if a tool has an input schema and view its properties, you can look at the tool's `tool_input_schema`.
# 
# In this example, the tool has an input schema that contains one required and one optional parameter.

# In[11]:


weather_tool.tool_input_schema


# To correctly pass an input to `invoke()`, you need to create an `invoke_input` dictionary with required parameter as a key with its value.

# In[12]:


invoke_input = {
    "location": "New York",
}

weather_result = weather_tool.invoke(input=invoke_input)
weather_result


# This time the output is a single string value. To fetch and print it you can execute the below cell.

# In[13]:


output = weather_result.get("output")
print(output)


# ### Invoke the tool with a ToolCall
# 
# We can also invoke the tool with a ToolCall, in which case a ToolMessage will be returned:

# In[14]:


invoke_input = {
    "location": "Los Angeles",
}
tool_call = dict(
    args=invoke_input,
    id="1",
    name=weather_tool.name,
    type="tool_call",
)
weather_tool.invoke(input=tool_call)


# ## Use within an agent

# In[ ]:


from langchain_ibm import ChatWatsonx

llm = ChatWatsonx(
    model_id="meta-llama/llama-3-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="PASTE YOUR PROJECT_ID HERE",
)


# In[16]:


from langgraph.prebuilt import create_react_agent

tools = [weather_tool]
agent = create_react_agent(llm, tools)


# In[17]:


example_query = "What is the weather in Boston?"

events = agent.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# ## API reference
# 
# For detailed documentation of all `WatsonxToolkit` features and configurations head to the [API reference](https://python.langchain.com/api_reference/ibm/toolkit/langchain_ibm.toolkit.WatsonxToolkit.html).
