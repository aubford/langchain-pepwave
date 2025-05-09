#!/usr/bin/env python
# coding: utf-8

# # Arcee
# This notebook demonstrates how to use the `Arcee` class for generating text using Arcee's Domain Adapted Language Models (DALMs).

# In[ ]:


##Installing the langchain packages needed to use the integration
get_ipython().run_line_magic('pip', 'install -qU langchain-community')


# ### Setup
# 
# Before using Arcee, make sure the Arcee API key is set as `ARCEE_API_KEY` environment variable. You can also pass the api key as a named parameter.

# In[ ]:


from langchain_community.llms import Arcee

# Create an instance of the Arcee class
arcee = Arcee(
    model="DALM-PubMed",
    # arcee_api_key="ARCEE-API-KEY" # if not already set in the environment
)


# ### Additional Configuration
# 
# You can also configure Arcee's parameters such as `arcee_api_url`, `arcee_app_url`, and `model_kwargs` as needed.
# Setting the `model_kwargs` at the object initialization uses the parameters as default for all the subsequent calls to the generate response.

# In[ ]:


arcee = Arcee(
    model="DALM-Patent",
    # arcee_api_key="ARCEE-API-KEY", # if not already set in the environment
    arcee_api_url="https://custom-api.arcee.ai",  # default is https://api.arcee.ai
    arcee_app_url="https://custom-app.arcee.ai",  # default is https://app.arcee.ai
    model_kwargs={
        "size": 5,
        "filters": [
            {
                "field_name": "document",
                "filter_type": "fuzzy_search",
                "value": "Einstein",
            }
        ],
    },
)


# ### Generating Text
# 
# You can generate text from Arcee by providing a prompt. Here's an example:

# In[ ]:


# Generate text
prompt = "Can AI-driven music therapy contribute to the rehabilitation of patients with disorders of consciousness?"
response = arcee(prompt)


# ### Additional parameters
# 
# Arcee allows you to apply `filters` and set the `size` (in terms of count) of retrieved document(s) to aid text generation. Filters help narrow down the results. Here's how to use these parameters:
# 
# 
# 

# In[ ]:


# Define filters
filters = [
    {"field_name": "document", "filter_type": "fuzzy_search", "value": "Einstein"},
    {"field_name": "year", "filter_type": "strict_search", "value": "1905"},
]

# Generate text with filters and size params
response = arcee(prompt, size=5, filters=filters)

