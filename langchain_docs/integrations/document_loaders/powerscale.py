#!/usr/bin/env python
# coding: utf-8

# # Dell PowerScale Document Loader
# 
# [Dell PowerScale](https://www.dell.com/en-us/shop/powerscale-family/sf/powerscale) is an enterprise scale out storage system that hosts industry leading OneFS filesystem that can be hosted on-prem or deployed in the cloud.
# 
# This document loader utilizes unique capabilities from PowerScale that can determine what files that have been modified since an application's last run and only returns modified files for processing. This will eliminate the need to re-process (chunk and embed) files that have not been changed, improving the overall data ingestion workflow.
# 
# This loader requires PowerScale's MetadataIQ feature enabled. Additional information can be found on our GitHub Repo: [https://github.com/dell/powerscale-rag-connector](https://github.com/dell/powerscale-rag-connector)
# 
# ## Overview
# ### Integration details
# 
# | Class | Package | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/document_loaders/web_loaders/__module_name___loader)|
# | :--- | :--- | :---: | :---: |  :---: |
# | [PowerScaleDocumentLoader](https://github.com/dell/powerscale-rag-connector/blob/main/src/powerscale_rag_connector/PowerScaleDocumentLoader.py) | [powerscale-rag-connector](https://github.com/dell/powerscale-rag-connector) | ✅ | ❌ | ❌ | 
# | [PowerScaleUnstructuredLoader](https://github.com/dell/powerscale-rag-connector/blob/main/src/powerscale_rag_connector/PowerScaleUnstructuredLoader.py) | [powerscale-rag-connector](https://github.com/dell/powerscale-rag-connector) | ✅ | ❌ | ❌ | 
# ### Loader features
# | Source | Document Lazy Loading | Native Async Support
# | :---: | :---: | :---: | 
# | PowerScaleDocumentLoader | ✅ | ✅ | 
# | PowerScaleUnstructuredLoader | ✅ | ✅ | 
# 
# ## Setup
# 
# This document loader requires the use of a Dell PowerScale system with MetadataIQ enabled. Additional information can be found on our github page: [https://github.com/dell/powerscale-rag-connector](https://github.com/dell/powerscale-rag-connector)
# 
# 

# ### Installation
# 
# The document loader lives in an external pip package and can be installed using standard tooling

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  powerscale-rag-connector')


# ## Initialization
# 
# Now we can instantiate document loader:

# ### Generic Document Loader
# 
# Our generic document loader can be used to incrementally load all files from PowerScale in the following manner:

# In[ ]:


from powerscale_rag_connector import PowerScaleDocumentLoader

loader = PowerScaleDocumentLoader(
    es_host_url="http://elasticsearch:9200",
    es_index_name="metadataiq",
    es_api_key="your-api-key",
    folder_path="/ifs/data",
)


# ### UnstructuredLoader Loader
# 
# Optionally, the `PowerScaleUnstructuredLoader` can be used to locate the changed files _and_ automatically process the files producing elements of the source file. This is done using LangChain's `UnstructuredLoader` class.

# In[ ]:


from powerscale_rag_connector import PowerScaleUnstructuredLoader

# Or load files with the Unstructured Loader
loader = PowerScaleUnstructuredLoader(
    es_host_url="http://elasticsearch:9200",
    es_index_name="metadataiq",
    es_api_key="your-api-key",
    folder_path="/ifs/data",
    # 'elements' mode splits the document into more granular chunks
    # Use 'single' mode if you want the entire document as a single chunk
    mode="elements",
)


# The fields:
#  - `es_host_url` is the endpoint to to MetadataIQ Elasticsearch database
#  - `es_index_index` is the name of the index where PowerScale writes it file system metadata
#  - `es_api_key` is the **encoded** version of your elasticsearch API key
#  - `folder_path` is the path on PowerScale to be queried for changes

# ## Load
# 
# Internally, all code is asynchronous with PowerScale and MetadataIQ and the load and lazy load methods will return a python generator. We recommend using the lazy load function.

# In[ ]:


for doc in loader.load():
    print(doc)


# ### Returned Object
# 
# Both document loaders will keep track of what files were previously returned to your application. When called again, the document loader will only return new or modified files since your previous run.
# 
#  - The `metadata` fields in the returned `Document` will return the path on PowerScale that contains the modified file. You will use this path to read the data via NFS (or S3) and process the data in your application (e.g.: create chunks and embedding). 
#  - The `source` field is the path on PowerScale and not necessarily on your local system (depending on your mount strategy); OneFS expresses the entire storage system as a single tree rooted at `/ifs`.
#  - The `change_types` property will inform you on what change occurred since the last one - e.g.: new, modified or delete.
# 
# Your RAG application can use the information from `change_types` to add, update or delete entries your chunk and vector store.
# 
# When using `PowerScaleUnstructuredLoader` the `page_content` field will be filled with data from the Unstructured Loader

# ## Lazy Load
# 
# Internally, all code is asynchronous with PowerScale and MetadataIQ and the load and lazy load methods will return a python generator. We recommend using the lazy load function.

# In[ ]:


for doc in loader.lazy_load():
    print(doc)  # do something specific with the document


# The same `Document` is returned as the load function with all the same properties mentioned above.

# ## Additional Examples
# 
# Additional examples and code can be found on our public github webpage: [https://github.com/dell/powerscale-rag-connector/tree/main/examples](https://github.com/dell/powerscale-rag-connector/tree/main/examples) that provide full working examples. 
# 
#  - [PowerScale LangChain Document Loader](https://github.com/dell/powerscale-rag-connector/blob/main/examples/powerscale_langchain_doc_loader.py) - Working example of our standard document loader
#  - [PowerScale LangChain Unstructured Loader](https://github.com/dell/powerscale-rag-connector/blob/main/examples/powerscale_langchain_unstructured_loader.py) - Working example of our standard document loader using unstructured loader for chunking and embedding
#  - [PowerScale NVIDIA Retriever Microservice Loader](https://github.com/dell/powerscale-rag-connector/blob/main/examples/powerscale_nvingest_example.py) - Working example of our document loader with NVIDIA NeMo Retriever microservices for chunking and embedding

# ## API reference
# 
# For detailed documentation of all PowerScale Document Loader features and configurations head to the github page: [https://github.com/dell/powerscale-rag-connector/](https://github.com/dell/powerscale-rag-connector/)
