#!/usr/bin/env python
# coding: utf-8

# # JSONLoader
# 
# This notebook provides a quick overview for getting started with JSON [document loader](https://python.langchain.com/docs/concepts/document_loaders). For detailed documentation of all JSONLoader features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.json_loader.JSONLoader.html).
# 
# - TODO: Add any other relevant links, like information about underlying API, etc.
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/document_loaders/file_loaders/json/)|
# | :--- | :--- | :---: | :---: |  :---: |
# | [JSONLoader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.json_loader.JSONLoader.html) | [langchain_community](https://python.langchain.com/api_reference/community/index.html) | ✅ | ❌ | ✅ | 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: | 
# | JSONLoader | ✅ | ❌ | 
# 
# ## Setup
# 
# To access JSON document loader you'll need to install the `langchain-community` integration package as well as the ``jq`` python package.
# 
# ### Credentials
# 
# No credentials are required to use the `JSONLoader` class.

# To enable automated tracing of your model calls, set your [LangSmith](https://docs.smith.langchain.com/) API key:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# Install **langchain_community** and **jq**:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain_community jq')


# ## Initialization
# 
# Now we can instantiate our model object and load documents:
# 
# - TODO: Update model instantiation with relevant params.

# In[1]:


from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="./example_data/facebook_chat.json",
    jq_schema=".messages[].content",
    text_content=False,
)


# ## Load

# In[2]:


docs = loader.load()
docs[0]


# In[3]:


print(docs[0].metadata)


# ## Lazy Load

# In[4]:


pages = []
for doc in loader.lazy_load():
    pages.append(doc)
    if len(pages) >= 10:
        # do some paged operation, e.g.
        # index.upsert(pages)

        pages = []


# ## Read from JSON Lines file
# 
# If you want to load documents from a JSON Lines file, you pass `json_lines=True`
# and specify `jq_schema` to extract `page_content` from a single JSON object.

# In[5]:


loader = JSONLoader(
    file_path="./example_data/facebook_chat_messages.jsonl",
    jq_schema=".content",
    text_content=False,
    json_lines=True,
)

docs = loader.load()
print(docs[0])


# ## Read specific content keys
# 
# Another option is to set `jq_schema='.'` and provide a `content_key` in order to only load specific content:

# In[6]:


loader = JSONLoader(
    file_path="./example_data/facebook_chat_messages.jsonl",
    jq_schema=".",
    content_key="sender_name",
    json_lines=True,
)

docs = loader.load()
print(docs[0])


# ## JSON file with jq schema `content_key`
# 
# To load documents from a JSON file using the `content_key` within the jq schema, set `is_content_key_jq_parsable=True`. Ensure that `content_key` is compatible and can be parsed using the jq schema.

# In[7]:


loader = JSONLoader(
    file_path="./example_data/facebook_chat.json",
    jq_schema=".messages[]",
    content_key=".content",
    is_content_key_jq_parsable=True,
)

docs = loader.load()
print(docs[0])


# ## Extracting metadata
# 
# Generally, we want to include metadata available in the JSON file into the documents that we create from the content.
# 
# The following demonstrates how metadata can be extracted using the `JSONLoader`.
# 
# There are some key changes to be noted. In the previous example where we didn't collect the metadata, we managed to directly specify in the schema where the value for the `page_content` can be extracted from.
# 
# In this example, we have to tell the loader to iterate over the records in the `messages` field. The jq_schema then has to be `.messages[]`
# 
# This allows us to pass the records (dict) into the `metadata_func` that has to be implemented. The `metadata_func` is responsible for identifying which pieces of information in the record should be included in the metadata stored in the final `Document` object.
# 
# Additionally, we now have to explicitly specify in the loader, via the `content_key` argument, the key from the record where the value for the `page_content` needs to be extracted from.

# In[8]:


# Define the metadata extraction function.
def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["sender_name"] = record.get("sender_name")
    metadata["timestamp_ms"] = record.get("timestamp_ms")

    return metadata


loader = JSONLoader(
    file_path="./example_data/facebook_chat.json",
    jq_schema=".messages[]",
    content_key="content",
    metadata_func=metadata_func,
)

docs = loader.load()
print(docs[0].metadata)


# ## API reference
# 
# For detailed documentation of all JSONLoader features and configurations head to the API reference: https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.json_loader.JSONLoader.html
