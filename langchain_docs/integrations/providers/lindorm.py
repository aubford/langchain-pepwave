#!/usr/bin/env python
# coding: utf-8

# # Lindorm
# 
# Lindorm is a cloud-native multimodal database from Alibaba-Cloud, It supports unified access and integrated processing of various types of data, including wide tables, time-series, text, objects, streams, and spatial data. It is compatible with multiple standard interfaces such as SQL, HBase/Cassandra/S3, TSDB, HDFS, Solr, and Kafka, and seamlessly integrates with third-party ecosystem tools. This makes it suitable for scenarios such as logging, monitoring, billing, advertising, social networking, travel, and risk control. Lindorm is also one of the databases that support Alibaba's core businesses. 
# 
# To use the AI and vector capabilities of Lindorm, you should [get the service](https://help.aliyun.com/document_detail/174640.html?spm=a2c4g.11186623.help-menu-172543.d_0_1_0.4c6367558DN8Uq) and install `langchain-lindorm-integration` package.

# In[2]:


get_ipython().system('pip install -U langchain-lindorm-integration')


# ## Embeddings
# 
# To use the embedding model deployed in Lindorm AI Service, import the LindormAIEmbeddings. 

# In[ ]:


from langchain_lindorm_integration import LindormAIEmbeddings


# ## Rerank
# 
# The Lindorm AI Service also supports reranking.

# In[ ]:


from langchain_lindorm_integration.reranker import LindormAIRerank


# ## Vector Store
# 
# Lindorm also supports vector store.

# In[ ]:


from langchain_lindorm_integration import LindormVectorStore


# ## ByteStore
# 
# Use ByteStore from Lindorm

# In[ ]:


from langchain_lindorm_integration import LindormByteStore

