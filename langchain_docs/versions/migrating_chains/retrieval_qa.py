#!/usr/bin/env python
# coding: utf-8

# # Migrating from RetrievalQA
#
# The [`RetrievalQA` chain](https://python.langchain.com/api_reference/langchain/chains/langchain.chains.retrieval_qa.base.RetrievalQA.html) performed natural-language question answering over a data source using retrieval-augmented generation.
#
# Some advantages of switching to the LCEL implementation are:
#
# - Easier customizability. Details such as the prompt and how documents are formatted are only configurable via specific parameters in the `RetrievalQA` chain.
# - More easily return source documents.
# - Support for runnable methods like streaming and async operations.
#
# Now let's look at them side-by-side. We'll use the following ingestion code to load a [blog post by Lilian Weng](https://lilianweng.github.io/posts/2023-06-23-agent/) on autonomous agents into a local vector store:
#
# ## Shared setup
#
# For both versions, we'll need to load the data with the `WebBaseLoader` document loader, split it with `RecursiveCharacterTextSplitter`, and add it to an in-memory `FAISS` vector store.
#
# We will also instantiate a chat model to use.

# In[ ]:


get_ipython().run_line_magic(
    "pip",
    "install --upgrade --quiet langchain-community langchain langchain-openai faiss-cpu beautifulsoup4",
)


# In[2]:


import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass()


# In[2]:


# Load docs
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
data = loader.load()

# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Store splits
vectorstore = FAISS.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# LLM
llm = ChatOpenAI()


# ## Legacy
#
# <details open>

# In[4]:


from langchain import hub
from langchain.chains import RetrievalQA

# See full prompt at https://smith.langchain.com/hub/rlm/rag-prompt
prompt = hub.pull("rlm/rag-prompt")

qa_chain = RetrievalQA.from_llm(
    llm, retriever=vectorstore.as_retriever(), prompt=prompt
)

qa_chain("What are autonomous agents?")


# </details>
#
# ## LCEL
#
# <details open>

# In[5]:


from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# See full prompt at https://smith.langchain.com/hub/rlm/rag-prompt
prompt = hub.pull("rlm/rag-prompt")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


qa_chain = (
    {
        "context": vectorstore.as_retriever() | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

qa_chain.invoke("What are autonomous agents?")


# The LCEL implementation exposes the internals of what's happening around retrieving, formatting documents, and passing them through a prompt to the LLM, but it is more verbose. You can customize and wrap this composition logic in a helper function, or use the higher-level [`create_retrieval_chain`](https://python.langchain.com/api_reference/langchain/chains/langchain.chains.retrieval.create_retrieval_chain.html) and [`create_stuff_documents_chain`](https://python.langchain.com/api_reference/langchain/chains/langchain.chains.combine_documents.stuff.create_stuff_documents_chain.html) helper method:

# In[6]:


from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# See full prompt at https://smith.langchain.com/hub/langchain-ai/retrieval-qa-chat
retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
rag_chain = create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)

rag_chain.invoke({"input": "What are autonomous agents?"})


# </details>
#
# ## Next steps
#
# Check out the [LCEL conceptual docs](/docs/concepts/lcel) for more background information on the LangChain expression language.
