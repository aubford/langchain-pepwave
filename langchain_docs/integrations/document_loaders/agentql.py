#!/usr/bin/env python
# coding: utf-8

# # AgentQLLoader
# 
# [AgentQL](https://www.agentql.com/)'s document loader provides structured data extraction from any web page using an [AgentQL query](https://docs.agentql.com/agentql-query). AgentQL can be used across multiple languages and web pages without breaking over time and change.
# 
# ## Overview
# 
# `AgentQLLoader` requires the following two parameters:
# - `url`: The URL of the web page you want to extract data from.
# - `query`: The AgentQL query to execute. Learn more about [how to write an AgentQL query in the docs](https://docs.agentql.com/agentql-query) or test one out in the [AgentQL Playground](https://dev.agentql.com/playground).
# 
# Setting the following parameters are optional:
# - `api_key`: Your AgentQL API key from [dev.agentql.com](https://dev.agentql.com). **`Optional`.**
# - `timeout`: The number of seconds to wait for a request before timing out. **Defaults to `900`.**
# - `is_stealth_mode_enabled`: Whether to enable experimental anti-bot evasion strategies. This feature may not work for all websites at all times. Data extraction may take longer to complete with this mode enabled. **Defaults to `False`.**
# - `wait_for`: The number of seconds to wait for the page to load before extracting data. **Defaults to `0`.**
# - `is_scroll_to_bottom_enabled`: Whether to scroll to bottom of the page before extracting data. **Defaults to `False`.**
# - `mode`: `"standard"` uses deep data analysis, while `"fast"` trades some depth of analysis for speed and is adequate for most usecases. [Learn more about the modes in this guide.](https://docs.agentql.com/accuracy/standard-mode) **Defaults to `"fast"`.**
# - `is_screenshot_enabled`: Whether to take a screenshot before extracting data. Returned in 'metadata' as a Base64 string. **Defaults to `False`.**
# 
# AgentQLLoader is implemented with AgentQL's [REST API](https://docs.agentql.com/rest-api/api-reference)
# 
# ### Integration details
# 
# | Class | Package | Local | Serializable | JS support |
# | :--- | :--- | :---: | :---: |  :---: |
# | AgentQLLoader| langchain-agentql | ✅ | ❌ | ❌ |
# 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: |
# | AgentQLLoader | ✅ | ❌ |

# ## Setup
# 
# To use the AgentQL Document Loader, you will need to configure the `AGENTQL_API_KEY` environment variable, or use the `api_key` parameter. You can acquire an API key from our [Dev Portal](https://dev.agentql.com).

# ### Installation
# 
# Install **langchain-agentql**.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain_agentql')


# ### Set Credentials

# In[3]:


import os

os.environ["AGENTQL_API_KEY"] = "YOUR_AGENTQL_API_KEY"


# ## Initialization
# 
# Next instantiate your model object:

# In[4]:


from langchain_agentql.document_loaders import AgentQLLoader

loader = AgentQLLoader(
    url="https://www.agentql.com/blog",
    query="""
    {
        posts[] {
            title
            url
            date
            author
        }
    }
    """,
    is_scroll_to_bottom_enabled=True,
)


# ## Load

# In[5]:


docs = loader.load()
docs[0]


# In[6]:


print(docs[0].metadata)


# ## Lazy Load
# 
# `AgentQLLoader` currently only loads one `Document` at a time. Therefore, `load()` and `lazy_load()` behave the same:

# In[7]:


pages = [doc for doc in loader.lazy_load()]
pages


# ## API reference
# 
# For more information on how to use this integration, please refer to the [git repo](https://github.com/tinyfish-io/agentql-integrations/tree/main/langchain) or the [langchain integration documentation](https://docs.agentql.com/integrations/langchain)
