#!/usr/bin/env python
# coding: utf-8

# # Tencent Cloud VectorDB
# 
# > [Tencent Cloud VectorDB](https://cloud.tencent.com/document/product/1709) is a fully managed, self-developed, enterprise-level distributed database    service designed for storing, retrieving, and analyzing multi-dimensional vector data.
# 
# In the walkthrough, we'll demo the `SelfQueryRetriever` with a Tencent Cloud VectorDB.

# ## create a TencentVectorDB instance
# First we'll want to create a TencentVectorDB and seed it with some data. We've created a small demo set of documents that contain summaries of movies.
# 
# **Note:** The self-query retriever requires you to have `lark` installed (`pip install lark`) along with integration-specific requirements.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet tcvectordb langchain-openai tiktoken lark')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[2]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# create a TencentVectorDB instance and seed it with some data:

# In[3]:


from langchain_community.vectorstores.tencentvectordb import (
    ConnectionParams,
    MetaField,
    TencentVectorDB,
)
from langchain_core.documents import Document
from tcvectordb.model.enum import FieldType

meta_fields = [
    MetaField(name="year", data_type="uint64", index=True),
    MetaField(name="rating", data_type="string", index=False),
    MetaField(name="genre", data_type=FieldType.String, index=True),
    MetaField(name="director", data_type=FieldType.String, index=True),
]

docs = [
    Document(
        page_content="The Shawshank Redemption is a 1994 American drama film written and directed by Frank Darabont.",
        metadata={
            "year": 1994,
            "rating": "9.3",
            "genre": "drama",
            "director": "Frank Darabont",
        },
    ),
    Document(
        page_content="The Godfather is a 1972 American crime film directed by Francis Ford Coppola.",
        metadata={
            "year": 1972,
            "rating": "9.2",
            "genre": "crime",
            "director": "Francis Ford Coppola",
        },
    ),
    Document(
        page_content="The Dark Knight is a 2008 superhero film directed by Christopher Nolan.",
        metadata={
            "year": 2008,
            "rating": "9.0",
            "genre": "science fiction",
            "director": "Christopher Nolan",
        },
    ),
    Document(
        page_content="Inception is a 2010 science fiction action film written and directed by Christopher Nolan.",
        metadata={
            "year": 2010,
            "rating": "8.8",
            "genre": "science fiction",
            "director": "Christopher Nolan",
        },
    ),
    Document(
        page_content="The Avengers is a 2012 American superhero film based on the Marvel Comics superhero team of the same name.",
        metadata={
            "year": 2012,
            "rating": "8.0",
            "genre": "science fiction",
            "director": "Joss Whedon",
        },
    ),
    Document(
        page_content="Black Panther is a 2018 American superhero film based on the Marvel Comics character of the same name.",
        metadata={
            "year": 2018,
            "rating": "7.3",
            "genre": "science fiction",
            "director": "Ryan Coogler",
        },
    ),
]

vector_db = TencentVectorDB.from_documents(
    docs,
    None,
    connection_params=ConnectionParams(
        url="http://10.0.X.X",
        key="eC4bLRy2va******************************",
        username="root",
        timeout=20,
    ),
    collection_name="self_query_movies",
    meta_fields=meta_fields,
    drop_old=True,
)


# ## Creating our self-querying retriever
# Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

# In[4]:


from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI

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
        name="director",
        description="The name of the movie director",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="string"
    ),
]
document_content_description = "Brief summary of a movie"


# In[5]:


llm = ChatOpenAI(temperature=0, model="gpt-4", max_tokens=4069)
retriever = SelfQueryRetriever.from_llm(
    llm, vector_db, document_content_description, metadata_field_info, verbose=True
)


# ## Test it out
# And now we can try actually using our retriever!
# 

# In[6]:


# This example only specifies a relevant query
retriever.invoke("movies about a superhero")


# In[7]:


# This example only specifies a filter
retriever.invoke("movies that were released after 2010")


# In[8]:


# This example specifies both a relevant query and a filter
retriever.invoke("movies about a superhero which were released after 2010")


# ## Filter k
# 
# We can also use the self query retriever to specify `k`: the number of documents to fetch.
# 
# We can do this by passing `enable_limit=True` to the constructor.

# In[9]:


retriever = SelfQueryRetriever.from_llm(
    llm,
    vector_db,
    document_content_description,
    metadata_field_info,
    verbose=True,
    enable_limit=True,
)


# In[10]:


retriever.invoke("what are two movies about a superhero")

