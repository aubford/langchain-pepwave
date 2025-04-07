#!/usr/bin/env python
# coding: utf-8

# # ManticoreSearch VectorStore
# 
# [ManticoreSearch](https://manticoresearch.com/) is an open-source search engine that offers fast, scalable, and user-friendly capabilities. Originating as a fork of [Sphinx Search](http://sphinxsearch.com/), it has evolved to incorporate modern search engine features and improvements. ManticoreSearch distinguishes itself with its robust performance and ease of integration into various applications.
# 
# ManticoreSearch has recently introduced [vector search capabilities](https://manual.manticoresearch.com/dev/Searching/KNN), starting with search engine version 6.2 and only with [manticore-columnar-lib](https://github.com/manticoresoftware/columnar) package installed. This feature is a considerable advancement, allowing for the execution of searches based on vector similarity.
# 
# As of now, the vector search functionality is only accessible in the developmental (dev) versions of the search engine. Consequently, it is imperative to employ a developmental [manticoresearch-dev](https://pypi.org/project/manticoresearch-dev/) Python client for utilizing this feature effectively.

# ## Setting up environments

# Starting Docker-container with ManticoreSearch and installing manticore-columnar-lib package (optional)

# In[14]:


import time

# Start container
containers = get_ipython().getoutput('docker ps --filter "name=langchain-manticoresearch-server" -q')
if len(containers) == 0:
    get_ipython().system('docker run -d -p 9308:9308 --name langchain-manticoresearch-server manticoresearch/manticore:dev')
    time.sleep(20)  # Wait for the container to start up

# Get ID of container
container_id = containers[0]

# Install manticore-columnar-lib package as root user
get_ipython().system('docker exec -it --user 0 {container_id} apt-get update')
get_ipython().system('docker exec -it --user 0 {container_id} apt-get install -y manticore-columnar-lib')

# Restart container
get_ipython().system('docker restart {container_id}')


# Installing ManticoreSearch python client

# In[15]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet manticoresearch-dev')


# We want to use OpenAIEmbeddings so we have to get the OpenAI API Key.

# In[16]:


from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import ManticoreSearch, ManticoreSearchSettings
from langchain_text_splitters import CharacterTextSplitter


# In[17]:


from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../modules/paul_graham_essay.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = GPT4AllEmbeddings()


# In[18]:


for d in docs:
    d.metadata = {"some": "metadata"}
settings = ManticoreSearchSettings(table="manticoresearch_vector_search_example")
docsearch = ManticoreSearch.from_documents(docs, embeddings, config=settings)

query = "Robert Morris is"
docs = docsearch.similarity_search(query)
print(docs)

