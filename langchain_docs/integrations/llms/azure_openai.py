#!/usr/bin/env python
# coding: utf-8

# # Azure OpenAI
# 
# :::caution
# You are currently on a page documenting the use of Azure OpenAI [text completion models](/docs/concepts/text_llms). The latest and most popular Azure OpenAI models are [chat completion models](/docs/concepts/chat_models).
# 
# Unless you are specifically using `gpt-3.5-turbo-instruct`, you are probably looking for [this page instead](/docs/integrations/chat/azure_chat_openai/).
# :::
# 
# This page goes over how to use LangChain with [Azure OpenAI](https://aka.ms/azure-openai).
# 
# The Azure OpenAI API is compatible with OpenAI's API.  The `openai` Python package makes it easy to use both OpenAI and Azure OpenAI.  You can call Azure OpenAI the same way you call OpenAI with the exceptions noted below.
# 
# ## API configuration
# You can configure the `openai` package to use Azure OpenAI using environment variables.  The following is for `bash`:
# 
# ```bash
# # The API version you want to use: set this to `2023-12-01-preview` for the released version.
# export OPENAI_API_VERSION=2023-12-01-preview
# # The base URL for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource.
# export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
# # The API key for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource.
# export AZURE_OPENAI_API_KEY=<your Azure OpenAI API key>
# ```
# 
# Alternatively, you can configure the API right within your running Python environment:
# 
# ```python
# import os
# os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
# ```
# 
# ## Azure Active Directory Authentication
# There are two ways you can authenticate to Azure OpenAI:
# - API Key
# - Azure Active Directory (AAD)
# 
# Using the API key is the easiest way to get started. You can find your API key in the Azure portal under your Azure OpenAI resource.
# 
# However, if you have complex security requirements - you may want to use Azure Active Directory. You can find more information on how to use AAD with Azure OpenAI [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity).
# 
# If you are developing locally, you will need to have the Azure CLI installed and be logged in. You can install the Azure CLI [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli). Then, run `az login` to log in.
# 
# Add a role an Azure role assignment `Cognitive Services OpenAI User` scoped to your Azure OpenAI resource. This will allow you to get a token from AAD to use with Azure OpenAI. You can grant this role assignment to a user, group, service principal, or managed identity. For more information about Azure OpenAI RBAC roles see [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control).
# 
# To use AAD in Python with LangChain, install the `azure-identity` package. Then, set `OPENAI_API_TYPE` to `azure_ad`. Next, use the `DefaultAzureCredential` class to get a token from AAD by calling `get_token` as shown below. Finally, set the `OPENAI_API_KEY` environment variable to the token value.
# 
# ```python
# import os
# from azure.identity import DefaultAzureCredential
# 
# # Get the Azure Credential
# credential = DefaultAzureCredential()
# 
# # Set the API type to `azure_ad`
# os.environ["OPENAI_API_TYPE"] = "azure_ad"
# # Set the API_KEY to the token from the Azure credential
# os.environ["OPENAI_API_KEY"] = credential.get_token("https://cognitiveservices.azure.com/.default").token
# ```
# 
# The `DefaultAzureCredential` class is an easy way to get started with AAD authentication. You can also customize the credential chain if necessary. In the example shown below, we first try Managed Identity, then fall back to the Azure CLI. This is useful if you are running your code in Azure, but want to develop locally.
# 
# ```python
# from azure.identity import ChainedTokenCredential, ManagedIdentityCredential, AzureCliCredential
# 
# credential = ChainedTokenCredential(
#     ManagedIdentityCredential(),
#     AzureCliCredential()
# )
# ```
# 
# ## Deployments
# With Azure OpenAI, you set up your own deployments of the common GPT-3 and Codex models.  When calling the API, you need to specify the deployment you want to use.
# 
# _**Note**: These docs are for the Azure text completion models. Models like GPT-4 are chat models. They have a slightly different interface, and can be accessed via the `AzureChatOpenAI` class. For docs on Azure chat see [Azure Chat OpenAI documentation](/docs/integrations/chat/azure_chat_openai)._
# 
# Let's say your deployment name is `gpt-35-turbo-instruct-prod`.  In the `openai` Python API, you can specify this deployment with the `engine` parameter.  For example:
# 
# ```python
# import openai
# 
# client = openai.AzureOpenAI(
#     api_version="2023-12-01-preview",
# )
# 
# response = client.completions.create(
#     model="gpt-35-turbo-instruct-prod",
#     prompt="Test prompt"
# )
# ```
# 

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-openai')


# In[1]:


import os

os.environ["OPENAI_API_VERSION"] = "2023-12-01-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["AZURE_OPENAI_API_KEY"] = "..."


# In[2]:


# Import Azure OpenAI
from langchain_openai import AzureOpenAI


# In[3]:


# Create an instance of Azure OpenAI
# Replace the deployment name with your own
llm = AzureOpenAI(
    deployment_name="gpt-35-turbo-instruct-0914",
)


# In[5]:


# Run the LLM
llm.invoke("Tell me a joke")


# We can also print the LLM and see its custom print.

# In[6]:


print(llm)


# In[ ]:




