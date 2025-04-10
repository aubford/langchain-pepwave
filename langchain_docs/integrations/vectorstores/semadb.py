#!/usr/bin/env python
# coding: utf-8

# # SemaDB
# 
# > [SemaDB](https://www.semafind.com/products/semadb) from [SemaFind](https://www.semafind.com) is a no fuss vector similarity database for building AI applications. The hosted `SemaDB Cloud` offers a no fuss developer experience to get started.
# 
# The full documentation of the API along with examples and an interactive playground is available on [RapidAPI](https://rapidapi.com/semafind-semadb/api/semadb).
# 
# This notebook demonstrates usage of the `SemaDB Cloud` vector store.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration

# ## Load document embeddings
# 
# To run things locally, we are using [Sentence Transformers](https://www.sbert.net/) which are commonly used for embedding sentences. You can use any embedding model LangChain offers.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  sentence_transformers')


# In[2]:


from langchain_huggingface import HuggingFaceEmbeddings

model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)


# In[3]:


from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
print(len(docs))


# ## Connect to SemaDB
# 
# SemaDB Cloud uses [RapidAPI keys](https://rapidapi.com/semafind-semadb/api/semadb) to authenticate. You can obtain yours by creating a free RapidAPI account.

# In[4]:


import getpass
import os

if "SEMADB_API_KEY" not in os.environ:
    os.environ["SEMADB_API_KEY"] = getpass.getpass("SemaDB API Key:")


# In[5]:


from langchain_community.vectorstores import SemaDB
from langchain_community.vectorstores.utils import DistanceStrategy


# The parameters to the SemaDB vector store reflect the API directly:
# 
# - "mycollection": is the collection name in which we will store these vectors.
# - 768: is dimensions of the vectors. In our case, the sentence transformer embeddings yield 768 dimensional vectors.
# - API_KEY: is your RapidAPI key.
# - embeddings: correspond to how the embeddings of documents, texts and queries will be generated.
# - DistanceStrategy: is the distance metric used. The wrapper automatically normalises vectors if COSINE is used.

# In[6]:


db = SemaDB("mycollection", 768, embeddings, DistanceStrategy.COSINE)

# Create collection if running for the first time. If the collection
# already exists this will fail.
db.create_collection()


# The SemaDB vector store wrapper adds the document text as point metadata to collect later. Storing large chunks of text is *not recommended*. If you are indexing a large collection, we instead recommend storing references to the documents such as external Ids.

# In[7]:


db.add_documents(docs)[:2]


# ## Similarity Search
# 
# We use the default LangChain similarity search interface to search for the most similar sentences.

# In[8]:


query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)
print(docs[0].page_content)


# In[9]:


docs = db.similarity_search_with_score(query)
docs[0]


# ## Clean up
# 
# You can delete the collection to remove all data.

# In[10]:


db.delete_collection()


# In[ ]:




