#!/usr/bin/env python
# coding: utf-8

# # TileDB
# 
# > [TileDB](https://github.com/TileDB-Inc/TileDB) is a powerful engine for indexing and querying dense and sparse multi-dimensional arrays.
# 
# > TileDB offers ANN search capabilities using the [TileDB-Vector-Search](https://github.com/TileDB-Inc/TileDB-Vector-Search) module. It provides serverless execution of ANN queries and storage of vector indexes both on local disk and cloud object stores (i.e. AWS S3).
# 
# More details in:
# -  [Why TileDB as a Vector Database](https://tiledb.com/blog/why-tiledb-as-a-vector-database)
# -  [TileDB 101: Vector Search](https://tiledb.com/blog/tiledb-101-vector-search)
# 
# This notebook shows how to use the `TileDB` vector database.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  tiledb-vector-search langchain-community')


# ## Basic Example

# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import TileDB
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

raw_documents = TextLoader("../../how_to/state_of_the_union.txt").load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
db = TileDB.from_documents(
    documents, embeddings, index_uri="/tmp/tiledb_index", index_type="FLAT"
)


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)
docs[0].page_content


# ### Similarity search by vector

# In[ ]:


embedding_vector = embeddings.embed_query(query)
docs = db.similarity_search_by_vector(embedding_vector)
docs[0].page_content


# ### Similarity search with score

# In[ ]:


docs_and_scores = db.similarity_search_with_score(query)
docs_and_scores[0]


# ## Maximal Marginal Relevance Search (MMR)

# In addition to using similarity search in the retriever object, you can also use `mmr` as retriever.

# In[ ]:


retriever = db.as_retriever(search_type="mmr")
retriever.invoke(query)


# Or use `max_marginal_relevance_search` directly:

# In[ ]:


db.max_marginal_relevance_search(query, k=2, fetch_k=10)

