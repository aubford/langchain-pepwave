#!/usr/bin/env python
# coding: utf-8

# # PGVector
# 
# > An implementation of LangChain vectorstore abstraction using `postgres` as the backend and utilizing the `pgvector` extension.
# 
# The code lives in an integration package called: [langchain_postgres](https://github.com/langchain-ai/langchain-postgres/).
# 
# ## Status
# 
# This code has been ported over from `langchain_community` into a dedicated package called `langchain-postgres`. The following changes have been made:
# 
# * langchain_postgres works only with psycopg3. Please update your connnecion strings from `postgresql+psycopg2://...` to `postgresql+psycopg://langchain:langchain@...` (yes, it's the driver name is `psycopg` not `psycopg3`, but it'll use `psycopg3`.
# * The schema of the embedding store and collection have been changed to make add_documents work correctly with user specified ids.
# * One has to pass an explicit connection object now.
# 
# 
# Currently, there is **no mechanism** that supports easy data migration on schema changes. So any schema changes in the vectorstore will require the user to recreate the tables and re-add the documents.
# If this is a concern, please use a different vectorstore. If not, this implementation should be fine for your use case.
# 
# ## Setup
# 
# First donwload the partner package:

# In[ ]:


pip install -qU langchain_postgres


# You can run the following command to spin up a a postgres container with the `pgvector` extension:

# In[ ]:


get_ipython().run_line_magic('docker', 'run --name pgvector-container -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -d pgvector/pgvector:pg16')


# ### Credentials
# 
# There are no credentials needed to run this notebook, just make sure you downloaded the `langchain_postgres` package and correctly started the postgres container.

# If you want to get best in-class automated tracing of your model calls you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ## Instantiation
# 
# import EmbeddingTabs from "@theme/EmbeddingTabs";
# 
# <EmbeddingTabs/>
# 

# In[1]:


# | output: false
# | echo: false
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


# In[ ]:


from langchain_postgres import PGVector

# See docker command above to launch a postgres instance with pgvector enabled.
connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
collection_name = "my_docs"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)


# ## Manage vector store
# 
# ### Add items to vector store
# 
# Note that adding documents by ID will over-write any existing documents that match that ID.

# In[6]:


from langchain_core.documents import Document

docs = [
    Document(
        page_content="there are cats in the pond",
        metadata={"id": 1, "location": "pond", "topic": "animals"},
    ),
    Document(
        page_content="ducks are also found in the pond",
        metadata={"id": 2, "location": "pond", "topic": "animals"},
    ),
    Document(
        page_content="fresh apples are available at the market",
        metadata={"id": 3, "location": "market", "topic": "food"},
    ),
    Document(
        page_content="the market also sells fresh oranges",
        metadata={"id": 4, "location": "market", "topic": "food"},
    ),
    Document(
        page_content="the new art exhibit is fascinating",
        metadata={"id": 5, "location": "museum", "topic": "art"},
    ),
    Document(
        page_content="a sculpture exhibit is also at the museum",
        metadata={"id": 6, "location": "museum", "topic": "art"},
    ),
    Document(
        page_content="a new coffee shop opened on Main Street",
        metadata={"id": 7, "location": "Main Street", "topic": "food"},
    ),
    Document(
        page_content="the book club meets at the library",
        metadata={"id": 8, "location": "library", "topic": "reading"},
    ),
    Document(
        page_content="the library hosts a weekly story time for kids",
        metadata={"id": 9, "location": "library", "topic": "reading"},
    ),
    Document(
        page_content="a cooking class for beginners is offered at the community center",
        metadata={"id": 10, "location": "community center", "topic": "classes"},
    ),
]

vector_store.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])


# ### Delete items from vector store

# In[14]:


vector_store.delete(ids=["3"])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Filtering Support
# 
# The vectorstore supports a set of filters that can be applied against the metadata fields of the documents.
# 
# | Operator | Meaning/Category        |
# |----------|-------------------------|
# | \$eq      | Equality (==)           |
# | \$ne      | Inequality (!=)         |
# | \$lt      | Less than (&lt;)           |
# | \$lte     | Less than or equal (&lt;=) |
# | \$gt      | Greater than (>)        |
# | \$gte     | Greater than or equal (>=) |
# | \$in      | Special Cased (in)      |
# | \$nin     | Special Cased (not in)  |
# | \$between | Special Cased (between) |
# | \$like    | Text (like)             |
# | \$ilike   | Text (case-insensitive like) |
# | \$and     | Logical (and)           |
# | \$or      | Logical (or)            |
# 
# ### Query directly
# 
# Performing a simple similarity search can be done as follows:

# In[15]:


results = vector_store.similarity_search(
    "kitty", k=10, filter={"id": {"$in": [1, 5, 2, 9]}}
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


# If you provide a dict with multiple fields, but no operators, the top level will be interpreted as a logical **AND** filter

# In[16]:


vector_store.similarity_search(
    "ducks",
    k=10,
    filter={"id": {"$in": [1, 5, 2, 9]}, "location": {"$in": ["pond", "market"]}},
)


# In[17]:


vector_store.similarity_search(
    "ducks",
    k=10,
    filter={
        "$and": [
            {"id": {"$in": [1, 5, 2, 9]}},
            {"location": {"$in": ["pond", "market"]}},
        ]
    },
)


# If you want to execute a similarity search and receive the corresponding scores you can run:

# In[18]:


results = vector_store.similarity_search_with_score(query="cats", k=1)
for doc, score in results:
    print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")


# For a full list of the different searches you can execute on a `PGVector` vector store, please refer to the [API reference](https://python.langchain.com/api_reference/postgres/vectorstores/langchain_postgres.vectorstores.PGVector.html).
# 
# ### Query by turning into retriever
# 
# You can also transform the vector store into a retriever for easier usage in your chains. 

# In[7]:


retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1})
retriever.invoke("kitty")


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/retrieval)

# ## API reference
# 
# For detailed documentation of all __ModuleName__VectorStore features and configurations head to the API reference: https://python.langchain.com/api_reference/postgres/vectorstores/langchain_postgres.vectorstores.PGVector.html
