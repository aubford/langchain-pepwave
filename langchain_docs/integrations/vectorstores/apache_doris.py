#!/usr/bin/env python
# coding: utf-8

# # Apache Doris
# 
# >[Apache Doris](https://doris.apache.org/) is a modern data warehouse for real-time analytics.
# It delivers lightning-fast analytics on real-time data at scale.
# 
# >Usually `Apache Doris` is categorized into OLAP, and it has showed excellent performance in [ClickBench — a Benchmark For Analytical DBMS](https://benchmark.clickhouse.com/). Since it has a super-fast vectorized execution engine, it could also be used as a fast vectordb.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration
# 
# Here we'll show how to use the Apache Doris Vector Store.

# ## Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  pymysql')


# Set `update_vectordb = False` at the beginning. If there is no docs updated, then we don't need to rebuild the embeddings of docs

# In[ ]:


get_ipython().system('pip install  sqlalchemy')
get_ipython().system('pip install langchain')


# In[1]:


from langchain.chains import RetrievalQA
from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.vectorstores.apache_doris import (
    ApacheDoris,
    ApacheDorisSettings,
)
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import TokenTextSplitter

update_vectordb = False


# ## Load docs and split them into tokens

# Load all markdown files under the `docs` directory
# 
# for Apache Doris documents, you can clone repo from https://github.com/apache/doris, and there is `docs` directory in it.

# In[2]:


loader = DirectoryLoader(
    "./docs", glob="**/*.md", loader_cls=UnstructuredMarkdownLoader
)
documents = loader.load()


# Split docs into tokens, and set `update_vectordb = True` because there are new docs/tokens.

# In[3]:


# load text splitter and split docs into snippets of text
text_splitter = TokenTextSplitter(chunk_size=400, chunk_overlap=50)
split_docs = text_splitter.split_documents(documents)

# tell vectordb to update text embeddings
update_vectordb = True


# split_docs[-20]

# print("# docs  = %d, # splits = %d" % (len(documents), len(split_docs)))

# ## Create vectordb instance

# ### Use Apache Doris as vectordb

# In[7]:


def gen_apache_doris(update_vectordb, embeddings, settings):
    if update_vectordb:
        docsearch = ApacheDoris.from_documents(split_docs, embeddings, config=settings)
    else:
        docsearch = ApacheDoris(embeddings, settings)
    return docsearch


# ## Convert tokens into embeddings and put them into vectordb

# Here we use Apache Doris as vectordb, you can configure Apache Doris instance via `ApacheDorisSettings`.
# 
# Configuring Apache Doris instance is pretty much like configuring mysql instance. You need to specify:
# 1. host/port
# 2. username(default: 'root')
# 3. password(default: '')
# 4. database(default: 'default')
# 5. table(default: 'langchain')

# In[8]:


import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()


# In[ ]:


update_vectordb = True

embeddings = OpenAIEmbeddings()

# configure Apache Doris settings(host/port/user/pw/db)
settings = ApacheDorisSettings()
settings.port = 9030
settings.host = "172.30.34.130"
settings.username = "root"
settings.password = ""
settings.database = "langchain"
docsearch = gen_apache_doris(update_vectordb, embeddings, settings)

print(docsearch)

update_vectordb = False


# ## Build QA and ask question to it

# In[ ]:


llm = OpenAI()
qa = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=docsearch.as_retriever()
)
query = "what is apache doris"
resp = qa.run(query)
print(resp)

