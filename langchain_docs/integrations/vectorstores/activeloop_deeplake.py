#!/usr/bin/env python
# coding: utf-8

# #  Activeloop Deep Lake
# 
# >[Activeloop Deep Lake](https://docs.deeplake.ai/) as a Multi-Modal Vector Store that stores embeddings and their metadata including text, jsons, images, audio, video, and more. It saves the data locally, in your cloud, or on Activeloop storage. It performs hybrid search including embeddings and their attributes.
# 
# This notebook showcases basic functionality related to `Activeloop Deep Lake`. While `Deep Lake` can store embeddings, it is capable of storing any type of data. It is a serverless data lake with version control, query engine and streaming dataloaders to deep learning frameworks.  
# 
# For more information, please see the Deep Lake [documentation](https://docs.deeplake.ai/)

# ## Setting up

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-openai langchain-deeplake tiktoken')


# ## Example provided by Activeloop
# 
# [Integration with LangChain](https://docs.activeloop.ai/tutorials/vector-store/deep-lake-vector-store-in-langchain).
# 

# ## Deep Lake locally

# In[ ]:


from langchain_deeplake.vectorstores import DeeplakeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

if "ACTIVELOOP_TOKEN" not in os.environ:
    os.environ["ACTIVELOOP_TOKEN"] = getpass.getpass("activeloop token:")


# In[ ]:


from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# ### Create a local dataset
# 
# Create a dataset locally at `./my_deeplake/`, then run similarity search. The Deeplake+LangChain integration uses Deep Lake datasets under the hood, so `dataset` and `vector store` are used interchangeably. To create a dataset in your own cloud, or in the Deep Lake storage, [adjust the path accordingly](https://docs.deeplake.ai/latest/getting-started/storage-and-creds/storage-options/).

# In[ ]:


db = DeeplakeVectorStore(
    dataset_path="./my_deeplake/", embedding_function=embeddings, overwrite=True
)
db.add_documents(docs)
# or shorter
# db = DeepLake.from_documents(docs, dataset_path="./my_deeplake/", embedding_function=embeddings, overwrite=True)


# ### Query dataset

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)


# In[ ]:


print(docs[0].page_content)


# Later, you can reload the dataset without recomputing embeddings

# In[ ]:


db = DeeplakeVectorStore(
    dataset_path="./my_deeplake/", embedding_function=embeddings, read_only=True
)
docs = db.similarity_search(query)


# Setting `read_only=True` revents accidental modifications to the vector store when updates are not needed. This ensures that the data remains unchanged unless explicitly intended. It is generally a good practice to specify this argument to avoid unintended updates.
# 

# ### Retrieval Question/Answering

# In[ ]:


from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    chain_type="stuff",
    retriever=db.as_retriever(),
)


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
qa.run(query)


# ### Attribute based filtering in metadata

# Let's create another vector store containing metadata with the year the documents were created.

# In[ ]:


import random

for d in docs:
    d.metadata["year"] = random.randint(2012, 2014)

db = DeeplakeVectorStore.from_documents(
    docs, embeddings, dataset_path="./my_deeplake/", overwrite=True
)


# In[ ]:


db.similarity_search(
    "What did the president say about Ketanji Brown Jackson",
    filter={"metadata": {"year": 2013}},
)


# ### Choosing distance function
# Distance function `L2` for Euclidean, `cos` for cosine similarity
# 

# In[ ]:


db.similarity_search(
    "What did the president say about Ketanji Brown Jackson?", distance_metric="l2"
)


# ### Maximal Marginal relevance
# Using maximal marginal relevance

# In[ ]:


db.max_marginal_relevance_search(
    "What did the president say about Ketanji Brown Jackson?"
)


# ### Delete dataset

# In[ ]:


db.delete_dataset()


# ## Deep Lake datasets on cloud (Activeloop, AWS, GCS, etc.) or in memory
# By default, Deep Lake datasets are stored locally. To store them in memory, in the Deep Lake Managed DB, or in any object storage, you can provide the [corresponding path and credentials when creating the vector store](https://docs.deeplake.ai/latest/getting-started/storage-and-creds/storage-options/). Some paths require registration with Activeloop and creation of an API token that can be [retrieved here](https://app.activeloop.ai/)

# In[ ]:


os.environ["ACTIVELOOP_TOKEN"] = activeloop_token


# In[ ]:


# Embed and store the texts
username = "<USERNAME_OR_ORG>"  # your username on app.activeloop.ai
dataset_path = f"hub://{username}/langchain_testing_python"  # could be also ./local/path (much faster locally), s3://bucket/path/to/dataset, gcs://path/to/dataset, etc.

docs = text_splitter.split_documents(documents)

embedding = OpenAIEmbeddings()
db = DeeplakeVectorStore(
    dataset_path=dataset_path, embedding_function=embeddings, overwrite=True
)
ids = db.add_documents(docs)


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)
print(docs[0].page_content)


# In[ ]:


# Embed and store the texts
username = "<USERNAME_OR_ORG>"  # your username on app.activeloop.ai
dataset_path = f"hub://{username}/langchain_testing"

docs = text_splitter.split_documents(documents)

embedding = OpenAIEmbeddings()
db = DeeplakeVectorStore(
    dataset_path=dataset_path,
    embedding_function=embeddings,
    overwrite=True,
)
ids = db.add_documents(docs)


# ### TQL Search

# Furthermore, the execution of queries is also supported within the similarity_search method, whereby the query can be specified utilizing Deep Lake's Tensor Query Language (TQL).

# In[ ]:


search_id = db.dataset["ids"][0]


# In[ ]:


docs = db.similarity_search(
    query=None,
    tql=f"SELECT * WHERE ids == '{search_id}'",
)


# In[ ]:


db.dataset.summary()


# ### Creating vector stores on AWS S3

# In[ ]:


dataset_path = "s3://BUCKET/langchain_test"  # could be also ./local/path (much faster locally), hub://bucket/path/to/dataset, gcs://path/to/dataset, etc.

embedding = OpenAIEmbeddings()
db = DeeplakeVectorStore.from_documents(
    docs,
    dataset_path=dataset_path,
    embedding=embeddings,
    overwrite=True,
    creds={
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
        "aws_session_token": os.environ["AWS_SESSION_TOKEN"],  # Optional
    },
)


# ## Deep Lake API
# you can access the Deep Lake  dataset at `db.vectorstore`

# In[ ]:


# get structure of the dataset
db.dataset.summary()


# In[ ]:


# get embeddings numpy array
embeds = db.dataset["embeddings"][:]


# ### Transfer local dataset to cloud
# Copy already created dataset to the cloud. You can also transfer from cloud to local.

# In[ ]:


import deeplake

username = "<USERNAME_OR_ORG>"  # your username on app.activeloop.ai
source = f"hub://{username}/langchain_testing"  # could be local, s3, gcs, etc.
destination = f"hub://{username}/langchain_test_copy"  # could be local, s3, gcs, etc.


deeplake.copy(src=source, dst=destination)


# In[ ]:


db = DeeplakeVectorStore(dataset_path=destination, embedding_function=embeddings)
db.add_documents(docs)

