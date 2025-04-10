#!/usr/bin/env python
# coding: utf-8

# # Psychic
# This notebook covers how to load documents from `Psychic`. See [here](/docs/integrations/providers/psychic) for more details.
# 
# ## Prerequisites
# 1. Follow the Quick Start section in [this document](/docs/integrations/providers/psychic)
# 2. Log into the [Psychic dashboard](https://dashboard.psychic.dev/) and get your secret key
# 3. Install the frontend react library into your web app and have a user authenticate a connection. The connection will be created using the connection id that you specify.

# ## Loading documents
# 
# Use the `PsychicLoader` class to load in documents from a connection. Each connection has a connector id (corresponding to the SaaS app that was connected) and a connection id (which you passed in to the frontend library).

# In[7]:


# Uncomment this to install psychicapi if you don't already have it installed
get_ipython().system('poetry run pip -q install psychicapi langchain-chroma')


# In[ ]:


from langchain_community.document_loaders import PsychicLoader
from psychicapi import ConnectorId

# Create a document loader for google drive. We can also load from other connectors by setting the connector_id to the appropriate value e.g. ConnectorId.notion.value
# This loader uses our test credentials
google_drive_loader = PsychicLoader(
    api_key="7ddb61c1-8b6a-4d31-a58e-30d1c9ea480e",
    connector_id=ConnectorId.gdrive.value,
    connection_id="google-test",
)

documents = google_drive_loader.load()


# ## Converting the docs to embeddings 
# 
# We can now convert these documents into embeddings and store them in a vector database like Chroma

# In[ ]:


from langchain.chains import RetrievalQAWithSourcesChain
from langchain_chroma import Chroma
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# In[ ]:


text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(texts, embeddings)
chain = RetrievalQAWithSourcesChain.from_chain_type(
    OpenAI(temperature=0), chain_type="stuff", retriever=docsearch.as_retriever()
)
chain({"question": "what is psychic?"}, return_only_outputs=True)

