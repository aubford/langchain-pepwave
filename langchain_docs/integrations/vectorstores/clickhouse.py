#!/usr/bin/env python
# coding: utf-8

# # ClickHouse
# 
# > [ClickHouse](https://clickhouse.com/) is the fastest and most resource efficient open-source database for real-time apps and analytics with full SQL support and a wide range of functions to assist users in writing analytical queries. Lately added data structures and distance search functions (like `L2Distance`) as well as [approximate nearest neighbor search indexes](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/annindexes) enable ClickHouse to be used as a high performance and scalable vector database to store and search vectors with SQL.
# 
# This notebook shows how to use functionality related to the `ClickHouse` vector store.
# 
# ## Setup
# 
# First set up a local clickhouse server with docker:

# In[ ]:


get_ipython().system(' docker run -d -p 8123:8123 -p9000:9000 --name langchain-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server:23.4.2.11')


# You'll need to install `langchain-community` and `clickhouse-connect` to use this integration

# In[ ]:


pip install -qU langchain-community clickhouse-connect


# ### Credentials
# 
# There are no credentials for this notebook, just make sure you have installed the packages as shown above.

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

# In[ ]:


# | output: false
# | echo: false
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")


# In[ ]:


from langchain_community.vectorstores import Clickhouse, ClickhouseSettings

settings = ClickhouseSettings(table="clickhouse_example")
vector_store = Clickhouse(embeddings, config=settings)


# ## Manage vector store
# 
# Once you have created your vector store, we can interact with it by adding and deleting different items.
# 
# ### Add items to vector store
# 
# We can add items to our vector store by using the `add_documents` function.

# In[ ]:


from uuid import uuid4

from langchain_core.documents import Document

document_1 = Document(
    page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

document_3 = Document(
    page_content="Building an exciting new project with LangChain - come check it out!",
    metadata={"source": "tweet"},
)

document_4 = Document(
    page_content="Robbers broke into the city bank and stole $1 million in cash.",
    metadata={"source": "news"},
)

document_5 = Document(
    page_content="Wow! That was an amazing movie. I can't wait to see it again.",
    metadata={"source": "tweet"},
)

document_6 = Document(
    page_content="Is the new iPhone worth the price? Read this review to find out.",
    metadata={"source": "website"},
)

document_7 = Document(
    page_content="The top 10 soccer players in the world right now.",
    metadata={"source": "website"},
)

document_8 = Document(
    page_content="LangGraph is the best framework for building stateful, agentic applications!",
    metadata={"source": "tweet"},
)

document_9 = Document(
    page_content="The stock market is down 500 points today due to fears of a recession.",
    metadata={"source": "news"},
)

document_10 = Document(
    page_content="I have a bad feeling I am going to get deleted :(",
    metadata={"source": "tweet"},
)

documents = [
    document_1,
    document_2,
    document_3,
    document_4,
    document_5,
    document_6,
    document_7,
    document_8,
    document_9,
    document_10,
]
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store.add_documents(documents=documents, ids=uuids)


# ### Delete items from vector store
# 
# We can delete items from our vector store by ID by using the `delete` function.

# In[ ]:


vector_store.delete(ids=uuids[-1])


# ## Query vector store
# 
# Once your vector store has been created and the relevant documents have been added you will most likely wish to query it during the running of your chain or agent. 
# 
# ### Query directly
# 
# #### Similarity search
# 
# Performing a simple similarity search can be done as follows:

# In[ ]:


results = vector_store.similarity_search(
    "LangChain provides abstractions to make working with LLMs easy", k=2
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")


# #### Similarity search with score
# 
# You can also search with score:

# In[ ]:


results = vector_store.similarity_search_with_score("Will it be hot tomorrow?", k=1)
for res, score in results:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")


# ## Filtering
# 
# You can have direct access to ClickHouse SQL where statement. You can write `WHERE` clause following standard SQL.
# 
# **NOTE**: Please be aware of SQL injection, this interface must not be directly called by end-user.
# 
# If you custimized your `column_map` under your setting, you search with filter like this:

# In[ ]:


meta = vector_store.metadata_column
results = vector_store.similarity_search_with_relevance_scores(
    "What did I eat for breakfast?",
    k=4,
    where_str=f"{meta}.source = 'tweet'",
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")


# #### Other search methods
# 
# There are a variety of other search methods that are not covered in this notebook, such as MMR search or searching by vector. For a full list of the search abilities available for `Clickhouse` vector store check out the [API reference](https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.clickhouse.Clickhouse.html).

# ### Query by turning into retriever
# 
# You can also transform the vector store into a retriever for easier usage in your chains. 
# 
# Here is how to transform your vector store into a retriever and then invoke the retreiever with a simple query and filter.

# In[ ]:


retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 1, "score_threshold": 0.5},
)
retriever.invoke("Stealing from the bank is a crime", filter={"source": "news"})


# ## Usage for retrieval-augmented generation
# 
# For guides on how to use this vector store for retrieval-augmented generation (RAG), see the following sections:
# 
# - [Tutorials](/docs/tutorials/)
# - [How-to: Question and answer with RAG](https://python.langchain.com/docs/how_to/#qa-with-rag)
# - [Retrieval conceptual docs](https://python.langchain.com/docs/concepts/retrieval)

# For more, check out a complete RAG template using Astra DB [here](https://github.com/langchain-ai/langchain/tree/master/templates/rag-astradb).

# ## API reference
# 
# For detailed documentation of all `Clickhouse` features and configurations head to the API reference:https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.clickhouse.Clickhouse.html
