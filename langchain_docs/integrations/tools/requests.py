#!/usr/bin/env python
# coding: utf-8

# # Requests Toolkit
# 
# We can use the Requests [toolkit](/docs/concepts/tools/#toolkits) to construct agents that generate HTTP requests.
# 
# For detailed documentation of all API toolkit features and configurations head to the API reference for [RequestsToolkit](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.openapi.toolkit.RequestsToolkit.html).
# 
# ## ⚠️ Security note ⚠️
# There are inherent risks in giving models discretion to execute real-world actions. Take precautions to mitigate these risks:
# 
# - Make sure that permissions associated with the tools are narrowly-scoped (e.g., for database operations or API requests);
# - When desired, make use of human-in-the-loop workflows.

# ## Setup
# 
# ### Installation
# 
# This toolkit lives in the `langchain-community` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# To enable automated tracing of individual tools, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ## Instantiation
# 
# First we will demonstrate a minimal example.
# 
# **NOTE**: There are inherent risks in giving models discretion to execute real-world actions. We must "opt-in" to these risks by setting `allow_dangerous_request=True` to use these tools.
# **This can be dangerous for calling unwanted requests**. Please make sure your custom OpenAPI spec (yaml) is safe and that permissions associated with the tools are narrowly-scoped.

# In[1]:


ALLOW_DANGEROUS_REQUEST = True


# We can use the [JSONPlaceholder](https://jsonplaceholder.typicode.com) API as a testing ground.
# 
# Let's create (a subset of) its API spec:

# In[2]:


from typing import Any, Dict, Union

import requests
import yaml


def _get_schema(response_json: Union[dict, list]) -> dict:
    if isinstance(response_json, list):
        response_json = response_json[0] if response_json else {}
    return {key: type(value).__name__ for key, value in response_json.items()}


def _get_api_spec() -> str:
    base_url = "https://jsonplaceholder.typicode.com"
    endpoints = [
        "/posts",
        "/comments",
    ]
    common_query_parameters = [
        {
            "name": "_limit",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "example": 2},
            "description": "Limit the number of results",
        }
    ]
    openapi_spec: Dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"title": "JSONPlaceholder API", "version": "1.0.0"},
        "servers": [{"url": base_url}],
        "paths": {},
    }
    # Iterate over the endpoints to construct the paths
    for endpoint in endpoints:
        response = requests.get(base_url + endpoint)
        if response.status_code == 200:
            schema = _get_schema(response.json())
            openapi_spec["paths"][endpoint] = {
                "get": {
                    "summary": f"Get {endpoint[1:]}",
                    "parameters": common_query_parameters,
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": schema}
                                }
                            },
                        }
                    },
                }
            }
    return yaml.dump(openapi_spec, sort_keys=False)


api_spec = _get_api_spec()


# Next we can instantiate the toolkit. We require no authorization or other headers for this API:

# In[3]:


from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper

toolkit = RequestsToolkit(
    requests_wrapper=TextRequestsWrapper(headers={}),
    allow_dangerous_requests=ALLOW_DANGEROUS_REQUEST,
)


# ## Tools
# 
# View available tools:

# In[4]:


tools = toolkit.get_tools()

tools


# - [RequestsGetTool](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.requests.tool.RequestsGetTool.html)
# - [RequestsPostTool](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.requests.tool.RequestsPostTool.html)
# - [RequestsPatchTool](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.requests.tool.RequestsPatchTool.html)
# - [RequestsPutTool](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.requests.tool.RequestsPutTool.html)
# - [RequestsDeleteTool](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.requests.tool.RequestsDeleteTool.html)

# ## Use within an agent

# In[5]:


from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o-mini")

system_message = """
You have access to an API to help answer user queries.
Here is documentation on the API:
{api_spec}
""".format(api_spec=api_spec)

agent_executor = create_react_agent(llm, tools, prompt=system_message)


# In[6]:


example_query = "Fetch the top two posts. What are their titles?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()


# ## API reference
# 
# For detailed documentation of all API toolkit features and configurations head to the API reference for [RequestsToolkit](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.openapi.toolkit.RequestsToolkit.html).
