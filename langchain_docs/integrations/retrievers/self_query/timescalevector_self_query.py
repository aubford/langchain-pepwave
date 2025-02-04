#!/usr/bin/env python
# coding: utf-8

# # Timescale Vector (Postgres) 
# 
# >[Timescale Vector](https://www.timescale.com/ai) is `PostgreSQL++` for AI applications. It enables you to efficiently store and query billions of vector embeddings in `PostgreSQL`.
# >
# >[PostgreSQL](https://en.wikipedia.org/wiki/PostgreSQL) also known as `Postgres`,
# > is a free and open-source relational database management system (RDBMS) 
# > emphasizing extensibility and `SQL` compliance.
# 
# This notebook shows how to use the Postgres vector database (`TimescaleVector`) to perform self-querying. In the notebook we'll demo the `SelfQueryRetriever` wrapped around a TimescaleVector vector store. 
# 
# ## What is Timescale Vector?
# **[Timescale Vector](https://www.timescale.com/ai) is PostgreSQL++ for AI applications.**
# 
# Timescale Vector enables you to efficiently store and query millions of vector embeddings in `PostgreSQL`.
# - Enhances `pgvector` with faster and more accurate similarity search on 1B+ vectors via DiskANN inspired indexing algorithm.
# - Enables fast time-based vector search via automatic time-based partitioning and indexing.
# - Provides a familiar SQL interface for querying vector embeddings and relational data.
# 
# Timescale Vector is cloud PostgreSQL for AI that scales with you from POC to production:
# - Simplifies operations by enabling you to store relational metadata, vector embeddings, and time-series data in a single database.
# - Benefits from rock-solid PostgreSQL foundation with enterprise-grade feature liked streaming backups and replication, high-availability and row-level security.
# - Enables a worry-free experience with enterprise-grade security and compliance.
# 
# ## How to access Timescale Vector
# Timescale Vector is available on [Timescale](https://www.timescale.com/ai), the cloud PostgreSQL platform. (There is no self-hosted version at this time.)
# 
# LangChain users get a 90-day free trial for Timescale Vector.
# - To get started, [signup](https://console.cloud.timescale.com/signup?utm_campaign=vectorlaunch&utm_source=langchain&utm_medium=referral) to Timescale, create a new database and follow this notebook!
# - See the [Timescale Vector explainer blog](https://www.timescale.com/blog/how-we-made-postgresql-the-best-vector-database/?utm_campaign=vectorlaunch&utm_source=langchain&utm_medium=referral) for more details and performance benchmarks.
# - See the [installation instructions](https://github.com/timescale/python-vector) for more details on using Timescale Vector in python.
# 

# ## Creating a TimescaleVector vectorstore
# First we'll want to create a Timescale Vector vectorstore and seed it with some data. We've created a small demo set of documents that contain summaries of movies.
# 
# NOTE: The self-query retriever requires you to have `lark` installed (`pip install lark`). We also need the `timescale-vector` package.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  lark')


# In[2]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  timescale-vector')


# In this example, we'll use `OpenAIEmbeddings`, so let's load your OpenAI API key.

# In[1]:


# Get openAI api key by reading local .env file
# The .env file should contain a line starting with `OPENAI_API_KEY=sk-`
import os

from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# Alternatively, use getpass to enter the key in a prompt
# import os
# import getpass
# os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# To connect to your PostgreSQL database, you'll need your service URI, which can be found in the cheatsheet or `.env` file you downloaded after creating a new database. 
# 
# If you haven't already, [signup for Timescale](https://console.cloud.timescale.com/signup?utm_campaign=vectorlaunch&utm_source=langchain&utm_medium=referral), and create a new database.
# 
# The URI will look something like this: `postgres://tsdbadmin:<password>@<id>.tsdb.cloud.timescale.com:<port>/tsdb?sslmode=require`

# In[2]:


# Get the service url by reading local .env file
# The .env file should contain a line starting with `TIMESCALE_SERVICE_URL=postgresql://`
_ = load_dotenv(find_dotenv())
TIMESCALE_SERVICE_URL = os.environ["TIMESCALE_SERVICE_URL"]

# Alternatively, use getpass to enter the key in a prompt
# import os
# import getpass
# TIMESCALE_SERVICE_URL = getpass.getpass("Timescale Service URL:")


# In[3]:


from langchain_community.vectorstores.timescalevector import TimescaleVector
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()


# Here's the sample documents we'll use for this demo. The data is about movies, and has both content and metadata fields with information about particular movie.

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
            "director": "Andrei Tarkovsky",
            "genre": "science fiction",
            "rating": 9.9,
        },
    ),
]


# Finally, we'll create our Timescale Vector vectorstore. Note that the collection name will be the name of the PostgreSQL table in which the documents are stored in.

# In[5]:


COLLECTION_NAME = "langchain_self_query_demo"
vectorstore = TimescaleVector.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    service_url=TIMESCALE_SERVICE_URL,
)


# ## Creating our self-querying retriever
# Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

# In[14]:


from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

# Give LLM info about the metadata fields
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

# Instantiate the self-query retriever from an LLM
llm = OpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info, verbose=True
)


# ## Self Querying Retrieval with Timescale Vector
# And now we can try actually using our retriever!
# 
# Run the queries below and note how you can specify a query, filter, composite filter (filters with AND, OR) in natural language and the self-query retriever will translate that query into SQL and perform the search on the Timescale Vector (Postgres) vectorstore.
# 
# This illustrates the power of the self-query retriever. You can use it to perform complex searches over your vectorstore without you or your users having to write any SQL directly!

# In[15]:


# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")


# In[16]:


# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")


# In[17]:


# This example specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women")


# In[18]:


# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5) science fiction film?")


# In[11]:


# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before 2005 that's all about toys, and preferably is animated"
)


# ### Filter k
# 
# We can also use the self query retriever to specify `k`: the number of documents to fetch.
# 
# We can do this by passing `enable_limit=True` to the constructor.

# In[19]:


retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    enable_limit=True,
    verbose=True,
)


# In[22]:


# This example specifies a query with a LIMIT value
retriever.invoke("what are two movies about dinosaurs")

