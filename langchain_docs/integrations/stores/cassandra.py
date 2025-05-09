#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Cassandra
---
# # CassandraByteStore
# 
# This will help you get started with Cassandra [key-value stores](/docs/concepts/key_value_stores). For detailed documentation of all `CassandraByteStore` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/storage/langchain_community.storage.cassandra.CassandraByteStore.html).
# 
# ## Overview
# 
# [Cassandra](https://cassandra.apache.org/) is a NoSQL, row-oriented, highly scalable and highly available database.
# 
# ### Integration details
# 
# | Class | Package | Local | [JS support](https://js.langchain.com/docs/integrations/stores/cassandra_storage) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: |
# | [CassandraByteStore](https://python.langchain.com/api_reference/community/storage/langchain_community.storage.cassandra.CassandraByteStore.html) | [langchain_community](https://python.langchain.com/api_reference/community/index.html) | ✅ | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain_community?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain_community?style=flat-square&label=%20) |
# 
# ## Setup
# 
# The `CassandraByteStore` is an implementation of `ByteStore` that stores the data in your Cassandra instance.
# The store keys must be strings and will be mapped to the `row_id` column of the Cassandra table.
# The store `bytes` values are mapped to the `body_blob` column of the Cassandra table.

# ### Installation
# 
# The LangChain `CassandraByteStore` integration lives in the `langchain_community` package. You'll also need to install the `cassio` package or the `cassandra-driver` package as a peer dependency depending on which initialization method you're using:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain_community')
get_ipython().run_line_magic('pip', 'install -qU cassandra-driver')
get_ipython().run_line_magic('pip', 'install -qU cassio')


# You'll also need to create a `cassandra.cluster.Session` object, as described in the [Cassandra driver documentation](https://docs.datastax.com/en/developer/python-driver/latest/api/cassandra/cluster/#module-cassandra.cluster). The details vary (e.g. with network settings and authentication), but this might be something like:

# ## Instantiation
# 
# You'll first need to create a `cassandra.cluster.Session` object, as described in the [Cassandra driver documentation](https://docs.datastax.com/en/developer/python-driver/latest/api/cassandra/cluster/#module-cassandra.cluster). The details vary (e.g. with network settings and authentication), but this might be something like:

# In[ ]:


from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect()


# Then you can create your store! You'll also need to provide the name of an existing keyspace of the Cassandra instance:

# In[ ]:


from langchain_community.storage import CassandraByteStore

kv_store = CassandraByteStore(
    table="my_store",
    session=session,
    keyspace="<YOUR KEYSPACE>",
)


# ## Usage
# 
# You can set data under keys like this using the `mset` method:

# In[ ]:


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

# In[ ]:


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


# ## Init using `cassio`
# 
# It's also possible to use cassio to configure the session and keyspace.

# In[ ]:


import cassio

cassio.init(contact_points="127.0.0.1", keyspace="<YOUR KEYSPACE>")

store = CassandraByteStore(
    table="my_store",
)

store.mset([("k1", b"v1"), ("k2", b"v2")])
print(store.mget(["k1", "k2"]))


# ## API reference
# 
# For detailed documentation of all `CassandraByteStore` features and configurations, head to the API reference: https://python.langchain.com/api_reference/community/storage/langchain_community.storage.cassandra.CassandraByteStore.html
