#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Local Filesystem
---
# # LocalFileStore
# 
# This will help you get started with local filesystem [key-value stores](/docs/concepts/key_value_stores). For detailed documentation of all LocalFileStore features and configurations head to the [API reference](https://python.langchain.com/api_reference/langchain/storage/langchain.storage.file_system.LocalFileStore.html).
# 
# ## Overview
# 
# The `LocalFileStore` is a persistent implementation of `ByteStore` that stores everything in a folder of your choosing. It's useful if you're using a single machine and are tolerant of files being added or deleted.
# 
# ### Integration details
# 
# | Class | Package | Local | [JS support](https://js.langchain.com/docs/integrations/stores/file_system) | Package downloads | Package latest |
# | :--- | :--- | :---: | :---: |  :---: | :---: |
# | [LocalFileStore](https://python.langchain.com/api_reference/langchain/storage/langchain.storage.file_system.LocalFileStore.html) | [langchain](https://python.langchain.com/api_reference/langchain/index.html) | ✅ | ✅ | ![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain?style=flat-square&label=%20) | ![PyPI - Version](https://img.shields.io/pypi/v/langchain?style=flat-square&label=%20) |

# ### Installation
# 
# The LangChain `LocalFileStore` integration lives in the `langchain` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain')


# ## Instantiation
# 
# Now we can instantiate our byte store:

# In[2]:


from pathlib import Path

from langchain.storage import LocalFileStore

root_path = Path.cwd() / "data"  # can also be a path set by a string

kv_store = LocalFileStore(root_path)


# ## Usage
# 
# You can set data under keys like this using the `mset` method:

# In[3]:


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


# You can see the created files in your `data` folder:

# In[4]:


get_ipython().system('ls {root_path}')


# And you can delete data using the `mdelete` method:

# In[5]:


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


# ## API reference
# 
# For detailed documentation of all `LocalFileStore` features and configurations, head to the API reference: https://python.langchain.com/api_reference/langchain/storage/langchain.storage.file_system.LocalFileStore.html
