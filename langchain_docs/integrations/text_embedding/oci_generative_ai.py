#!/usr/bin/env python
# coding: utf-8

# # Oracle Cloud Infrastructure Generative AI

# Oracle Cloud Infrastructure (OCI) Generative AI is a fully managed service that provides a set of state-of-the-art, customizable large language models (LLMs), that cover a wide range of use cases, and which are available through a single API.
# Using the OCI Generative AI service you can access ready-to-use pretrained models, or create and host your own fine-tuned custom models based on your own data on dedicated AI clusters. Detailed documentation of the service and API is available __[here](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)__ and __[here](https://docs.oracle.com/en-us/iaas/api/#/en/generative-ai/20231130/)__.
# 
# This notebook explains how to use OCI's Genrative AI models with LangChain.

# ### Prerequisite
# We will need to install the oci sdk

# In[ ]:


get_ipython().system('pip install -U oci')


# ### OCI Generative AI API endpoint 
# https://inference.generativeai.us-chicago-1.oci.oraclecloud.com

# ## Authentication
# The authentication methods supported for this langchain integration are:
# 
# 1. API Key
# 2. Session token
# 3. Instance principal
# 4. Resource principal 
# 
# These follows the standard SDK authentication methods detailed __[here](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm)__.
#  

# ## Usage

# In[ ]:


from langchain_community.embeddings import OCIGenAIEmbeddings

# use default authN method API-key
embeddings = OCIGenAIEmbeddings(
    model_id="MY_EMBEDDING_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)


query = "This is a query in English."
response = embeddings.embed_query(query)
print(response)

documents = ["This is a sample document", "and here is another one"]
response = embeddings.embed_documents(documents)
print(response)


# In[ ]:


# Use Session Token to authN
embeddings = OCIGenAIEmbeddings(
    model_id="MY_EMBEDDING_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
    auth_type="SECURITY_TOKEN",
    auth_profile="MY_PROFILE",  # replace with your profile name
    auth_file_location="MY_CONFIG_FILE_LOCATION",  # replace with file location where profile name configs present
)


query = "This is a sample query"
response = embeddings.embed_query(query)
print(response)

documents = ["This is a sample document", "and here is another one"]
response = embeddings.embed_documents(documents)
print(response)

