#!/usr/bin/env python
# coding: utf-8

# # Arcee
# 
# >[Arcee](https://www.arcee.ai/about/about-us) helps with the development of the SLMs—small, specialized, secure, and scalable language models.
# 
# This notebook demonstrates how to use the `ArceeRetriever` class to retrieve relevant document(s) for Arcee's `Domain Adapted Language Models` (`DALMs`).

# ### Setup
# 
# Before using `ArceeRetriever`, make sure the Arcee API key is set as `ARCEE_API_KEY` environment variable. You can also pass the api key as a named parameter.

# In[ ]:


from langchain_community.retrievers import ArceeRetriever

retriever = ArceeRetriever(
    model="DALM-PubMed",
    # arcee_api_key="ARCEE-API-KEY" # if not already set in the environment
)


# ### Additional Configuration
# 
# You can also configure `ArceeRetriever`'s parameters such as `arcee_api_url`, `arcee_app_url`, and `model_kwargs` as needed.
# Setting the `model_kwargs` at the object initialization uses the filters and size as default for all the subsequent retrievals.

# In[ ]:


retriever = ArceeRetriever(
    model="DALM-PubMed",
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


# ### Retrieving documents
# You can retrieve relevant documents from uploaded contexts by providing a query. Here's an example:

# In[ ]:


query = "Can AI-driven music therapy contribute to the rehabilitation of patients with disorders of consciousness?"
documents = retriever.invoke(query)


# ### Additional parameters
# 
# Arcee allows you to apply `filters` and set the `size` (in terms of count) of retrieved document(s). Filters help narrow down the results. Here's how to use these parameters:

# In[ ]:


# Define filters
filters = [
    {"field_name": "document", "filter_type": "fuzzy_search", "value": "Music"},
    {"field_name": "year", "filter_type": "strict_search", "value": "1905"},
]

# Retrieve documents with filters and size params
documents = retriever.invoke(query, size=5, filters=filters)

