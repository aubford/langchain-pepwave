#!/usr/bin/env python
# coding: utf-8

# # Google Spanner
# > [Spanner](https://cloud.google.com/spanner) is a highly scalable database that combines unlimited scalability with relational semantics, such as secondary indexes, strong consistency, schemas, and SQL providing 99.999% availability in one easy solution.
# 
# This notebook goes over how to use `Spanner` for Vector Search with `SpannerVectorStore` class.
# 
# Learn more about the package on [GitHub](https://github.com/googleapis/langchain-google-spanner-python/).
# 
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googleapis/langchain-google-spanner-python/blob/main/docs/vector_store.ipynb)

# ## Before You Begin
# 
# To run this notebook, you will need to do the following:
# 
#  * [Create a Google Cloud Project](https://developers.google.com/workspace/guides/create-project)
#  * [Enable the Cloud Spanner API](https://console.cloud.google.com/flows/enableapi?apiid=spanner.googleapis.com)
#  * [Create a Spanner instance](https://cloud.google.com/spanner/docs/create-manage-instances)
#  * [Create a Spanner database](https://cloud.google.com/spanner/docs/create-manage-databases)

# ### 🦜🔗 Library Installation
# The integration lives in its own `langchain-google-spanner` package, so we need to install it.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-google-spanner langchain-google-vertexai')


# **Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.

# In[2]:


# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)


# ### 🔐 Authentication
# Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
# 
# * If you are using Colab to run this notebook, use the cell below and continue.
# * If you are using Vertex AI Workbench, check out the setup instructions [here](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/setup-env).

# In[ ]:


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
get_ipython().run_line_magic('env', 'GOOGLE_CLOUD_PROJECT={PROJECT_ID}')


# ### 💡 API Enablement
# The `langchain-google-spanner` package requires that you [enable the Spanner API](https://console.cloud.google.com/flows/enableapi?apiid=spanner.googleapis.com) in your Google Cloud Project.

# In[ ]:


# enable Spanner API
get_ipython().system('gcloud services enable spanner.googleapis.com')


# ## Basic Usage

# ### Set Spanner database values
# Find your database values, in the [Spanner Instances page](https://console.cloud.google.com/spanner?_ga=2.223735448.2062268965.1707700487-2088871159.1707257687).

# In[4]:


# @title Set Your Values Here { display-mode: "form" }
INSTANCE = "my-instance"  # @param {type: "string"}
DATABASE = "my-database"  # @param {type: "string"}
TABLE_NAME = "vectors_search_data"  # @param {type: "string"}


# ### Initialize a table
# The `SpannerVectorStore` class instance requires a database table with id, content and embeddings columns. 
# 
# The helper method `init_vector_store_table()` that can be used to create a table with the proper schema for you.

# In[ ]:


from langchain_google_spanner import SecondaryIndex, SpannerVectorStore, TableColumn

SpannerVectorStore.init_vector_store_table(
    instance_id=INSTANCE,
    database_id=DATABASE,
    table_name=TABLE_NAME,
    # Customize the table creation
    # id_column="row_id",
    # content_column="content_column",
    # metadata_columns=[
    #     TableColumn(name="metadata", type="JSON", is_null=True),
    #     TableColumn(name="title", type="STRING(MAX)", is_null=False),
    # ],
    # secondary_indexes=[
    #     SecondaryIndex(index_name="row_id_and_title", columns=["row_id", "title"])
    # ],
)


# ### Create an embedding class instance
# 
# You can use any [LangChain embeddings model](/docs/integrations/text_embedding/).
# You may need to enable Vertex AI API to use `VertexAIEmbeddings`. We recommend setting the embedding model's version for production, learn more about the [Text embeddings models](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-embeddings).

# In[ ]:


# enable Vertex AI API
get_ipython().system('gcloud services enable aiplatform.googleapis.com')


# In[5]:


from langchain_google_vertexai import VertexAIEmbeddings

embeddings = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest", project=PROJECT_ID
)


# ### SpannerVectorStore
# 
# To initialize the `SpannerVectorStore` class you need to provide 4 required arguments and other arguments are optional and only need to pass if it's different from default ones
# 
# 1. `instance_id` - The name of the Spanner instance
# 1. `database_id` - The name of the Spanner database
# 1. `table_name` - The name of the table within the database to store the documents & their embeddings.
# 1. `embedding_service` - The Embeddings implementation which is used to generate the embeddings.

# In[ ]:


db = SpannerVectorStore(
    instance_id=INSTANCE,
    database_id=DATABASE,
    table_name=TABLE_NAME,
    embedding_service=embeddings,
    # Connect to a custom vector store table
    # id_column="row_id",
    # content_column="content",
    # metadata_columns=["metadata", "title"],
)


# #### Add Documents
# To add documents in the vector store.

# In[ ]:


import uuid

from langchain_community.document_loaders import HNLoader

loader = HNLoader("https://news.ycombinator.com/item?id=34817881")

documents = loader.load()
ids = [str(uuid.uuid4()) for _ in range(len(documents))]
db.add_documents(documents, ids)


# #### Search Documents
# To search documents in the vector store with similarity search.

# In[ ]:


db.similarity_search(query="Explain me vector store?", k=3)


# #### Search Documents
# To search documents in the vector store with max marginal relevance search.

# In[ ]:


db.max_marginal_relevance_search("Testing the langchain integration with spanner", k=3)


# #### Delete Documents
# To remove documents from the vector store, use the IDs that correspond to the values in the `row_id`` column when initializing the VectorStore.

# In[ ]:


db.delete(ids=["id1", "id2"])


# #### Delete Documents
# To remove documents from the vector store, you can utilize the documents themselves. The content column and metadata columns provided during VectorStore initialization will be used to find out the rows corresponding to the documents. Any matching rows will then be deleted.

# In[ ]:


db.delete(documents=[documents[0], documents[1]])

