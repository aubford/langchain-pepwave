#!/usr/bin/env python
# coding: utf-8

# # Typesense
# 
# > [Typesense](https://typesense.org) is an open-source, in-memory search engine, that you can either [self-host](https://typesense.org/docs/guide/install-typesense#option-2-local-machine-self-hosting) or run on [Typesense Cloud](https://cloud.typesense.org/).
# >
# > Typesense focuses on performance by storing the entire index in RAM (with a backup on disk) and also focuses on providing an out-of-the-box developer experience by simplifying available options and setting good defaults.
# >
# > It also lets you combine attribute-based filtering together with vector queries, to fetch the most relevant documents.

# This notebook shows you how to use Typesense as your VectorStore.

# Let's first install our dependencies:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  typesense openapi-schema-pydantic langchain-openai langchain-community tiktoken')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[2]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# In[6]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Typesense
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# Let's import our test dataset:

# In[19]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# In[ ]:


docsearch = Typesense.from_documents(
    docs,
    embeddings,
    typesense_client_params={
        "host": "localhost",  # Use xxx.a1.typesense.net for Typesense Cloud
        "port": "8108",  # Use 443 for Typesense Cloud
        "protocol": "http",  # Use https for Typesense Cloud
        "typesense_api_key": "xyz",
        "typesense_collection_name": "lang-chain",
    },
)


# ## Similarity Search

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
found_docs = docsearch.similarity_search(query)


# In[ ]:


print(found_docs[0].page_content)


# ## Typesense as a Retriever
# 
# Typesense, as all the other vector stores, is a LangChain Retriever, by using cosine similarity.

# In[ ]:


retriever = docsearch.as_retriever()
retriever


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
retriever.invoke(query)[0]

