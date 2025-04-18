#!/usr/bin/env python
# coding: utf-8

# # Tigris
# 
# > [Tigris](https://tigrisdata.com) is an open-source Serverless NoSQL Database and Search Platform designed to simplify building high-performance vector search applications.
# > `Tigris` eliminates the infrastructure complexity of managing, operating, and synchronizing multiple tools, allowing you to focus on building great applications instead.

# This notebook guides you how to use Tigris as your VectorStore

# **Pre requisites**
# 1. An OpenAI account. You can sign up for an account [here](https://platform.openai.com/)
# 2. [Sign up for a free Tigris account](https://console.preview.tigrisdata.cloud). Once you have signed up for the Tigris account, create a new project called `vectordemo`. Next, make a note of the *Uri* for the region you've created your project in, the **clientId** and **clientSecret**. You can get all this information from the **Application Keys** section of the project.

# Let's first install our dependencies:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  tigrisdb openapi-schema-pydantic langchain-openai langchain-community tiktoken')


# We will load the `OpenAI` api key and `Tigris` credentials in our environment

# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
if "TIGRIS_PROJECT" not in os.environ:
    os.environ["TIGRIS_PROJECT"] = getpass.getpass("Tigris Project Name:")
if "TIGRIS_CLIENT_ID" not in os.environ:
    os.environ["TIGRIS_CLIENT_ID"] = getpass.getpass("Tigris Client Id:")
if "TIGRIS_CLIENT_SECRET" not in os.environ:
    os.environ["TIGRIS_CLIENT_SECRET"] = getpass.getpass("Tigris Client Secret:")


# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Tigris
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# ### Initialize Tigris vector store
# Let's import our test dataset:

# In[ ]:


loader = TextLoader("../../../state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# In[ ]:


vector_store = Tigris.from_documents(docs, embeddings, index_name="my_embeddings")


# ### Similarity Search

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
found_docs = vector_store.similarity_search(query)
print(found_docs)


# ### Similarity Search with score (vector distance)

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
result = vector_store.similarity_search_with_score(query)
for doc, score in result:
    print(f"document={doc}, score={score}")

