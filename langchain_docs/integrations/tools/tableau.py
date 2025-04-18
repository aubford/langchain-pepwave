#!/usr/bin/env python
# coding: utf-8

# # Tableau
# 
# This notebook provides a quick overview for getting started with [Tableau](https://help.tableau.com/current/api/vizql-data-service/en-us/index.html). 

# ### Overview
# 
# Tableau's VizQL Data Service (aka VDS) provides developers with programmatic access to their Tableau Published Data Sources, allowing them to extend their business semantics for any custom workload or application, including AI Agents. The simple_datasource_qa tool adds VDS to the Langchain framework. This notebook shows you how you can use it to build agents that answer analytical questions grounded on your enterprise semantic models. 
# 
# Follow the [tableau-langchain](https://github.com/Tab-SE/tableau_langchain) project for more tools coming soon!

# #### Setup
# Make sure you are running and have access to:
# 1. python version 3.12.2 or higher
# 2. A Tableau Cloud or Server environment with at least 1 published data source
# 
# Get started by installing and/or importing the required packages

# In[ ]:


# %pip install langchain-openai


# In[ ]:


# %pip install langgraph


# In[ ]:


# %pip install langchain-tableau --upgrade


# Note you may need to restart your kernal to use updated packages

# ### Credentials
# 
# You can declare your environment variables explicitly, as shown in several cases in this doc. However, if these parameters are not provided, the simple_datasource_qa tool will attempt to automatically read them from environment variables.
# 
# For the Data Source that you choose to query, make sure you've updated the VizqlDataApiAccess permission in Tableau to allow the VDS API to access that Data Source via REST. More info [here](https://help.tableau.com/current/server/en-us/permissions_capabilities.htm#data-sources
# ). 

# In[ ]:


# langchain package imports
from langchain_openai import ChatOpenAI

# langchain_tableau and langgraph imports
from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa
from langgraph.prebuilt import create_react_agent


# ## Authentication Variables
# You can declare your environment variables explicitly, as shown in several cases in this cookbook. However, if these parameters are not provided, the simple_datasource_qa tool will attempt to automatically read them from environment variables.
# 
# For the Data Source that you choose, make sure you've updated the VizqlDataApiAccess permission in Tableau to allow the VDS API to access that Data Source via REST. More info [here](https://help.tableau.com/current/server/en-us/permissions_capabilities.htm#data-sources
# ). 

# In[6]:


import os

from dotenv import load_dotenv

load_dotenv()

tableau_server = "https://stage-dataplane2.tableau.sfdc-shbmgi.svc.sfdcfc.net/"  # replace with your Tableau server name
tableau_site = "vizqldataservicestage02"  # replace with your Tableau site
tableau_jwt_client_id = os.getenv(
    "TABLEAU_JWT_CLIENT_ID"
)  # a JWT client ID (obtained through Tableau's admin UI)
tableau_jwt_secret_id = os.getenv(
    "TABLEAU_JWT_SECRET_ID"
)  # a JWT secret ID (obtained through Tableau's admin UI)
tableau_jwt_secret = os.getenv(
    "TABLEAU_JWT_SECRET"
)  # a JWT secret ID (obtained through Tableau's admin UI)
tableau_api_version = "3.21"  # the current Tableau REST API Version
tableau_user = "joe.constantino@salesforce.com"  # replace with the username querying the target Tableau Data Source

# For this cookbook we are connecting to the Superstore dataset that comes by default with every Tableau server
datasource_luid = (
    "0965e61b-a072-43cf-994c-8c6cf526940d"  # the target data source for this Tool
)

# Add variables to control LLM models for the Agent and Tools
os.environ["OPENAI_API_KEY"]  # set an your model API key as an environment variable
tooling_llm_model = "gpt-4o"


# ## Instantiation
# The initialize_simple_datasource_qa initializes the Langgraph tool called [simple_datasource_qa](https://github.com/Tab-SE/tableau_langchain/blob/3ff9047414479cd55d797c18a78f834d57860761/pip_package/langchain_tableau/tools/simple_datasource_qa.py#L101), which can be used for analytical questions and answers on a Tableau Data Source.
# 
# This initializer function:
# 1. Authenticates to Tableau using Tableau's connected-app framework for JWT-based authentication. All the required variables must be defined at runtime or as environment variables.
# 2. Asynchronously queries for the field metadata of the target datasource specified in the datasource_luid variable.
# 3. Grounds on the metadata of the target datasource to transform natural language questions into the json-formatted query payload required to make VDS query-datasource requests.
# 4. Executes a POST request to VDS.
# 5. Formats and returns the results in a structured response.

# In[ ]:


# Initalize simple_datasource_qa for querying Tableau Datasources through VDS
analyze_datasource = initialize_simple_datasource_qa(
    domain=tableau_server,
    site=tableau_site,
    jwt_client_id=tableau_jwt_client_id,
    jwt_secret_id=tableau_jwt_secret_id,
    jwt_secret=tableau_jwt_secret,
    tableau_api_version=tableau_api_version,
    tableau_user=tableau_user,
    datasource_luid=datasource_luid,
    tooling_llm_model=tooling_llm_model,
)

# load the List of Tools to be used by the Agent. In this case we will just load our data source Q&A tool.
tools = [analyze_datasource]


# ## Invocation - Langgraph Example
# First, we'll initlialize the LLM of our choice. Then, we define an agent using a langgraph agent constructor class and invoke it with a query related to the target data source. 

# In[8]:


from IPython.display import Markdown, display

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tableauAgent = create_react_agent(model, tools)

# Run the agent
messages = tableauAgent.invoke(
    {
        "messages": [
            (
                "human",
                "which states sell the most? Are those the same states with the most profits?",
            )
        ]
    }
)
messages
# display(Markdown(messages['messages'][4].content)) #display a nicely formatted answer for successful generations


# ## Chaining
# 
# TODO.

# ## API reference
# 
# TODO.
