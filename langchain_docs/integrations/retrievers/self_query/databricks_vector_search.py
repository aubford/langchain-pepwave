#!/usr/bin/env python
# coding: utf-8

# # Databricks Vector Search
# 
# >[Databricks Vector Search](https://docs.databricks.com/en/generative-ai/vector-search.html) is a serverless similarity search engine that allows you to store a vector representation of your data, including metadata, in a vector database. With Vector Search, you can create auto-updating vector search indexes from Delta tables managed by Unity Catalog and query them with a simple API to return the most similar vectors.
# 
# 
# In the walkthrough, we'll demo the `SelfQueryRetriever` with a Databricks Vector Search.

# ## create Databricks vector store index
# First we'll want to create a databricks vector store index and seed it with some data. We've created a small demo set of documents that contain summaries of movies.
# 
# **Note:** The self-query retriever requires you to have `lark` installed (`pip install lark`) along with integration-specific requirements.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-core databricks-vectorsearch langchain-openai tiktoken')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[2]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
databricks_host = getpass.getpass("Databricks host:")
databricks_token = getpass.getpass("Databricks token:")


# In[13]:


from databricks.vector_search.client import VectorSearchClient
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
emb_dim = len(embeddings.embed_query("hello"))

vector_search_endpoint_name = "vector_search_demo_endpoint"


vsc = VectorSearchClient(
    workspace_url=databricks_host, personal_access_token=databricks_token
)
vsc.create_endpoint(name=vector_search_endpoint_name, endpoint_type="STANDARD")


# In[14]:


index_name = "udhay_demo.10x.demo_index"

index = vsc.create_direct_access_index(
    endpoint_name=vector_search_endpoint_name,
    index_name=index_name,
    primary_key="id",
    embedding_dimension=emb_dim,
    embedding_vector_column="text_vector",
    schema={
        "id": "string",
        "page_content": "string",
        "year": "int",
        "rating": "float",
        "genre": "string",
        "text_vector": "array<float>",
    },
)

index.describe()


# In[15]:


index = vsc.get_index(endpoint_name=vector_search_endpoint_name, index_name=index_name)

index.describe()


# In[7]:


from langchain_core.documents import Document

docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"id": 1, "year": 1993, "rating": 7.7, "genre": "action"},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"id": 2, "year": 2010, "genre": "thriller", "rating": 8.2},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
        metadata={"id": 3, "year": 2019, "rating": 8.3, "genre": "drama"},
    ),
    Document(
        page_content="Three men walk into the Zone, three men walk out of the Zone",
        metadata={"id": 4, "year": 1979, "rating": 9.9, "genre": "science fiction"},
    ),
    Document(
        page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
        metadata={"id": 5, "year": 2006, "genre": "thriller", "rating": 9.0},
    ),
    Document(
        page_content="Toys come alive and have a blast doing so",
        metadata={"id": 6, "year": 1995, "genre": "animated", "rating": 9.3},
    ),
]


# In[16]:


from langchain_community.vectorstores import DatabricksVectorSearch

vector_store = DatabricksVectorSearch(
    index,
    text_column="page_content",
    embedding=embeddings,
    columns=["year", "rating", "genre"],
)


# In[10]:


vector_store.add_documents(docs)


# ## Creating our self-querying retriever
# Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

# In[17]:


from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"
llm = OpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vector_store, document_content_description, metadata_field_info, verbose=True
)


# ## Test it out
# And now we can try actually using our retriever!
# 

# In[18]:


# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")


# In[19]:


# This example specifies a filter
retriever.invoke("What are some highly rated movies (above 9)?")


# In[20]:


# This example specifies both a relevant query and a filter
retriever.invoke("What are the thriller movies that are highly rated?")


# In[21]:


# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before 2005 that's all about dinosaurs, \
    and preferably has a lot of action"
)


# ## Filter k
# 
# We can also use the self query retriever to specify `k`: the number of documents to fetch.
# 
# We can do this by passing `enable_limit=True` to the constructor.

# ## Filter k
# 
# We can also use the self query retriever to specify `k`: the number of documents to fetch.
# 
# We can do this by passing `enable_limit=True` to the constructor.

# In[22]:


retriever = SelfQueryRetriever.from_llm(
    llm,
    vector_store,
    document_content_description,
    metadata_field_info,
    verbose=True,
    enable_limit=True,
)


# In[ ]:


retriever.invoke("What are two movies about dinosaurs?")

