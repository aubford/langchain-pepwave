#!/usr/bin/env python
# coding: utf-8

# # Xata
# 
# > [Xata](https://xata.io) is a serverless data platform, based on PostgreSQL. It provides a Python SDK for interacting with your database, and a UI for managing your data.
# > Xata has a native vector type, which can be added to any table, and supports similarity search. LangChain inserts vectors directly to Xata, and queries it for the nearest neighbors of a given vector, so that you can use all the LangChain Embeddings integrations with Xata.

# This notebook guides you how to use Xata as a VectorStore.

# ## Setup
# 
# ### Create a database to use as a vector store
# 
# In the [Xata UI](https://app.xata.io) create a new database. You can name it whatever you want, in this notepad we'll use `langchain`.
# Create a table, again you can name it anything, but we will use `vectors`. Add the following columns via the UI:
# 
# * `content` of type "Text". This is used to store the `Document.pageContent` values.
# * `embedding` of type "Vector". Use the dimension used by the model you plan to use. In this notebook we use OpenAI embeddings, which have 1536 dimensions.
# * `source` of type "Text". This is used as a metadata column by this example.
# * any other columns you want to use as metadata. They are populated from the `Document.metadata` object. For example, if in the `Document.metadata` object you have a `title` property, you can create a `title` column in the table and it will be populated.
# 

# Let's first install our dependencies:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  xata langchain-openai langchain-community tiktoken langchain')


# Let's load the OpenAI key to the environment. If you don't have one you can create an OpenAI account and create a key on this [page](https://platform.openai.com/account/api-keys).

# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# Similarly, we need to get the environment variables for Xata. You can create a new API key by visiting your [account settings](https://app.xata.io/settings). To find the database URL, go to the Settings page of the database that you have created. The database URL should look something like this: `https://demo-uni3q8.eu-west-1.xata.sh/db/langchain`.

# In[ ]:


api_key = getpass.getpass("Xata API key: ")
db_url = input("Xata database URL (copy it from your DB settings):")


# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.xata import XataVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# ### Create the Xata vector store
# Let's import our test dataset:

# In[ ]:


loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# Now create the actual vector store, backed by the Xata table.

# In[ ]:


vector_store = XataVectorStore.from_documents(
    docs, embeddings, api_key=api_key, db_url=db_url, table_name="vectors"
)


# After running the above command, if you go to the Xata UI, you should see the documents loaded together with their embeddings.
# To use an existing Xata table that already contains vector contents, initialize the XataVectorStore constructor:

# In[ ]:


vector_store = XataVectorStore(
    api_key=api_key, db_url=db_url, embedding=embeddings, table_name="vectors"
)


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

