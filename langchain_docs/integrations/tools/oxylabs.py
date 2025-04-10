#!/usr/bin/env python
# coding: utf-8

# # Oxylabs

# >[Oxylabs](https://oxylabs.io/) is a market-leading web intelligence collection platform, driven by the highest business, ethics, and compliance standards, enabling companies worldwide to unlock data-driven insights.
# 
# ## Overview
# 
# This package contains the LangChain integration with Oxylabs, providing tools to scrape Google search results with Oxylabs Web Scraper API using LangChain's framework.
# 
# The following classes are provided by this package:
# - `OxylabsSearchRun` - A tool that returns scraped Google search results in a formatted text
# - `OxylabsSearchResults` - A tool that returns scraped Google search results in a JSON format
# - `OxylabsSearchAPIWrapper` - An API wrapper for initializing Oxylabs API

# |             Pricing             |
# |:-------------------------------:|
# | ✅ Free 5,000 results for 1 week |

# ## Setup

# Install the required dependencies.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-oxylabs')


# ### Credentials

# Set up the proper API keys and environment variables. Create your API user credentials: Sign up for a free trial or purchase the product in the [Oxylabs dashboard](https://dashboard.oxylabs.io/en/registration) to create your API user credentials (OXYLABS_USERNAME and OXYLABS_PASSWORD).

# In[ ]:


import getpass
import os

os.environ["OXYLABS_USERNAME"] = getpass.getpass("Enter your Oxylabs username: ")
os.environ["OXYLABS_PASSWORD"] = getpass.getpass("Enter your Oxylabs password: ")


# ## Instantiation

# In[ ]:


from langchain_oxylabs import OxylabsSearchAPIWrapper, OxylabsSearchRun

oxylabs_wrapper = OxylabsSearchAPIWrapper()
tool_ = OxylabsSearchRun(wrapper=oxylabs_wrapper)


# ## Invocation

# ### Invoke directly with args

# The `OxylabsSearchRun` tool takes a single "query" argument, which should be a natural language query and returns combined string format result:

# In[ ]:


tool_.invoke({"query": "Restaurants in Paris."})


# ### Invoke with ToolCall

# In[ ]:


tool_ = OxylabsSearchRun(
    wrapper=oxylabs_wrapper,
    kwargs={
        "result_categories": [
            "local_information",
            "combined_search_result",
        ]
    },
)


# In[ ]:


from pprint import pprint

model_generated_tool_call = {
    "args": {
        "query": "Visit restaurants in Vilnius.",
        "geo_location": "Vilnius,Lithuania",
    },
    "id": "1",
    "name": "oxylabs_search",
    "type": "tool_call",
}
tool_call_result = tool_.invoke(model_generated_tool_call)

# The content is a JSON string of results
pprint(tool_call_result.content)


# ## Use within an agent
# Install the required dependencies.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU "langchain[openai]" langgraph')


# In[ ]:


import getpass
import os

from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
llm = init_chat_model("gpt-4o-mini", model_provider="openai")


# In[ ]:


from langgraph.prebuilt import create_react_agent

# Initialize OxylabsSearchRun tool
tool_ = OxylabsSearchRun(wrapper=oxylabs_wrapper)

agent = create_react_agent(llm, [tool_])

user_input = "What happened in the latest Burning Man floods?"

for step in agent.stream(
    {"messages": user_input},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()


# ## JSON results
# `OxylabsSearchResults` tool can be used as an alternative to `OxylabsSearchRun` to retrieve results in a JSON format:

# In[ ]:


import json

from langchain_oxylabs import OxylabsSearchResults

tool_ = OxylabsSearchResults(wrapper=oxylabs_wrapper)

response_results = tool_.invoke({"query": "What are the most famous artists?"})
response_results = json.loads(response_results)

for result in response_results:
    for key, value in result.items():
        print(f"{key}: {value}")


# ## API reference
# More information about this integration package can be found here: https://github.com/oxylabs/langchain-oxylabs
# 
# Oxylabs Web Scraper API documentation: https://developers.oxylabs.io/scraper-apis/web-scraper-api
# 
