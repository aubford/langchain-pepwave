#!/usr/bin/env python
# coding: utf-8

# # OpenSearch
# 
# > [OpenSearch](https://opensearch.org/) is a scalable, flexible, and extensible open-source software suite for search, analytics, and observability applications licensed under Apache 2.0. `OpenSearch` is a distributed search and analytics engine based on `Apache Lucene`.
# 
# 
# This notebook shows how to use functionality related to the `OpenSearch` database.
# 
# To run, you should have an OpenSearch instance up and running: [see here for an easy Docker installation](https://hub.docker.com/r/opensearchproject/opensearch).
# 
# `similarity_search` by default performs the Approximate k-NN Search which uses one of the several algorithms like lucene, nmslib, faiss recommended for
# large datasets. To perform brute force search we have other search methods known as Script Scoring and Painless Scripting.
# Check [this](https://opensearch.org/docs/latest/search-plugins/knn/index/) for more details.

# ## Installation
# Install the Python client.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  opensearch-py langchain-community')


# We want to use OpenAIEmbeddings so we have to get the OpenAI API Key.

# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# In[1]:


from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# In[ ]:


from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# ## similarity_search using Approximate k-NN
# 
# `similarity_search` using `Approximate k-NN` Search with Custom Parameters

# In[ ]:


docsearch = OpenSearchVectorSearch.from_documents(
    docs, embeddings, opensearch_url="http://localhost:9200"
)

# If using the default Docker installation, use this instantiation instead:
# docsearch = OpenSearchVectorSearch.from_documents(
#     docs,
#     embeddings,
#     opensearch_url="https://localhost:9200",
#     http_auth=("admin", "admin"),
#     use_ssl = False,
#     verify_certs = False,
#     ssl_assert_hostname = False,
#     ssl_show_warn = False,
# )


# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(query, k=10)


# In[ ]:


print(docs[0].page_content)


# In[ ]:


docsearch = OpenSearchVectorSearch.from_documents(
    docs,
    embeddings,
    opensearch_url="http://localhost:9200",
    engine="faiss",
    space_type="innerproduct",
    ef_construction=256,
    m=48,
)

query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(query)


# In[ ]:


print(docs[0].page_content)


# ## similarity_search using Script Scoring
# 
# `similarity_search` using `Script Scoring` with Custom Parameters

# In[ ]:


docsearch = OpenSearchVectorSearch.from_documents(
    docs, embeddings, opensearch_url="http://localhost:9200", is_appx_search=False
)

query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(
    "What did the president say about Ketanji Brown Jackson",
    k=1,
    search_type="script_scoring",
)


# In[ ]:


print(docs[0].page_content)


# ## similarity_search using Painless Scripting
# 
# `similarity_search` using `Painless Scripting` with Custom Parameters

# In[ ]:


docsearch = OpenSearchVectorSearch.from_documents(
    docs, embeddings, opensearch_url="http://localhost:9200", is_appx_search=False
)
filter = {"bool": {"filter": {"term": {"text": "smuggling"}}}}
query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(
    "What did the president say about Ketanji Brown Jackson",
    search_type="painless_scripting",
    space_type="cosineSimilarity",
    pre_filter=filter,
)


# In[ ]:


print(docs[0].page_content)


# ## Maximum marginal relevance search (MMR)
# If you’d like to look up for some similar documents, but you’d also like to receive diverse results, MMR is method you should consider. Maximal marginal relevance optimizes for similarity to query AND diversity among selected documents.

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.max_marginal_relevance_search(query, k=2, fetch_k=10, lambda_param=0.5)


# ## Using a preexisting OpenSearch instance
# 
# It's also possible to use a preexisting OpenSearch instance with documents that already have vectors present.

# In[ ]:


# this is just an example, you would need to change these values to point to another opensearch instance
docsearch = OpenSearchVectorSearch(
    index_name="index-*",
    embedding_function=embeddings,
    opensearch_url="http://localhost:9200",
)

# you can specify custom field names to match the fields you're using to store your embedding, document text value, and metadata
docs = docsearch.similarity_search(
    "Who was asking about getting lunch today?",
    search_type="script_scoring",
    space_type="cosinesimil",
    vector_field="message_embedding",
    text_field="message",
    metadata_field="message_metadata",
)


# ## Using AOSS (Amazon OpenSearch Service Serverless)
# 
# It is an example of the `AOSS` with `faiss` engine and `efficient_filter`.
# 
# 
# We need to install several `python` packages.

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  boto3 requests requests-aws4auth')


# In[ ]:


import boto3
from opensearchpy import RequestsHttpConnection
from requests_aws4auth import AWS4Auth

service = "aoss"  # must set the service as 'aoss'
region = "us-east-2"
credentials = boto3.Session(
    aws_access_key_id="xxxxxx", aws_secret_access_key="xxxxx"
).get_credentials()
awsauth = AWS4Auth("xxxxx", "xxxxxx", region, service, session_token=credentials.token)

docsearch = OpenSearchVectorSearch.from_documents(
    docs,
    embeddings,
    opensearch_url="host url",
    http_auth=awsauth,
    timeout=300,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    index_name="test-index-using-aoss",
    engine="faiss",
)

docs = docsearch.similarity_search(
    "What is feature selection",
    efficient_filter=filter,
    k=200,
)


# ## Using AOS (Amazon OpenSearch Service)

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  boto3')


# In[ ]:


# This is just an example to show how to use Amazon OpenSearch Service, you need to set proper values.
import boto3
from opensearchpy import RequestsHttpConnection

service = "es"  # must set the service as 'es'
region = "us-east-2"
credentials = boto3.Session(
    aws_access_key_id="xxxxxx", aws_secret_access_key="xxxxx"
).get_credentials()
awsauth = AWS4Auth("xxxxx", "xxxxxx", region, service, session_token=credentials.token)

docsearch = OpenSearchVectorSearch.from_documents(
    docs,
    embeddings,
    opensearch_url="host url",
    http_auth=awsauth,
    timeout=300,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    index_name="test-index",
)

docs = docsearch.similarity_search(
    "What is feature selection",
    k=200,
)

