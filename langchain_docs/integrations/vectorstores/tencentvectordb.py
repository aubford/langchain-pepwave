#!/usr/bin/env python
# coding: utf-8

# # Tencent Cloud VectorDB
# 
# >[Tencent Cloud VectorDB](https://cloud.tencent.com/document/product/1709) is a fully managed, self-developed, enterprise-level distributed database service designed for storing, retrieving, and analyzing multi-dimensional vector data. The database supports multiple index types and similarity calculation methods. A single index can support a vector scale of up to 1 billion and can support millions of QPS and millisecond-level query latency. Tencent Cloud Vector Database can not only provide an external knowledge base for large models to improve the accuracy of large model responses but can also be widely used in AI fields such as recommendation systems, NLP services, computer vision, and intelligent customer service.
# 
# This notebook shows how to use functionality related to the Tencent vector database.
# 
# To run, you should have a [Database instance.](https://cloud.tencent.com/document/product/1709/95101).
# 
# ## Basic Usage
# 

# In[ ]:


get_ipython().system('pip3 install tcvectordb langchain-community')


# In[4]:


from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.fake import FakeEmbeddings
from langchain_community.vectorstores import TencentVectorDB
from langchain_community.vectorstores.tencentvectordb import ConnectionParams
from langchain_text_splitters import CharacterTextSplitter


# load the documents, split them into chunks.

# In[5]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)


# we support two ways to embed the documents:
# - Use any Embeddings models compatible with Langchain Embeddings.
# - Specify the Embedding model name of the Tencent VectorStore DB, choices are:
#     - `bge-base-zh`, dimension: 768
#     - `m3e-base`, dimension: 768
#     - `text2vec-large-chinese`, dimension: 1024
#     - `e5-large-v2`, dimension: 1024
#     - `multilingual-e5-base`, dimension: 768 
# 
# flowing code shows both ways to embed the documents, you can choose one of them by commenting the other:

# In[6]:


##  you can use a Langchain Embeddings model, like OpenAIEmbeddings:

# from langchain_community.embeddings.openai import OpenAIEmbeddings
#
# embeddings = OpenAIEmbeddings()
# t_vdb_embedding = None

## Or you can use a Tencent Embedding model, like `bge-base-zh`:

t_vdb_embedding = "bge-base-zh"  # bge-base-zh is the default model
embeddings = None


# now we can create a TencentVectorDB instance, you must provide at least one of the `embeddings` or `t_vdb_embedding` parameters. if both are provided, the `embeddings` parameter will be used:

# In[7]:


conn_params = ConnectionParams(
    url="http://10.0.X.X",
    key="eC4bLRy2va******************************",
    username="root",
    timeout=20,
)

vector_db = TencentVectorDB.from_documents(
    docs, embeddings, connection_params=conn_params, t_vdb_embedding=t_vdb_embedding
)


# In[8]:


query = "What did the president say about Ketanji Brown Jackson"
docs = vector_db.similarity_search(query)
docs[0].page_content


# In[9]:


vector_db = TencentVectorDB(embeddings, conn_params)

vector_db.add_texts(["Ankush went to Princeton"])
query = "Where did Ankush go to college?"
docs = vector_db.max_marginal_relevance_search(query)
docs[0].page_content


# ## Metadata and filtering
# 
# Tencent VectorDB supports metadata and [filtering](https://cloud.tencent.com/document/product/1709/95099#c6f6d3a3-02c5-4891-b0a1-30fe4daf18d8). You can add metadata to the documents and filter the search results based on the metadata.
# 
# now we will create a new TencentVectorDB collection with metadata and demonstrate how to filter the search results based on the metadata:

# In[2]:


from langchain_community.vectorstores.tencentvectordb import (
    META_FIELD_TYPE_STRING,
    META_FIELD_TYPE_UINT64,
    ConnectionParams,
    MetaField,
    TencentVectorDB,
)
from langchain_core.documents import Document

meta_fields = [
    MetaField(name="year", data_type=META_FIELD_TYPE_UINT64, index=True),
    MetaField(name="rating", data_type=META_FIELD_TYPE_STRING, index=False),
    MetaField(name="genre", data_type=META_FIELD_TYPE_STRING, index=True),
    MetaField(name="director", data_type=META_FIELD_TYPE_STRING, index=True),
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
            "genre": "superhero",
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
    collection_name="movies",
    meta_fields=meta_fields,
)

query = "film about dream by Christopher Nolan"

# you can use the tencentvectordb filtering syntax with the `expr` parameter:
result = vector_db.similarity_search(query, expr='director="Christopher Nolan"')

# you can either use the langchain filtering syntax with the `filter` parameter:
# result = vector_db.similarity_search(query, filter='eq("director", "Christopher Nolan")')

result

