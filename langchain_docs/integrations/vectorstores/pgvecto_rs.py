#!/usr/bin/env python
# coding: utf-8

# # PGVecto.rs
# 
# This notebook shows how to use functionality related to the Postgres vector database ([pgvecto.rs](https://github.com/tensorchord/pgvecto.rs)).

# In[ ]:


get_ipython().run_line_magic('pip', 'install "pgvecto_rs[sdk]" langchain-community')


# In[ ]:


from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.fake import FakeEmbeddings
from langchain_community.vectorstores.pgvecto_rs import PGVecto_rs
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter


# In[ ]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = FakeEmbeddings(size=3)


# Start the database with the [official demo docker image](https://github.com/tensorchord/pgvecto.rs#installation).

# In[ ]:


get_ipython().system(' docker run --name pgvecto-rs-demo -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d tensorchord/pgvecto-rs:latest')


# Then contruct the db URL

# In[ ]:


## PGVecto.rs needs the connection string to the database.
## We will load it from the environment variables.
import os

PORT = os.getenv("DB_PORT", 5432)
HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "postgres")
PASS = os.getenv("DB_PASS", "mysecretpassword")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Run tests with shell:
URL = "postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}".format(
    port=PORT,
    host=HOST,
    username=USER,
    password=PASS,
    db_name=DB_NAME,
)


# Finally, create the VectorStore from the documents:

# In[ ]:


db1 = PGVecto_rs.from_documents(
    documents=docs,
    embedding=embeddings,
    db_url=URL,
    # The table name is f"collection_{collection_name}", so that it should be unique.
    collection_name="state_of_the_union",
)


# You can connect to the table laterly with:

# In[ ]:


# Create new empty vectorstore with collection_name.
# Or connect to an existing vectorstore in database if exists.
# Arguments should be the same as when the vectorstore was created.
db1 = PGVecto_rs.from_collection_name(
    embedding=embeddings,
    db_url=URL,
    collection_name="state_of_the_union",
)


# Make sure that the user is permitted to create a table.

# ## Similarity search with score

# ### Similarity Search with Euclidean Distance (Default)

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs: List[Document] = db1.similarity_search(query, k=4)
for doc in docs:
    print(doc.page_content)
    print("======================")


# ### Similarity Search with Filter

# In[ ]:


from pgvecto_rs.sdk.filters import meta_contains

query = "What did the president say about Ketanji Brown Jackson"
docs: List[Document] = db1.similarity_search(
    query, k=4, filter=meta_contains({"source": "../../how_to/state_of_the_union.txt"})
)

for doc in docs:
    print(doc.page_content)
    print("======================")


# Or:

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs: List[Document] = db1.similarity_search(
    query, k=4, filter={"source": "../../how_to/state_of_the_union.txt"}
)

for doc in docs:
    print(doc.page_content)
    print("======================")

