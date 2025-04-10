#!/usr/bin/env python
# coding: utf-8

# # Google Memorystore for Redis
# 
# > [Google Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis/memorystore-for-redis-overview) is a fully-managed service that is powered by the Redis in-memory data store to build application caches that provide sub-millisecond data access. Extend your database application to build AI-powered experiences leveraging Memorystore for Redis's Langchain integrations.
# 
# This notebook goes over how to use [Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis/memorystore-for-redis-overview) to store vector embeddings with the `MemorystoreVectorStore` class.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-memorystore-redis-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-memorystore-redis-python/blob/main/docs/vector_store.ipynb)

# ## Pre-reqs

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
# * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
# * [Enable the Memorystore for Redis API](https://console.cloud.google.com/flows/enableapi?apiid=redis.googleapis.com)
# * [Create a Memorystore for Redis instance](https://cloud.google.com/memorystore/docs/redis/create-instance-console). Ensure that the version is greater than or equal to 7.2.

# ### 🦜🔗 Library Installation
# 
# The integration lives in its own `langchain-google-memorystore-redis` package, so we need to install it.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -upgrade --quiet langchain-google-memorystore-redis langchain')


# **Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

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
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# * If you are using Colab to run this notebook, use the cell below and continue.
# * If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[ ]:


from google.colab import auth

auth.authenticate_user()


# ## Basic Usage

# ### Initialize a Vector Index

# In[13]:


import redis
from langchain_google_memorystore_redis import (
    DistanceStrategy,
    HNSWConfig,
    RedisVectorStore,
)

# Connect to a Memorystore for Redis instance
redis_client = redis.from_url("redis://127.0.0.1:6379")

# Configure HNSW index with descriptive parameters
index_config = HNSWConfig(
    name="my_vector_index", distance_strategy=DistanceStrategy.COSINE, vector_size=128
)

# Initialize/create the vector store index
RedisVectorStore.init_index(client=redis_client, index_config=index_config)


# ### Prepare Documents
# 
# Text needs processing and numerical representation before interacting with a vector store. This involves:
# 
# * Loading Text: The TextLoader obtains text data from a file (e.g., "state_of_the_union.txt").
# * Text Splitting: The CharacterTextSplitter breaks the text into smaller chunks for embedding models.

# In[14]:


from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("./state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)


# ### Add Documents to the Vector Store
# 
# After text preparation and embedding generation, the following methods insert them into the Redis vector store.

# #### Method 1: Classmethod for Direct Insertion
# 
# This approach combines embedding creation and insertion into a single step using the from_documents classmethod:

# In[ ]:


from langchain_community.embeddings.fake import FakeEmbeddings

embeddings = FakeEmbeddings(size=128)
redis_client = redis.from_url("redis://127.0.0.1:6379")
rvs = RedisVectorStore.from_documents(
    docs, embedding=embeddings, client=redis_client, index_name="my_vector_index"
)


# #### Method 2: Instance-Based Insertion
# This approach offers flexibility when working with a new or existing RedisVectorStore:
# 
# * [Optional] Create a RedisVectorStore Instance: Instantiate a RedisVectorStore object for customization. If you already have an instance, proceed to the next step.
# * Add Text with Metadata: Provide raw text and metadata to the instance. Embedding generation and insertion into the vector store are handled automatically.

# In[ ]:


rvs = RedisVectorStore(
    client=redis_client, index_name="my_vector_index", embeddings=embeddings
)
ids = rvs.add_texts(
    texts=[d.page_content for d in docs], metadatas=[d.metadata for d in docs]
)


# ### Perform a Similarity Search (KNN)
# 
# With the vector store populated, it's possible to search for text semantically similar to a query.  Here's how to use KNN (K-Nearest Neighbors) with default settings:
# 
# * Formulate the Query: A natural language question expresses the search intent (e.g., "What did the president say about Ketanji Brown Jackson").
# * Retrieve Similar Results: The `similarity_search` method finds items in the vector store closest to the query in meaning.

# In[ ]:


import pprint

query = "What did the president say about Ketanji Brown Jackson"
knn_results = rvs.similarity_search(query=query)
pprint.pprint(knn_results)


# ### Perform a Range-Based Similarity Search
# 
# Range queries provide more control by specifying a desired similarity threshold along with the query text:
# 
# * Formulate the Query: A natural language question defines the search intent.
# * Set Similarity Threshold: The distance_threshold parameter determines how close a match must be considered relevant.
# * Retrieve Results: The `similarity_search_with_score` method finds items from the vector store that fall within the specified similarity threshold.

# In[ ]:


rq_results = rvs.similarity_search_with_score(query=query, distance_threshold=0.8)
pprint.pprint(rq_results)


# ### Perform a Maximal Marginal Relevance (MMR) Search
# 
# MMR queries aim to find results that are both relevant to the query and diverse from each other, reducing redundancy in search results.
# 
# * Formulate the Query: A natural language question defines the search intent.
# * Balance Relevance and Diversity: The lambda_mult parameter controls the trade-off between strict relevance and promoting variety in the results.
# * Retrieve MMR Results: The `max_marginal_relevance_search` method returns items that optimize the combination of relevance and diversity based on the lambda setting.

# In[ ]:


mmr_results = rvs.max_marginal_relevance_search(query=query, lambda_mult=0.90)
pprint.pprint(mmr_results)


# ## Use the Vector Store as a Retriever
# 
# For seamless integration with other LangChain components, a vector store can be converted into a Retriever. This offers several advantages:
# 
# * LangChain Compatibility: Many LangChain tools and methods are designed to directly interact with retrievers.
# * Ease of Use: The `as_retriever()` method converts the vector store into a format that simplifies querying.

# In[ ]:


retriever = rvs.as_retriever()
results = retriever.invoke(query)
pprint.pprint(results)


# ## Clean up

# ### Delete Documents from the Vector Store
# 
# Occasionally, it's necessary to remove documents (and their associated vectors) from the vector store.  The `delete` method provides this functionality.

# In[ ]:


rvs.delete(ids)


# ### Delete a Vector Index
# 
# There might be circumstances where the deletion of an existing vector index is necessary. Common reasons include:
# 
# * Index Configuration Changes: If index parameters need modification, it's often required to delete and recreate the index.
# * Storage Management: Removing unused indices can help free up space within the Redis instance.
# 
# Caution: Vector index deletion is an irreversible operation. Be certain that the stored vectors and search functionality are no longer required before proceeding.

# In[22]:


# Delete the vector index
RedisVectorStore.drop_index(client=redis_client, index_name="my_vector_index")

