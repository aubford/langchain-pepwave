#!/usr/bin/env python
# coding: utf-8

# # ERNIE
# 
# [ERNIE Embedding-V1](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/alj562vvu) is a text representation model based on `Baidu Wenxin` large-scale model technology, 
# which converts text into a vector form represented by numerical values, and is used in text retrieval, information recommendation, knowledge mining and other scenarios.

# **Deprecated Warning**
# 
# We recommend users using `langchain_community.embeddings.ErnieEmbeddings` 
# to use `langchain_community.embeddings.QianfanEmbeddingsEndpoint` instead.
# 
# documentation for `QianfanEmbeddingsEndpoint` is [here](/docs/integrations/text_embedding/baidu_qianfan_endpoint/).
# 
# they are 2 why we recommend users to use `QianfanEmbeddingsEndpoint`:
# 
# 1. `QianfanEmbeddingsEndpoint` support more embedding model in the Qianfan platform.
# 2. `ErnieEmbeddings` is lack of maintenance and deprecated.

# Some tips for migration:

# In[ ]:


from langchain_community.embeddings import QianfanEmbeddingsEndpoint

embeddings = QianfanEmbeddingsEndpoint(
    qianfan_ak="your qianfan ak",
    qianfan_sk="your qianfan sk",
)


# ## Usage

# In[ ]:


from langchain_community.embeddings import ErnieEmbeddings


# In[ ]:


embeddings = ErnieEmbeddings()


# In[ ]:


query_result = embeddings.embed_query("foo")


# In[ ]:


doc_results = embeddings.embed_documents(["foo"])

