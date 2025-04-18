#!/usr/bin/env python
# coding: utf-8

# # Alibaba Cloud OpenSearch
# 
# >[Alibaba Cloud Opensearch](https://www.alibabacloud.com/product/opensearch) is a one-stop platform to develop intelligent search services. `OpenSearch` was built on the large-scale distributed search engine developed by `Alibaba`. `OpenSearch` serves more than 500 business cases in Alibaba Group and thousands of Alibaba Cloud customers. `OpenSearch` helps develop search services in different search scenarios, including e-commerce, O2O, multimedia, the content industry, communities and forums, and big data query in enterprises.
# 
# >`OpenSearch` helps you develop high-quality, maintenance-free, and high-performance intelligent search services to provide your users with high search efficiency and accuracy.
# 
# >`OpenSearch` provides the vector search feature. In specific scenarios, especially test question search and image search scenarios, you can use the vector search feature together with the multimodal search feature to improve the accuracy of search results.
# 
# This notebook shows how to use functionality related to the `Alibaba Cloud OpenSearch Vector Search Edition`.

# ## Setting up
# 
# 
# ### Purchase an instance and configure it
# 
# Purchase OpenSearch Vector Search Edition from [Alibaba Cloud](https://opensearch.console.aliyun.com) and configure the instance according to the help [documentation](https://help.aliyun.com/document_detail/463198.html?spm=a2c4g.465092.0.0.2cd15002hdwavO).
# 
# To run, you should have an [OpenSearch Vector Search Edition](https://opensearch.console.aliyun.com) instance up and running.
# 
#   
# ### Alibaba Cloud OpenSearch Vector Store class
#                                                                                                                 `AlibabaCloudOpenSearch` class supports functions:
# - `add_texts`
# - `add_documents`
# - `from_texts`
# - `from_documents`
# - `similarity_search`
# - `asimilarity_search`
# - `similarity_search_by_vector`
# - `asimilarity_search_by_vector`
# - `similarity_search_with_relevance_scores`
# - `delete_doc_by_texts`
# 
# 
# Read the [help document](https://www.alibabacloud.com/help/en/opensearch/latest/vector-search) to quickly familiarize and configure OpenSearch Vector Search Edition instance.
# 
# If you encounter any problems during use, please feel free to contact xingshaomin.xsm@alibaba-inc.com, and we will do our best to provide you with assistance and support.

# After the instance is up and running, follow these steps to split documents, get embeddings, connect to the alibaba cloud opensearch instance, index documents, and perform vector retrieval.

# We need to install the following Python packages first.

# In[1]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  langchain-community alibabacloud_ha3engine_vector')


# We want to use `OpenAIEmbeddings` so we have to get the OpenAI API Key.

# In[ ]:


import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")


# ## Example

# In[ ]:


from langchain_community.vectorstores import (
    AlibabaCloudOpenSearch,
    AlibabaCloudOpenSearchSettings,
)
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


# Split documents and get embeddings.

# In[ ]:


from langchain_community.document_loaders import TextLoader

loader = TextLoader("../../../state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()


# Create opensearch settings.

# In[ ]:


settings = AlibabaCloudOpenSearchSettings(
    endpoint=" The endpoint of opensearch instance, You can find it from the console of Alibaba Cloud OpenSearch.",
    instance_id="The identify of opensearch instance, You can find it from the console of Alibaba Cloud OpenSearch.",
    protocol="Communication Protocol between SDK and Server, default is http.",
    username="The username specified when purchasing the instance.",
    password="The password specified when purchasing the instance.",
    namespace="The instance data will be partitioned based on the namespace field. If the namespace is enabled, you need to specify the namespace field name during initialization. Otherwise, the queries cannot be executed correctly.",
    tablename="The table name specified during instance configuration.",
    embedding_field_separator="Delimiter specified for writing vector field data, default is comma.",
    output_fields="Specify the field list returned when invoking OpenSearch, by default it is the value list of the field mapping field.",
    field_name_mapping={
        "id": "id",  # The id field name mapping of index document.
        "document": "document",  # The text field name mapping of index document.
        "embedding": "embedding",  # The embedding field name mapping of index document.
        "name_of_the_metadata_specified_during_search": "opensearch_metadata_field_name,=",
        # The metadata field name mapping of index document, could specify multiple, The value field contains mapping name and operator, the operator would be used when executing metadata filter query,
        # Currently supported logical operators are: > (greater than), < (less than), = (equal to), <= (less than or equal to), >= (greater than or equal to), != (not equal to).
        # Refer to this link: https://help.aliyun.com/zh/open-search/vector-search-edition/filter-expression
    },
)

# for example

# settings = AlibabaCloudOpenSearchSettings(
#     endpoint='ha-cn-5yd3fhdm102.public.ha.aliyuncs.com',
#     instance_id='ha-cn-5yd3fhdm102',
#     username='instance user name',
#     password='instance password',
#     table_name='test_table',
#     field_name_mapping={
#         "id": "id",
#         "document": "document",
#         "embedding": "embedding",
#         "string_field": "string_filed,=",
#         "int_field": "int_filed,=",
#         "float_field": "float_field,=",
#         "double_field": "double_field,="
#
#     },
# )


# Create an opensearch access instance by settings.

# In[ ]:


# Create an opensearch instance and index docs.
opensearch = AlibabaCloudOpenSearch.from_texts(
    texts=docs, embedding=embeddings, config=settings
)


# or

# In[ ]:


# Create an opensearch instance.
opensearch = AlibabaCloudOpenSearch(embedding=embeddings, config=settings)


# Add texts and build index.

# In[ ]:


metadatas = [
    {"string_field": "value1", "int_field": 1, "float_field": 1.0, "double_field": 2.0},
    {"string_field": "value2", "int_field": 2, "float_field": 3.0, "double_field": 4.0},
    {"string_field": "value3", "int_field": 3, "float_field": 5.0, "double_field": 6.0},
]
# the key of metadatas must match field_name_mapping in settings.
opensearch.add_texts(texts=docs, ids=[], metadatas=metadatas)


# Query and retrieve data.

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
docs = opensearch.similarity_search(query)
print(docs[0].page_content)


# Query and retrieve data with metadata.
# 

# In[ ]:


query = "What did the president say about Ketanji Brown Jackson"
metadata = {
    "string_field": "value1",
    "int_field": 1,
    "float_field": 1.0,
    "double_field": 2.0,
}
docs = opensearch.similarity_search(query, filter=metadata)
print(docs[0].page_content)


# If you encounter any problems during use, please feel free to contact xingshaomin.xsm@alibaba-inc.com, and we will do our best to provide you with assistance and support.
# 
