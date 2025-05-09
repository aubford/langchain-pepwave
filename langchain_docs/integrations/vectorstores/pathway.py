#!/usr/bin/env python
# coding: utf-8

# # Pathway
# > [Pathway](https://pathway.com/) is an open data processing framework. It allows you to easily develop data transformation pipelines and Machine Learning applications that work with live data sources and changing data.
# 
# This notebook demonstrates how to use a live `Pathway` data indexing pipeline with `Langchain`. You can query the results of this pipeline from your chains in the same manner as you would a regular vector store. However, under the hood, Pathway updates the index on each data change giving you always up-to-date answers.
# 
# In this notebook, we will use a [public demo document processing pipeline](https://pathway.com/solutions/ai-pipelines#try-it-out) that:
# 
# 1. Monitors several cloud data sources for data changes.
# 2. Builds a vector index for the data.
# 
# To have your own document processing pipeline check the [hosted offering](https://pathway.com/solutions/ai-pipelines) or [build your own](https://pathway.com/developers/user-guide/llm-xpack/vectorstore_pipeline/).
# 
# We will connect to the index using a `VectorStore` client, which implements the `similarity_search` function to retrieve matching documents.
# 
# The basic pipeline used in this document allows to effortlessly build a simple vector index of files stored in a cloud location. However, Pathway provides everything needed to build realtime data pipelines and apps, including SQL-like able operations such as groupby-reductions and joins between disparate data sources, time-based grouping and windowing of data, and a wide array of connectors.
# 
# You'll need to install `langchain-community` with `pip install -qU langchain-community` to use this integration

# ## Querying the data pipeline

# To instantiate and configure the client you need to provide either the `url` or the `host` and `port` of your document indexing pipeline. In the code below we use a publicly available [demo pipeline](https://pathway.com/solutions/ai-pipelines#try-it-out), which REST API you can access at `https://demo-document-indexing.pathway.stream`. This demo ingests documents from [Google Drive](https://drive.google.com/drive/u/0/folders/1cULDv2OaViJBmOfG5WB0oWcgayNrGtVs) and [Sharepoint](https://navalgo.sharepoint.com/sites/ConnectorSandbox/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FConnectorSandbox%2FShared%20Documents%2FIndexerSandbox&p=true&ga=1) and maintains an index for retrieving documents.

# In[ ]:


from langchain_community.vectorstores import PathwayVectorClient

client = PathwayVectorClient(url="https://demo-document-indexing.pathway.stream")


#  And we can start asking queries

# In[ ]:


query = "What is Pathway?"
docs = client.similarity_search(query)


# In[ ]:


print(docs[0].page_content)


#  **Your turn!** [Get your pipeline](https://pathway.com/solutions/ai-pipelines) or upload [new documents](https://chat-realtime-sharepoint-gdrive.demo.pathway.com/) to the demo pipeline and retry the query!

# ## Filtering based on file metadata
# 
# We support document filtering using [jmespath](https://jmespath.org/) expressions, for instance:

# In[ ]:


# take into account only sources modified later than unix timestamp
docs = client.similarity_search(query, metadata_filter="modified_at >= `1702672093`")

# take into account only sources modified later than unix timestamp
docs = client.similarity_search(query, metadata_filter="owner == `james`")

# take into account only sources with path containing 'repo_readme'
docs = client.similarity_search(query, metadata_filter="contains(path, 'repo_readme')")

# and of two conditions
docs = client.similarity_search(
    query, metadata_filter="owner == `james` && modified_at >= `1702672093`"
)

# or of two conditions
docs = client.similarity_search(
    query, metadata_filter="owner == `james` || modified_at >= `1702672093`"
)


# ## Getting information on indexed files

#  `PathwayVectorClient.get_vectorstore_statistics()` gives essential statistics on the state of the vector store, like the number of indexed files and the timestamp of last updated one. You can use it in your chains to tell the user how fresh is your knowledge base.

# In[ ]:


client.get_vectorstore_statistics()


# ## Your own pipeline

# ### Running in production
# To have your own Pathway data indexing pipeline check the Pathway's offer for [hosted pipelines](https://pathway.com/solutions/ai-pipelines). You can also run your own Pathway pipeline - for information on how to build the pipeline refer to [Pathway guide](https://pathway.com/developers/user-guide/llm-xpack/vectorstore_pipeline/).

# ### Processing documents
# 
# The vectorization pipeline supports pluggable components for parsing, splitting and embedding documents. For embedding and splitting you can use [Langchain components](https://pathway.com/developers/user-guide/llm-xpack/vectorstore_pipeline/#langchain) or check [embedders](https://pathway.com/developers/api-docs/pathway-xpacks-llm/embedders) and [splitters](https://pathway.com/developers/api-docs/pathway-xpacks-llm/splitters) available in Pathway. If parser is not provided, it defaults to `UTF-8` parser. You can find available parsers [here](https://github.com/pathwaycom/pathway/blob/main/python/pathway/xpacks/llm/parser.py).

# 
