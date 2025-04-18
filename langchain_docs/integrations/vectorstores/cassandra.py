#!/usr/bin/env python
# coding: utf-8

# # Apache Cassandra
# 
# This page provides a quickstart for using [Apache Cassandra®](https://cassandra.apache.org/) as a Vector Store.

# > [Cassandra](https://cassandra.apache.org/) is a NoSQL, row-oriented, highly scalable and highly available database.Starting with version 5.0, the database ships with [vector search capabilities](https://cassandra.apache.org/doc/trunk/cassandra/vector-search/overview.html).

# _Note: in addition to access to the database, an OpenAI API Key is required to run the full example._

# ### Setup and general dependencies

# Use of the integration requires the following Python package.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-community "cassio>=0.1.4"')


# _Note: depending on your LangChain setup, you may need to install/upgrade other dependencies needed for this demo_
# _(specifically, recent versions of `datasets`, `openai`, `pypdf` and `tiktoken` are required, along with `langchain-community`)._

# In[ ]:


import os
from getpass import getpass

from datasets import (
    load_dataset,
)
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# In[ ]:


if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("OPENAI_API_KEY = ")


# In[ ]:


embe = OpenAIEmbeddings()


# ## Import the Vector Store

# In[ ]:


from langchain_community.vectorstores import Cassandra


# ## Connection parameters
# 
# The Vector Store integration shown in this page can be used with Cassandra as well as other derived databases, such as Astra DB, which use the CQL (Cassandra Query Language) protocol.
# 
# > DataStax [Astra DB](https://docs.datastax.com/en/astra-serverless/docs/vector-search/quickstart.html) is a managed serverless database built on Cassandra, offering the same interface and strengths.
# 
# Depending on whether you connect to a Cassandra cluster or to Astra DB through CQL, you will provide different parameters when creating the vector store object.

# ### Connecting to a Cassandra cluster
# 
# You first need to create a `cassandra.cluster.Session` object, as described in the [Cassandra driver documentation](https://docs.datastax.com/en/developer/python-driver/latest/api/cassandra/cluster/#module-cassandra.cluster). The details vary (e.g. with network settings and authentication), but this might be something like:

# In[ ]:


from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect()


# You can now set the session, along with your desired keyspace name, as a global CassIO parameter:

# In[ ]:


import cassio

CASSANDRA_KEYSPACE = input("CASSANDRA_KEYSPACE = ")

cassio.init(session=session, keyspace=CASSANDRA_KEYSPACE)


# Now you can create the vector store:

# In[ ]:


vstore = Cassandra(
    embedding=embe,
    table_name="cassandra_vector_demo",
    # session=None, keyspace=None  # Uncomment on older versions of LangChain
)


# _Note: you can also pass your session and keyspace directly as parameters when creating the vector store. Using the global `cassio.init` setting, however, comes handy if your applications uses Cassandra in several ways (for instance, for vector store, chat memory and LLM response caching), as it allows to centralize credential and DB connection management in one place._

# ### Connecting to Astra DB through CQL

# In this case you initialize CassIO with the following connection parameters:
# 
# - the Database ID, e.g. `01234567-89ab-cdef-0123-456789abcdef`
# - the Token, e.g. `AstraCS:6gBhNmsk135....` (it must be a "Database Administrator" token)
# - Optionally a Keyspace name (if omitted, the default one for the database will be used)

# In[ ]:


ASTRA_DB_ID = input("ASTRA_DB_ID = ")
ASTRA_DB_APPLICATION_TOKEN = getpass("ASTRA_DB_APPLICATION_TOKEN = ")

desired_keyspace = input("ASTRA_DB_KEYSPACE (optional, can be left empty) = ")
if desired_keyspace:
    ASTRA_DB_KEYSPACE = desired_keyspace
else:
    ASTRA_DB_KEYSPACE = None


# In[ ]:


import cassio

cassio.init(
    database_id=ASTRA_DB_ID,
    token=ASTRA_DB_APPLICATION_TOKEN,
    keyspace=ASTRA_DB_KEYSPACE,
)


# Now you can create the vector store:

# In[ ]:


vstore = Cassandra(
    embedding=embe,
    table_name="cassandra_vector_demo",
    # session=None, keyspace=None  # Uncomment on older versions of LangChain
)


# ## Load a dataset

# Convert each entry in the source dataset into a `Document`, then write them into the vector store:

# In[ ]:


philo_dataset = load_dataset("datastax/philosopher-quotes")["train"]

docs = []
for entry in philo_dataset:
    metadata = {"author": entry["author"]}
    doc = Document(page_content=entry["quote"], metadata=metadata)
    docs.append(doc)

inserted_ids = vstore.add_documents(docs)
print(f"\nInserted {len(inserted_ids)} documents.")


# In the above, `metadata` dictionaries are created from the source data and are part of the `Document`.

# Add some more entries, this time with `add_texts`:

# In[ ]:


texts = ["I think, therefore I am.", "To the things themselves!"]
metadatas = [{"author": "descartes"}, {"author": "husserl"}]
ids = ["desc_01", "huss_xy"]

inserted_ids_2 = vstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
print(f"\nInserted {len(inserted_ids_2)} documents.")


# _Note: you may want to speed up the execution of `add_texts` and `add_documents` by increasing the concurrency level for_
# _these bulk operations - check out the methods' `batch_size` parameter_
# _for more details. Depending on the network and the client machine specifications, your best-performing choice of parameters may vary._

# ## Run searches

# This section demonstrates metadata filtering and getting the similarity scores back:

# In[ ]:


results = vstore.similarity_search("Our life is what we make of it", k=3)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")


# In[ ]:


results_filtered = vstore.similarity_search(
    "Our life is what we make of it",
    k=3,
    filter={"author": "plato"},
)
for res in results_filtered:
    print(f"* {res.page_content} [{res.metadata}]")


# In[ ]:


results = vstore.similarity_search_with_score("Our life is what we make of it", k=3)
for res, score in results:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")


# ### MMR (Maximal-marginal-relevance) search

# In[ ]:


results = vstore.max_marginal_relevance_search(
    "Our life is what we make of it",
    k=3,
    filter={"author": "aristotle"},
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")


# ## Deleting stored documents

# In[ ]:


delete_1 = vstore.delete(inserted_ids[:3])
print(f"all_succeed={delete_1}")  # True, all documents deleted


# In[ ]:


delete_2 = vstore.delete(inserted_ids[2:5])
print(f"some_succeeds={delete_2}")  # True, though some IDs were gone already


# ## A minimal RAG chain

# The next cells will implement a simple RAG pipeline:
# - download a sample PDF file and load it onto the store;
# - create a RAG chain with LCEL (LangChain Expression Language), with the vector store at its heart;
# - run the question-answering chain.

# In[ ]:


get_ipython().system('curl -L      "https://github.com/awesome-astra/datasets/blob/main/demo-resources/what-is-philosophy/what-is-philosophy.pdf?raw=true"      -o "what-is-philosophy.pdf"')


# In[ ]:


pdf_loader = PyPDFLoader("what-is-philosophy.pdf")
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
docs_from_pdf = pdf_loader.load_and_split(text_splitter=splitter)

print(f"Documents from PDF: {len(docs_from_pdf)}.")
inserted_ids_from_pdf = vstore.add_documents(docs_from_pdf)
print(f"Inserted {len(inserted_ids_from_pdf)} documents.")


# In[ ]:


retriever = vstore.as_retriever(search_kwargs={"k": 3})

philo_template = """
You are a philosopher that draws inspiration from great thinkers of the past
to craft well-thought answers to user questions. Use the provided context as the basis
for your answers and do not make up new reasoning paths - just mix-and-match what you are given.
Your answers must be concise and to the point, and refrain from answering about other topics than philosophy.

CONTEXT:
{context}

QUESTION: {question}

YOUR ANSWER:"""

philo_prompt = ChatPromptTemplate.from_template(philo_template)

llm = ChatOpenAI()

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | philo_prompt
    | llm
    | StrOutputParser()
)


# In[ ]:


chain.invoke("How does Russel elaborate on Peirce's idea of the security blanket?")


# For more, check out a complete RAG template using Astra DB through CQL [here](https://github.com/langchain-ai/langchain/tree/master/templates/cassandra-entomology-rag).

# ## Cleanup

# the following essentially retrieves the `Session` object from CassIO and runs a CQL `DROP TABLE` statement with it:
# 
# _(You will lose the data you stored in it.)_

# In[ ]:


cassio.config.resolve_session().execute(
    f"DROP TABLE {cassio.config.resolve_keyspace()}.cassandra_vector_demo;"
)


# ### Learn more

# For more information, extended quickstarts and additional usage examples, please visit the [CassIO documentation](https://cassio.org/frameworks/langchain/about/) for more on using the LangChain `Cassandra` vector store.

# #### Attribution statement
# 
# > Apache Cassandra, Cassandra and Apache are either registered trademarks or trademarks of the [Apache Software Foundation](http://www.apache.org/) in the United States and/or other countries.
# 
