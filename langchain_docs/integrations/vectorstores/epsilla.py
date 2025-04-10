#!/usr/bin/env python
# coding: utf-8

# # Epsilla
# 
# >[Epsilla](https://www.epsilla.com) is an open-source vector database that leverages the advanced parallel graph traversal techniques for vector indexing. Epsilla is licensed under GPL-3.0.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration
# 
# This notebook shows how to use the functionalities related to the `Epsilla` vector database.
# 
# As a prerequisite, you need to have a running Epsilla vector database (for example, through our docker image), and install the ``pyepsilla`` package. View full docs at [docs](https://epsilla-inc.gitbook.io/epsilladb/quick-start).

# In[ ]:


get_ipython().system('pip/pip3 install pyepsilla')


# We want to use OpenAIEmbeddings so we have to get the OpenAI API Key. 

# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# OpenAI API Key: ········

# In[ ]:


from langchain_community.vectorstores import Epsilla
from langchain_openai import OpenAIEmbeddings


# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()

documents = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0).split_documents(
    documents
)

embeddings = OpenAIEmbeddings()


# Epsilla vectordb is running with default host "localhost" and port "8888". We have a custom db path, db name and collection name instead of the default ones.

# In[ ]:


from pyepsilla import vectordb

client = vectordb.Client()
vector_store = Epsilla.from_documents(
    documents,
    embeddings,
    client,
    db_path="/tmp/mypath",
    db_name="MyDB",
    collection_name="MyCollection",
)


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = vector_store.similarity_search(query)
print(docs[0].page_content)


# In state after state, new laws have been passed, not only to suppress the vote, but to subvert entire elections.
# 
# We cannot let this happen.
# 
# Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections.
# 
# Tonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service.
# 
# One of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court.
# 
# And I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.
