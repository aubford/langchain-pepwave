#!/usr/bin/env python
# coding: utf-8

# ---
# sidebar_label: SQLiteVec
# ---

# # SQLite as a Vector Store with SQLiteVec
# 
# This notebook covers how to get started with the SQLiteVec vector store.
# 
# >[SQLite-Vec](https://alexgarcia.xyz/sqlite-vec/) is an `SQLite` extension designed for vector search, emphasizing local-first operations and easy integration into applications without external servers. It is the successor to [SQLite-VSS](https://alexgarcia.xyz/sqlite-vss/) by the same author. It is written in zero-dependency C and designed to be easy to build and use.
# 
# This notebook shows how to use the `SQLiteVec` vector database.

# ## Setup
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration

# In[ ]:


# You need to install sqlite-vec as a dependency.
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  sqlite-vec')


# ### Credentials
# SQLiteVec does not require any credentials to use as the vector store is a simple SQLite file.

# ## Initialization

# In[ ]:


from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import SQLiteVec

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = SQLiteVec(
    table="state_union", db_file="/tmp/vec.db", embedding=embedding_function
)


# ## Manage vector store

# ### Add items to vector store

# In[ ]:


vector_store.add_texts(texts=["Ketanji Brown Jackson is awesome", "foo", "bar"])


# ### Update items in vector store
# Not supported yet

# ### Delete items from vector store
# Not supported yet

# ## Query vector store

# ### Query directly

# In[ ]:


data = vector_store.similarity_search("Ketanji Brown Jackson", k=4)


# ### Query by turning into retriever
# Not supported yet

# ## Usage for retrieval-augmented generation
# Refer to the documentation on sqlite-vec at https://alexgarcia.xyz/sqlite-vec/ for more information on how to use it for retrieval-augmented generation.

# ## API reference
# For detailed documentation of all SQLiteVec features and configurations head to the API reference: https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.sqlitevec.SQLiteVec.html

# ### Other examples

# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import SQLiteVec
from langchain_text_splitters import CharacterTextSplitter

# load the document and split it into chunks
loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
texts = [doc.page_content for doc in docs]


# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


# load it in sqlite-vss in a table named state_union.
# the db_file parameter is the name of the file you want
# as your sqlite database.
db = SQLiteVec.from_texts(
    texts=texts,
    embedding=embedding_function,
    table="state_union",
    db_file="/tmp/vec.db",
)

# query it
query = "What did the president say about Ketanji Brown Jackson"
data = db.similarity_search(query)

# print results
data[0].page_content


# ### Example using existing SQLite connection

# In[7]:


from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import SQLiteVec
from langchain_text_splitters import CharacterTextSplitter

# load the document and split it into chunks
loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
texts = [doc.page_content for doc in docs]


# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
connection = SQLiteVec.create_connection(db_file="/tmp/vec.db")

db1 = SQLiteVec(
    table="state_union", embedding=embedding_function, connection=connection
)

db1.add_texts(["Ketanji Brown Jackson is awesome"])
# query it again
query = "What did the president say about Ketanji Brown Jackson"
data = db1.similarity_search(query)

# print results
data[0].page_content

