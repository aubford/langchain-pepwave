#!/usr/bin/env python
# coding: utf-8

# # Google AlloyDB for PostgreSQL
# 
# > [AlloyDB](https://cloud.google.com/alloydb) is a fully managed relational database service that offers high performance, seamless integration, and impressive scalability. AlloyDB is 100% compatible with PostgreSQL. Extend your database application to build AI-powered experiences leveraging AlloyDB's Langchain integrations.
# 
# This notebook goes over how to use `AlloyDB for PostgreSQL` to store vector embeddings with the `AlloyDBVectorStore` class.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-alloydb-pg-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-alloydb-pg-python/blob/main/docs/vector_store.ipynb)

# ## Before you begin
# 
# To run this notebook, you will need to do the following:
# 
#  * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
#  * [Enable the AlloyDB API](https://console.cloud.google.com/flows/enableapi?apiid=alloydb.googleapis.com)
#  * [Create a AlloyDB cluster and instance.](https://cloud.google.com/alloydb/docs/cluster-create)
#  * [Create a AlloyDB database.](https://cloud.google.com/alloydb/docs/quickstart/create-and-connect)
#  * [Add a User to the database.](https://cloud.google.com/alloydb/docs/database-users/about)

# ### 🦜🔗 Library Installation
# Install the integration library, `langchain-google-alloydb-pg`, and the library for the embedding service, `langchain-google-vertexai`.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-google-alloydb-pg langchain-google-vertexai')


# **Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

# In[ ]:


# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)


# ### 🔐 Authentication
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# * If you are using Colab to run this notebook, use the cell below and continue.
# * If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[1]:


from google.colab import auth

auth.authenticate_user()


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


# ## Basic Usage

# ### Set AlloyDB database values
# Find your database values, in the [AlloyDB Instances page](https://console.cloud.google.com/alloydb/clusters).

# In[4]:


# @title Set Your Values Here { display-mode: "form" }
REGION = "us-central1"  # @param {type: "string"}
CLUSTER = "my-cluster"  # @param {type: "string"}
INSTANCE = "my-primary"  # @param {type: "string"}
DATABASE = "my-database"  # @param {type: "string"}
TABLE_NAME = "vector_store"  # @param {type: "string"}


# ### AlloyDBEngine Connection Pool
# 
# One of the requirements and arguments to establish AlloyDB as a vector store is a `AlloyDBEngine` object. The `AlloyDBEngine`  configures a connection pool to your AlloyDB database, enabling successful connections from your application and following industry best practices.
# 
# To create a `AlloyDBEngine` using `AlloyDBEngine.from_instance()` you need to provide only 5 things:
# 
# 1. `project_id` : Project ID of the Google Cloud Project where the AlloyDB instance is located.
# 1. `region` : Region where the AlloyDB instance is located.
# 1. `cluster`: The name of the AlloyDB cluster.
# 1. `instance` : The name of the AlloyDB instance.
# 1. `database` : The name of the database to connect to on the AlloyDB instance.
# 
# By default, [IAM database authentication](https://cloud.google.com/alloydb/docs/connect-iam) will be used as the method of database authentication. This library uses the IAM principal belonging to the [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) sourced from the environment.
# 
# Optionally, [built-in database authentication](https://cloud.google.com/alloydb/docs/database-users/about) using a username and password to access the AlloyDB database can also be used. Just provide the optional `user` and `password` arguments to `AlloyDBEngine.from_instance()`:
# 
# * `user` : Database user to use for built-in database authentication and login
# * `password` : Database password to use for built-in database authentication and login.
# 

# **Note:** This tutorial demonstrates the async interface. All async methods have corresponding sync methods.

# In[ ]:


from langchain_google_alloydb_pg import AlloyDBEngine

engine = await AlloyDBEngine.afrom_instance(
    project_id=PROJECT_ID,
    region=REGION,
    cluster=CLUSTER,
    instance=INSTANCE,
    database=DATABASE,
)


# ### Initialize a table
# The `AlloyDBVectorStore` class requires a database table. The `AlloyDBEngine` engine has a helper method `init_vectorstore_table()` that can be used to create a table with the proper schema for you.

# In[34]:


await engine.ainit_vectorstore_table(
    table_name=TABLE_NAME,
    vector_size=768,  # Vector size for VertexAI model(textembedding-gecko@latest)
)


# ### Create an embedding class instance
# 
# You can use any [LangChain embeddings model](/docs/integrations/text_embedding/).
# You may need to enable Vertex AI API to use `VertexAIEmbeddings`. We recommend setting the embedding model's version for production, learn more about the [Text embeddings models](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-embeddings).

# In[3]:


# enable Vertex AI API
get_ipython().system('gcloud services enable aiplatform.googleapis.com')


# In[16]:


from langchain_google_vertexai import VertexAIEmbeddings

embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=PROJECT_ID
)


# ### Initialize a default AlloyDBVectorStore

# In[ ]:


from langchain_google_alloydb_pg import AlloyDBVectorStore

store = await AlloyDBVectorStore.create(
    engine=engine,
    table_name=TABLE_NAME,
    embedding_service=embedding,
)


# ### Add texts

# In[ ]:


import uuid

all_texts = ["Apples and oranges", "Cars and airplanes", "Pineapple", "Train", "Banana"]
metadatas = [{"len": len(t)} for t in all_texts]
ids = [str(uuid.uuid4()) for _ in all_texts]

await store.aadd_texts(all_texts, metadatas=metadatas, ids=ids)


# ### Delete texts

# In[ ]:


await store.adelete([ids[1]])


# ### Search for documents

# In[ ]:


query = "I'd like a fruit."
docs = await store.asimilarity_search(query)
print(docs)


# ### Search for documents by vector

# In[ ]:


query_vector = embedding.embed_query(query)
docs = await store.asimilarity_search_by_vector(query_vector, k=2)
print(docs)


# ## Add a Index
# Speed up vector search queries by applying a vector index. Learn more about [vector indexes](https://cloud.google.com/blog/products/databases/faster-similarity-search-performance-with-pgvector-indexes).

# In[ ]:


from langchain_google_alloydb_pg.indexes import IVFFlatIndex

index = IVFFlatIndex()
await store.aapply_vector_index(index)


# ### Re-index

# In[ ]:


await store.areindex()  # Re-index using default index name


# ### Remove an index

# In[ ]:


await store.adrop_vector_index()  # Delete index using default name


# ## Create a custom Vector Store
# A Vector Store can take advantage of relational data to filter similarity searches.
# 
# Create a table with custom metadata columns.

# In[ ]:


from langchain_google_alloydb_pg import Column

# Set table name
TABLE_NAME = "vectorstore_custom"

await engine.ainit_vectorstore_table(
    table_name=TABLE_NAME,
    vector_size=768,  # VertexAI model: textembedding-gecko@latest
    metadata_columns=[Column("len", "INTEGER")],
)


# Initialize AlloyDBVectorStore
custom_store = await AlloyDBVectorStore.create(
    engine=engine,
    table_name=TABLE_NAME,
    embedding_service=embedding,
    metadata_columns=["len"],
    # Connect to a existing VectorStore by customizing the table schema:
    # id_column="uuid",
    # content_column="documents",
    # embedding_column="vectors",
)


# ### Search for documents with metadata filter

# In[ ]:


import uuid

# Add texts to the Vector Store
all_texts = ["Apples and oranges", "Cars and airplanes", "Pineapple", "Train", "Banana"]
metadatas = [{"len": len(t)} for t in all_texts]
ids = [str(uuid.uuid4()) for _ in all_texts]
await store.aadd_texts(all_texts, metadatas=metadatas, ids=ids)

# Use filter on search
docs = await custom_store.asimilarity_search_by_vector(query_vector, filter="len >= 6")

print(docs)

