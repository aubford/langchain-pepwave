#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Firestore
---
# # Google Firestore (Native Mode)
# 
# > [Firestore](https://cloud.google.com/firestore) is a serverless document-oriented database that scales to meet any demand. Extend your database application to build AI-powered experiences leveraging Firestore's Langchain integrations.
# 
# This notebook goes over how to use [Firestore](https://cloud.google.com/firestore) to to store vectors and query them using the `FirestoreVectorStore` class.
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-firestore-python/blob/main/docs/vectorstores.ipynb)

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
# * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
# * [Enable the Firestore API](https://console.cloud.google.com/flows/enableapi?apiid=firestore.googleapis.com)
# * [Create a Firestore database](https://cloud.google.com/firestore/docs/manage-databases)
# 
# After confirmed access to database in the runtime environment of this notebook, filling the following values and run the cell before running example scripts.

# In[ ]:


# @markdown Please specify a source for demo purpose.
COLLECTION_NAME = "test"  # @param {type:"CollectionReference"|"string"}


# ### 🦜🔗 Library Installation
# 
# The integration lives in its own `langchain-google-firestore` package, so we need to install it. For this notebook, we will also install `langchain-google-genai` to use Google Generative AI embeddings.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -upgrade --quiet langchain-google-firestore langchain-google-vertexai')


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

PROJECT_ID = "extensions-testing"  # @param {type:"string"}

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


# # Basic Usage

# ### Initialize FirestoreVectorStore
# 
# `FirestoreVectorStore` allows you to store new vectors in a Firestore database. You can use it to store embeddings from any model, including those from Google Generative AI.

# In[ ]:


from langchain_google_firestore import FirestoreVectorStore
from langchain_google_vertexai import VertexAIEmbeddings

embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest",
    project=PROJECT_ID,
)

# Sample data
ids = ["apple", "banana", "orange"]
fruits_texts = ['{"name": "apple"}', '{"name": "banana"}', '{"name": "orange"}']

# Create a vector store
vector_store = FirestoreVectorStore(
    collection="fruits",
    embedding=embedding,
)

# Add the fruits to the vector store
vector_store.add_texts(fruits_texts, ids=ids)


# As a shorthand, you can initilize and add vectors in a single step using the `from_texts` and `from_documents` method.

# In[ ]:


vector_store = FirestoreVectorStore.from_texts(
    collection="fruits",
    texts=fruits_texts,
    embedding=embedding,
)


# In[ ]:


from langchain_core.documents import Document

fruits_docs = [Document(page_content=fruit) for fruit in fruits_texts]

vector_store = FirestoreVectorStore.from_documents(
    collection="fruits",
    documents=fruits_docs,
    embedding=embedding,
)


# ### Delete Vectors

# You can delete documents with vectors from the database using the `delete` method. You'll need to provide the document ID of the vector you want to delete. This will remove the whole document from the database, including any other fields it may have.

# In[ ]:


vector_store.delete(ids)


# ### Update Vectors

# Updating vectors is similar to adding them. You can use the `add` method to update the vector of a document by providing the document ID and the new vector.

# In[ ]:


fruit_to_update = ['{"name": "apple","price": 12}']
apple_id = "apple"

vector_store.add_texts(fruit_to_update, ids=[apple_id])


# ## Similarity Search
# 
# You can use the `FirestoreVectorStore` to perform similarity searches on the vectors you have stored. This is useful for finding similar documents or text.

# In[ ]:


vector_store.similarity_search("I like fuji apples", k=3)


# In[ ]:


vector_store.max_marginal_relevance_search("fuji", 5)


# You can add a pre-filter to the search by using the `filters` parameter. This is useful for filtering by a specific field or value.

# In[ ]:


from google.cloud.firestore_v1.base_query import FieldFilter

vector_store.max_marginal_relevance_search(
    "fuji", 5, filters=FieldFilter("content", "==", "apple")
)


# ### Customize Connection & Authentication

# In[ ]:


from google.api_core.client_options import ClientOptions
from google.cloud import firestore
from langchain_google_firestore import FirestoreVectorStore

client_options = ClientOptions()
client = firestore.Client(client_options=client_options)

# Create a vector store
vector_store = FirestoreVectorStore(
    collection="fruits",
    embedding=embedding,
    client=client,
)

