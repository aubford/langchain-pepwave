#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Vectorize
---
# # VectorizeRetriever
# 
# This notebook shows how to use the LangChain Vectorize retriever.
# 
# > [Vectorize](https://vectorize.io/) helps you build AI apps faster and with less hassle.
# > It automates data extraction, finds the best vectorization strategy using RAG evaluation,
# > and lets you quickly deploy real-time RAG pipelines for your unstructured data.
# > Your vector search indexes stay up-to-date, and it integrates with your existing vector database,
# > so you maintain full control of your data.
# > Vectorize handles the heavy lifting, freeing you to focus on building robust AI solutions without getting bogged down by data management.
# 

# ## Setup
# 
# In the following steps, we'll setup the Vectorize environment and create a RAG pipeline.
# 

# ### Create a Vectorize Account & Get Your Access Token
# 
# Sign up for a free Vectorize account [here](https://platform.vectorize.io/)
# Generate an access token in the [Access Token](https://docs.vectorize.io/rag-pipelines/retrieval-endpoint#access-tokens) section
# Gather your organization ID. From the browser url, extract the UUID from the URL after /organization/

# ### Configure token and organization ID
# 
# 

# In[ ]:


import getpass

VECTORIZE_ORG_ID = getpass.getpass("Enter Vectorize organization ID: ")
VECTORIZE_API_TOKEN = getpass.getpass("Enter Vectorize API Token: ")


# ### Installation
# 
# This retriever lives in the `langchain-vectorize` package:

# In[ ]:


get_ipython().system('pip install -qU langchain-vectorize')


# ### Download a PDF file

# In[ ]:


get_ipython().system('wget "https://raw.githubusercontent.com/vectorize-io/vectorize-clients/refs/tags/python-0.1.3/tests/python/tests/research.pdf"')


# ### Initialize the vectorize client

# In[ ]:


import vectorize_client as v

api = v.ApiClient(v.Configuration(access_token=VECTORIZE_API_TOKEN))


# ### Create a File Upload Source Connector

# In[ ]:


import json
import os

import urllib3

connectors_api = v.ConnectorsApi(api)
response = connectors_api.create_source_connector(
    VECTORIZE_ORG_ID, [{"type": "FILE_UPLOAD", "name": "From API"}]
)
source_connector_id = response.connectors[0].id


# ### Upload the PDF file

# In[ ]:


file_path = "research.pdf"

http = urllib3.PoolManager()
uploads_api = v.UploadsApi(api)
metadata = {"created-from-api": True}

upload_response = uploads_api.start_file_upload_to_connector(
    VECTORIZE_ORG_ID,
    source_connector_id,
    v.StartFileUploadToConnectorRequest(
        name=file_path.split("/")[-1],
        content_type="application/pdf",
        # add additional metadata that will be stored along with each chunk in the vector database
        metadata=json.dumps(metadata),
    ),
)

with open(file_path, "rb") as f:
    response = http.request(
        "PUT",
        upload_response.upload_url,
        body=f,
        headers={
            "Content-Type": "application/pdf",
            "Content-Length": str(os.path.getsize(file_path)),
        },
    )

if response.status != 200:
    print("Upload failed: ", response.data)
else:
    print("Upload successful")


# ### Connect to the AI Platform and Vector Database

# In[ ]:


ai_platforms = connectors_api.get_ai_platform_connectors(VECTORIZE_ORG_ID)
builtin_ai_platform = [
    c.id for c in ai_platforms.ai_platform_connectors if c.type == "VECTORIZE"
][0]

vector_databases = connectors_api.get_destination_connectors(VECTORIZE_ORG_ID)
builtin_vector_db = [
    c.id for c in vector_databases.destination_connectors if c.type == "VECTORIZE"
][0]


# ### Configure and Deploy the Pipeline

# In[ ]:


pipelines = v.PipelinesApi(api)
response = pipelines.create_pipeline(
    VECTORIZE_ORG_ID,
    v.PipelineConfigurationSchema(
        source_connectors=[
            v.SourceConnectorSchema(
                id=source_connector_id, type="FILE_UPLOAD", config={}
            )
        ],
        destination_connector=v.DestinationConnectorSchema(
            id=builtin_vector_db, type="VECTORIZE", config={}
        ),
        ai_platform=v.AIPlatformSchema(
            id=builtin_ai_platform, type="VECTORIZE", config={}
        ),
        pipeline_name="My Pipeline From API",
        schedule=v.ScheduleSchema(type="manual"),
    ),
)
pipeline_id = response.data.id


# ### Configure tracing (optional)
# 
# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ## Instantiation

# In[ ]:


from langchain_vectorize.retrievers import VectorizeRetriever

retriever = VectorizeRetriever(
    api_token=VECTORIZE_API_TOKEN,
    organization=VECTORIZE_ORG_ID,
    pipeline_id=pipeline_id,
)


# ## Usage
# 
# 

# In[ ]:


query = "Apple Shareholders equity"
retriever.invoke(query, num_results=2)


# ## Use within a chain
# 
# Like other retrievers, VectorizeRetriever can be incorporated into LLM applications via [chains](/docs/how_to/sequence/).
# 
# We will need a LLM or chat model:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />

# In[ ]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


# In[ ]:


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the context provided.

Context: {context}

Question: {question}"""
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# In[ ]:


chain.invoke("...")


# ## API reference
# 
# For detailed documentation of all VectorizeRetriever features and configurations head to the [API reference](https://python.langchain.com/api_reference/vectorize/langchain_vectorize.retrievers.VectorizeRetriever.html).
