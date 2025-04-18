#!/usr/bin/env python
# coding: utf-8
---
sidebar_label: Cognee
---
# # CogneeRetriever
# 
# This will help you getting started with the Cognee [retriever](/docs/concepts/retrievers). For detailed documentation of all CogneeRetriever features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.cognee.CogneeRetriever.html).
# 
# ### Integration details
# 
# Bring-your-own data (i.e., index and search a custom corpus of documents):
# 
# | Retriever | Self-host | Cloud offering | Package |
# | :--- | :--- | :---: | :---: |
# [CogneeRetriever](https://python.langchain.com/api_reference/community/retrievers/langchain_community.retrievers.cognee.CogneeRetriever.html) | ✅ | ❌ | langchain-cognee |
# 
# ## Setup
# 
# For cognee default setup, only thing you need is your OpenAI API key. 
# 

# If you want to get automated tracing from individual queries, you can also set your [LangSmith](https://docs.smith.langchain.com/) API key by uncommenting below:

# In[ ]:


# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
# os.environ["LANGSMITH_TRACING"] = "true"


# ### Installation
# 
# This retriever lives in the `langchain-cognee` package:

# In[ ]:


get_ipython().run_line_magic('pip', 'install -qU langchain-cognee')


# In[ ]:


import nest_asyncio

nest_asyncio.apply()


# ## Instantiation
# 
# Now we can instantiate our retriever:

# In[ ]:


from langchain_cognee import CogneeRetriever

retriever = CogneeRetriever(
    llm_api_key="sk-",  # OpenAI API Key
    dataset_name="my_dataset",
    k=3,
)


# ## Usage
# 
# Add some documents, process them, and then run queries. Cognee retrieves relevant knowledge to your queries and generates final answers.

# In[ ]:


# Example of adding and processing documents
from langchain_core.documents import Document

docs = [
    Document(page_content="Elon Musk is the CEO of SpaceX."),
    Document(page_content="SpaceX focuses on rockets and space travel."),
]

retriever.add_documents(docs)
retriever.process_data()

# Now let's query the retriever
query = "Tell me about Elon Musk"
results = retriever.invoke(query)

for idx, doc in enumerate(results, start=1):
    print(f"Doc {idx}: {doc.page_content}")


# ## Use within a chain
# 
# Like other retrievers, CogneeRetriever can be incorporated into LLM applications via [chains](/docs/how_to/sequence/).
# 
# We will need a LLM or chat model:
# 
# import ChatModelTabs from "@theme/ChatModelTabs";
# 
# <ChatModelTabs customVarName="llm" />

# In[ ]:


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# In[ ]:


from langchain_cognee import CogneeRetriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Instantiate the retriever with your Cognee config
retriever = CogneeRetriever(llm_api_key="sk-", dataset_name="my_dataset", k=3)

# Optionally, prune/reset the dataset for a clean slate
retriever.prune()

# Add some documents
docs = [
    Document(page_content="Elon Musk is the CEO of SpaceX."),
    Document(page_content="SpaceX focuses on space travel."),
]
retriever.add_documents(docs)
retriever.process_data()


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


answer = chain.invoke("What companies do Elon Musk own?")

print("\nFinal chain answer:\n", answer)


# ## API reference
# 
# TODO: add link to API reference.

# 
