#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Azure AI Search
---
# # AzureAISearchRetriever
# 
# [Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search) (formerly known as `Azure Cognitive Search`) is a Microsoft cloud search service that gives developers infrastructure, APIs, and tools for information retrieval of vector, keyword, and hybrid queries at scale.
# 
# `AzureAISearchRetriever` is an integration module that returns documents from an unstructured query. It's based on the BaseRetriever class and it targets the 2023-11-01 stable REST API version of Azure AI Search, which means it supports vector indexing and queries.
# 
# This guide will help you getting started with the Azure AI Search [retriever](/docs/concepts/retrievers). For detailed documentation of all `AzureAISearchRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.azure_ai_search.AzureAISearchRetriever.html).
# 
# `AzureAISearchRetriever` replaces `AzureCognitiveSearchRetriever`, which will soon be deprecated. We recommend switching to the newer version that's based on the most recent stable version of the search APIs.
# 
# ### Integration details
# 
# import {ItemTable} from "@theme/FeatureTables";
# 
# <ItemTable category="document_retrievers" item="AzureAISearchRetriever" />
# 
# 
# ## Setup
# 
# To use this module, you need:
# 
# + An Azure AI Search service. You can [create one](https://learn.microsoft.com/azure/search/search-create-service-portal) for free if you sign up for the Azure trial. A free service has lower quotas, but it's sufficient for running the code in this notebook.
# 
# + An existing index with vector fields. There are several ways to create one, including using the [vector store module](../vectorstores/azuresearch.ipynb). Or, [try the Azure AI Search REST APIs](https://learn.microsoft.com/azure/search/search-get-started-vector).
# 
# + An API key. API keys are generated when you create the search service. If you're just querying an index, you can use the query API key, otherwise use an admin API key. See [Find your API keys](https://learn.microsoft.com/azure/search/search-security-api-keys?tabs=rest-use%2Cportal-find%2Cportal-query#find-existing-keys) for details.
# 
# We can then set the search service name, index name, and API key as environment variables (alternatively, you can pass them as arguments to `AzureAISearchRetriever`). The search index provides the searchable content.

# In[ ]:


import os

os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = "<YOUR_SEARCH_SERVICE_NAME>"
os.environ["AZURE_AI_SEARCH_INDEX_NAME"] = "<YOUR_SEARCH_INDEX_NAME>"
os.environ["AZURE_AI_SEARCH_API_KEY"] = "<YOUR_API_KEY>"


# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This retriever lives in the `langchain-community` package. We will need some additional dependencies as well:

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-community')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet langchain-openai')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  azure-search-documents>=11.4')
get_ipython().run_line_magic('pip', 'install --upgrade --quiet  azure-identity')


# ## Instantiation
# 
# For `AzureAISearchRetriever`, provide an `index_name`, `content_key`, and `top_k` set to the number of number of results you'd like to retrieve. Setting `top_k` to zero (the default) returns all results.

# In[ ]:


from langchain_community.retrievers import AzureAISearchRetriever

retriever = AzureAISearchRetriever(
    content_key="content", top_k=1, index_name="langchain-vector-demo"
)


# ## Usage
# 
# Now you can use it to retrieve documents from Azure AI Search. 
# This is the method you would call to do so. It will return all documents relevant to the query. 

# In[ ]:


retriever.invoke("here is my unstructured query string")


# ## Example 
# 
# This section demonstrates using the retriever over built-in sample data. You can skip this step if you already have a vector index on your search service.
# 
# Start by providing the endpoints and keys. Since we're creating a vector index in this step, specify a text embedding model to get a vector representation of the text. This example assumes Azure OpenAI with a deployment of text-embedding-ada-002. Because this step creates an index, be sure to use an admin API key for your search service.

# In[ ]:


import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_text_splitters import TokenTextSplitter

os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = "<YOUR_SEARCH_SERVICE_NAME>"
os.environ["AZURE_AI_SEARCH_INDEX_NAME"] = "langchain-vector-demo"
os.environ["AZURE_AI_SEARCH_API_KEY"] = "<YOUR_SEARCH_SERVICE_ADMIN_API_KEY>"
azure_endpoint: str = "<YOUR_AZURE_OPENAI_ENDPOINT>"
azure_openai_api_key: str = "<YOUR_AZURE_OPENAI_API_KEY>"
azure_openai_api_version: str = "2023-05-15"
azure_deployment: str = "text-embedding-ada-002"


# We'll use an embedding model from Azure OpenAI to turn our documents into embeddings stored in the Azure AI Search vector store. We'll also set the index name to `langchain-vector-demo`. This will create a new vector store associated with that index name. 

# In[ ]:


embeddings = AzureOpenAIEmbeddings(
    model=azure_deployment,
    azure_endpoint=azure_endpoint,
    openai_api_key=azure_openai_api_key,
)

vector_store: AzureSearch = AzureSearch(
    embedding_function=embeddings.embed_query,
    azure_search_endpoint=os.getenv("AZURE_AI_SEARCH_SERVICE_NAME"),
    azure_search_key=os.getenv("AZURE_AI_SEARCH_API_KEY"),
    index_name="langchain-vector-demo",
)


# Next, we'll load data into our newly created vector store. For this example, we load the `state_of_the_union.txt` file. We'll split the text in 400 token chunks with no overlap. Finally, the documents are added to our vector store as emeddings.

# In[ ]:


from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("../../how_to/state_of_the_union.txt", encoding="utf-8")

documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

vector_store.add_documents(documents=docs)


# Next, we'll create a retriever. The current `index_name` variable is `langchain-vector-demo` from the last step. If you skipped vector store creation, provide your index name in the parameter. In this query, the top result is returned.

# In[21]:


retriever = AzureAISearchRetriever(
    content_key="content", top_k=1, index_name="langchain-vector-demo"
)


# Now we can retrieve the data that is relevant to our query from the documents we uploaded. 

# In[ ]:


retriever.invoke("does the president have a plan for covid-19?")


# ## Use within a chain

# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided.

Context: {context}

Question: {question}"""
)

llm = ChatOpenAI(model="gpt-4o-mini")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# In[ ]:


chain.invoke("does the president have a plan for covid-19?")


# ## API reference
# 
# For detailed documentation of all `AzureAISearchRetriever` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.azure_ai_search.AzureAISearchRetriever.html).
