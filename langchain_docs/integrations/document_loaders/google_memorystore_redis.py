#!/usr/bin/env python
# coding: utf-8

# # Google Memorystore for Redis
# 
# > [Google Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis/memorystore-for-redis-overview) is a fully-managed service that is powered by the Redis in-memory data store to build application caches that provide sub-millisecond data access. Extend your database application to build AI-powered experiences leveraging Memorystore for Redis's Langchain integrations.
# 
# This notebook goes over how to use [Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis/memorystore-for-redis-overview) to [save, load and delete langchain documents](/docs/how_to#document-loaders) with `MemorystoreDocumentLoader` and `MemorystoreDocumentSaver`.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-memorystore-redis-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-memorystore-redis-python/blob/main/docs/document_loader.ipynb)

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
# * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
# * [Enable the Memorystore for Redis API](https://console.cloud.google.com/flows/enableapi?apiid=redis.googleapis.com)
# * [Create a Memorystore for Redis instance](https://cloud.google.com/memorystore/docs/redis/create-instance-console). Ensure that the version is greater than or equal to 5.0.
# 
# After confirmed access to database in the runtime environment of this notebook, filling the following values and run the cell before running example scripts.

# In[ ]:


# @markdown Please specify an endpoint associated with the instance and a key prefix for demo purpose.
ENDPOINT = "redis://127.0.0.1:6379"  # @param {type:"string"}
KEY_PREFIX = "doc:"  # @param {type:"string"}


# ### 🦜🔗 Library Installation
# 
# The integration lives in its own `langchain-google-memorystore-redis` package, so we need to install it.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -upgrade --quiet langchain-google-memorystore-redis')


# **Colab only**: Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

# In[ ]:


# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)


# ### ☁ Set Your Google Cloud Project
# Set your Google Cloud project so that you can leverage Google Cloud resources within this notebook.
# 
# If you don't know your project ID, try the following:
# 
# * Run `gcloud config list`.
# * Run `gcloud projects list`.
# * See the support page: [Locate the project ID](https://support.google.com/googleapi/answer/7014113).

# In[ ]:


# @markdown Please fill in the value below with your Google Cloud project ID and then run the cell.

PROJECT_ID = "my-project-id"  # @param {type:"string"}

# Set the project id
get_ipython().system('gcloud config set project {PROJECT_ID}')


# ### 🔐 Authentication
# 
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# - If you are using Colab to run this notebook, use the cell below and continue.
# - If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[ ]:


from google.colab import auth

auth.authenticate_user()


# ## Basic Usage

# ### Save documents
# 
# Save langchain documents with `MemorystoreDocumentSaver.add_documents(<documents>)`. To initialize `MemorystoreDocumentSaver` class you need to provide 2 things:
# 
# 1. `client` - A `redis.Redis` client object.
# 1. `key_prefix` - A prefix for the keys to store Documents in Redis.
# 
# The Documents will be stored into randomly generated keys with the specified prefix of `key_prefix`. Alternatively, you can designate the suffixes of the keys by specifying `ids` in the `add_documents` method.

# In[ ]:


import redis
from langchain_core.documents import Document
from langchain_google_memorystore_redis import MemorystoreDocumentSaver

test_docs = [
    Document(
        page_content="Apple Granny Smith 150 0.99 1",
        metadata={"fruit_id": 1},
    ),
    Document(
        page_content="Banana Cavendish 200 0.59 0",
        metadata={"fruit_id": 2},
    ),
    Document(
        page_content="Orange Navel 80 1.29 1",
        metadata={"fruit_id": 3},
    ),
]
doc_ids = [f"{i}" for i in range(len(test_docs))]

redis_client = redis.from_url(ENDPOINT)
saver = MemorystoreDocumentSaver(
    client=redis_client,
    key_prefix=KEY_PREFIX,
    content_field="page_content",
)
saver.add_documents(test_docs, ids=doc_ids)


# ### Load documents
# 
# Initialize a loader that loads all documents stored in the Memorystore for Redis instance with a specific prefix.
# 
# Load langchain documents with `MemorystoreDocumentLoader.load()` or `MemorystoreDocumentLoader.lazy_load()`. `lazy_load` returns a generator that only queries database during the iteration. To initialize `MemorystoreDocumentLoader` class you need to provide:
# 
# 1. `client` - A `redis.Redis` client object.
# 1. `key_prefix` - A prefix for the keys to store Documents in Redis.

# In[ ]:


import redis
from langchain_google_memorystore_redis import MemorystoreDocumentLoader

redis_client = redis.from_url(ENDPOINT)
loader = MemorystoreDocumentLoader(
    client=redis_client,
    key_prefix=KEY_PREFIX,
    content_fields=set(["page_content"]),
)
for doc in loader.lazy_load():
    print("Loaded documents:", doc)


# ### Delete documents
# 
# Delete all of keys with the specified prefix in the Memorystore for Redis instance with `MemorystoreDocumentSaver.delete()`. You can also specify the suffixes of the keys if you know.

# In[ ]:


docs = loader.load()
print("Documents before delete:", docs)

saver.delete(ids=[0])
print("Documents after delete:", loader.load())

saver.delete()
print("Documents after delete all:", loader.load())


# ## Advanced Usage

# ### Customize Document Page Content & Metadata
# 
# When initializing a loader with more than 1 content field, the `page_content` of the loaded Documents will contain a JSON-encoded string with top level fields equal to the specified fields in `content_fields`.
# 
# If the `metadata_fields` are specified, the `metadata` field of the loaded Documents will only have the top level fields equal to the specified `metadata_fields`. If any of the values of the metadata fields is stored as a JSON-encoded string, it will be decoded prior to being loaded to the metadata fields.

# In[ ]:


loader = MemorystoreDocumentLoader(
    client=redis_client,
    key_prefix=KEY_PREFIX,
    content_fields=set(["content_field_1", "content_field_2"]),
    metadata_fields=set(["title", "author"]),
)

