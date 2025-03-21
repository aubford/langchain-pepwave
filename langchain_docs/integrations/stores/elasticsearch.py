#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Elasticsearch
---
# # ElasticsearchEmbeddingsCache
# 
# This will help you get started with Elasticsearch [key-value stores](/docs/concepts/key_value_stores). For detailed documentation of all `ElasticsearchEmbeddingsCache` features and configurations head to the [API reference](https://python.langchain.com/api_reference/elasticsearch/cache/langchain_elasticsearch.cache.ElasticsearchEmbeddingsCache.html).
# 
# ## Overview
# 
# The `ElasticsearchEmbeddingsCache` is a `ByteStore` implementation that uses your Elasticsearch instance for efficient storage and retrieval of embeddings.
# 
# ### Integration details
# 
# | Class | Package | Local | JS support | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: |
# | [ElasticsearchEmbeddingsCache](https://python.langchain.com/api_reference/elasticsearch/cache/langchain_elasticsearch.cache.ElasticsearchEmbeddingsCache.html) | [langchain_elasticsearch](https://python.langchain.com/api_reference/elasticsearch/index.html) | ✅ | ❌ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain_elasticsearch?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain_elasticsearch?style=flat-square&label=%20) |
# 
# ## Setup
# 
# To create a `ElasticsearchEmbeddingsCache` byte store, you'll need an Elasticsearch cluster. You can [set one up locally](https://www.elastic.co/downloads/elasticsearch) or create an [Elastic account](https://www.elastic.co/elasticsearch).

# ### Installation
# 
# The LangChain `ElasticsearchEmbeddingsCache` integration lives in the `__package_name__` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain_elasticsearch')


# ## Instantiation
# 
# Now we can instantiate our byte store:

# In[4]:


from langchain_elasticsearch import ElasticsearchEmbeddingsCache

# Example config for a locally running Elasticsearch instance
kv_store = ElasticsearchEmbeddingsCache(
    es_url="https://localhost:9200",
    index_name="llm-chat-cache",
    metadata={"project": "my_chatgpt_project"},
    namespace="my_chatgpt_project",
    es_user="elastic",
    es_password="<GENERATED PASSWORD>",
    es_params={
        "ca_certs": "~/http_ca.crt",
    },
)


# ## Usage
# 
# You can set data under keys like this using the `mset` method:

# In[5]:


kv_store.mset(
    [
        ["key1", b"value1"],
        ["key2", b"value2"],
    ]
)

kv_store.mget(
    [
        "key1",
        "key2",
    ]
)


# And you can delete data using the `mdelete` method:

# In[6]:


kv_store.mdelete(
    [
        "key1",
        "key2",
    ]
)

kv_store.mget(
    [
        "key1",
        "key2",
    ]
)


# ## Use as an embeddings cache
# 
# Like other `ByteStores`, you can use an `ElasticsearchEmbeddingsCache` instance for [persistent caching in document ingestion](/docs/how_to/caching_embeddings/) for RAG.
# 
# However, cached vectors won't be searchable by default. The developer can customize the building of the Elasticsearch document in order to add indexed vector field.
# 
# This can be done by subclassing and overriding methods:

# In[ ]:


from typing import Any, Dict, List


class SearchableElasticsearchStore(ElasticsearchEmbeddingsCache):
    @property
    def mapping(self) -> Dict[str, Any]:
        mapping = super().mapping
        mapping["mappings"]["properties"]["vector"] = {
            "type": "dense_vector",
            "dims": 1536,
            "index": True,
            "similarity": "dot_product",
        }
        return mapping

    def build_document(self, llm_input: str, vector: List[float]) -> Dict[str, Any]:
        body = super().build_document(llm_input, vector)
        body["vector"] = vector
        return body


# When overriding the mapping and the document building, please only make additive modifications, keeping the base mapping intact.

# ## API reference
# 
# For detailed documentation of all `ElasticsearchEmbeddingsCache` features and configurations, head to the API reference: https://python.langchain.com/api_reference/elasticsearch/cache/langchain_elasticsearch.cache.ElasticsearchEmbeddingsCache.html
