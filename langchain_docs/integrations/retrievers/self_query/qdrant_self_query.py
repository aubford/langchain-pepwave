#!/usr/bin/env python
# coding: utf-8

# # Qdrant
# 
# >[Qdrant](https://qdrant.tech/documentation/) (read: quadrant) is a vector similarity search engine. It provides a production-ready service with a convenient API to store, search, and manage points - vectors with an additional payload. `Qdrant` is tailored to extended filtering support.
# 
# In the notebook, we'll demo the `SelfQueryRetriever` wrapped around a `Qdrant` vector store. 

# ## Creating a Qdrant vector store
# First we'll want to create a Qdrant vector store and seed it with some data. We've created a small demo set of documents that contain summaries of movies.
# 
# **Note:** The self-query retriever requires you to have `lark` installed (`pip install lark`). We also need the `qdrant-client` package.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  lark qdrant-client')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[2]:


# import os
# import getpass

# os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API Key:')


# In[3]:


from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()


# In[4]:


docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"year": 1993, "rating": 7.7, "genre": "science fiction"},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
    Document(
        page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
        metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
    ),
    Document(
        page_content="Toys come alive and have a blast doing so",
        metadata={"year": 1995, "genre": "animated"},
    ),
    Document(
        page_content="Three men walk into the Zone, three men walk out of the Zone",
        metadata={
            "year": 1979,
            "rating": 9.9,
            "director": "Andrei Tarkovsky",
            "genre": "science fiction",
        },
    ),
]
vectorstore = Qdrant.from_documents(
    docs,
    embeddings,
    location=":memory:",  # Local mode with in-memory storage only
    collection_name="my_documents",
)


# ## Creating our self-querying retriever
# Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

# In[5]:


from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string or list[string]",
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
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"
llm = OpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info, verbose=True
)


# ## Testing it out
# And now we can try actually using our retriever!

# In[6]:


# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")


# In[7]:


# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")


# In[9]:


# This example specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women")


# In[10]:


# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5) science fiction film?")


# In[11]:


# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before 2005 that's all about toys, and preferably is animated"
)


# ## Filter k
# 
# We can also use the self query retriever to specify `k`: the number of documents to fetch.
# 
# We can do this by passing `enable_limit=True` to the constructor.

# In[12]:


retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    enable_limit=True,
    verbose=True,
)


# In[13]:


# This example only specifies a relevant query
retriever.invoke("what are two movies about dinosaurs")

