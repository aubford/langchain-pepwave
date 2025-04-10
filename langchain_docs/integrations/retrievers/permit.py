#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Permit
---
# # PermitRetriever
# 
# Permit is an access control platform that provides fine-grained, real-time permission management using various models such as RBAC, ABAC, and ReBAC. It enables organizations to enforce dynamic policies across their applications, ensuring that only authorized users can access specific resources.
# 
# ### Integration details
# 
# This notebook illustrates how to integrate [Permit.io](https://permit.io/) permissions into LangChain retrievers.
# 
# We provide two custom retrievers:
# 
# - PermitSelfQueryRetriever – Uses a self-query approach to parse the user’s natural-language prompt, fetch the user’s permitted resource IDs from Permit, and apply that filter automatically in a vector store search. 
#  
# - PermitEnsembleRetriever – Combines multiple underlying retrievers (e.g., BM25 + Vector) via LangChain’s EnsembleRetriever, then filters the merged results with Permit.io.
# 
# ## Setup
# 
# Install the package with the command:
# 
# ```bash
# pip install langchain-permit
# ```

# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# ```bash
# pip install langchain-permit
# ```
# 
# #### Environment Variables
# 
# ```bash
# PERMIT_API_KEY=your_api_key
# PERMIT_PDP_URL= # or your real deployment
# OPENAI_API_KEY=sk-...
# ```
# - A running Permit PDP. See [Permit docs](https://docs.permit.io/) for details on setting up your policy and container.
# - A vector store or multiple retrievers that we can wrap.

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-permit')


# ## Instantiation
# 
# ### PermitSelfQueryRetriever
# 
# #### Basic Explanation
# 
# 1. Retrieves permitted document IDs from Permit.  
# 
# 2. Uses an LLM to parse your query and build a “structured filter,” ensuring only docs with those permitted IDs are considered.
# 
# #### Basic Usage
# 
# ```python
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_permit.retrievers import PermitSelfQueryRetriever
# 
# # Step 1: Create / load some documents and build a vector store
# docs = [...]
# embeddings = OpenAIEmbeddings()
# vectorstore = FAISS.from_documents(docs, embeddings)
# 
# # Step 2: Initialize the retriever
# retriever = PermitSelfQueryRetriever(
#     api_key="...",
#     pdp_url="...",
#     user={"key": "user-123"},
#     resource_type="document",
#     action="read",
#     llm=...,                # Typically a ChatOpenAI or other LLM
#     vectorstore=vectorstore,
#     enable_limit=True,      # optional
# )
# 
# # Step 3: Query
# query = "Give me docs about cats"
# results = retriever.get_relevant_documents(query)
# for doc in results:
#     print(doc.metadata.get("id"), doc.page_content)
# ```
# 
# ### PermitEnsembleRetriever
# 
# #### Basic Explanation
# 
# 1. Uses LangChain’s EnsembleRetriever to gather documents from multiple sub-retrievers (e.g., vector-based, BM25, etc.).
# 2. After retrieving documents, it calls filter_objects on Permit to eliminate any docs the user isn’t allowed to see.
# 
# #### Basic Usage
# 
# ```python
# from langchain_community.retrievers import BM25Retriever
# from langchain_core.documents import Document
# from langchain_permit.retrievers import PermitEnsembleRetriever
# 
# # Suppose we have two child retrievers: bm25_retriever, vector_retriever
# ...
# ensemble_retriever = PermitEnsembleRetriever(
#     api_key="...",
#     pdp_url="...",
#     user="user_abc",
#     action="read",
#     resource_type="document",
#     retrievers=[bm25_retriever, vector_retriever],
#     weights=None
# )
# 
# docs = ensemble_retriever.get_relevant_documents("Query about cats")
# for doc in docs:
#     print(doc.metadata.get("id"), doc.page_content)
# ```
# 
# ### Demo Scripts
# 
# For more complete demos, check out the `/langchain_permit/examples/demo_scripts` folder:
# 
# 1. demo_self_query.py – Demonstrates PermitSelfQueryRetriever.
# 2. demo_ensemble.py – Demonstrates PermitEnsembleRetriever.
# 
# Each script shows how to build or load documents, configure Permit, and run queries.
# 
# ### Conclusion
# 
# With these custom retrievers, you can seamlessly integrate Permit.io’s permission checks into LangChain’s retrieval workflow. You can keep your application’s vector search logic while ensuring only authorized documents are returned.
# 
# For more details on setting up Permit policies, see the official Permit docs. If you want to combine these with other tools (like JWT validation or a broader RAG pipeline), check out our docs/tools.ipynb in the examples folder.

# In[ ]:


from langchain_permit import PermitRetriever

retriever = PermitRetriever(
    # ...
)


# ## Usage

# 

# In[ ]:


query = "..."

retriever.invoke(query)


# ## Use within a chain
# 
# Like other retrievers, PermitRetriever can be incorporated into LLM applications via [chains](https://docs.permit.io/).
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
# For detailed documentation of all PermitRetriever features and configurations head to the [Repo](https://github.com/permitio/langchain-permit/tree/master/langchain_permit/examples/demo_scripts).
