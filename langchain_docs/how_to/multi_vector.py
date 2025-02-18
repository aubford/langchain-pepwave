#!/usr/bin/env python
# coding: utf-8

# # How to retrieve using multiple vectors per document
#
# It can often be useful to store multiple [vectors](/docs/concepts/vectorstores/) per document. There are multiple use cases where this is beneficial. For example, we can [embed](/docs/concepts/embedding_models/) multiple chunks of a document and associate those embeddings with the parent document, allowing [retriever](/docs/concepts/retrievers/) hits on the chunks to return the larger document.
#
# LangChain implements a base [MultiVectorRetriever](https://python.langchain.com/api_reference/langchain/retrievers/langchain.retrievers.multi_vector.MultiVectorRetriever.html), which simplifies this process. Much of the complexity lies in how to create the multiple vectors per document. This notebook covers some of the common ways to create those vectors and use the `MultiVectorRetriever`.
#
# The methods to create multiple vectors per document include:
#
# - Smaller chunks: split a document into smaller chunks, and embed those (this is [ParentDocumentRetriever](https://python.langchain.com/api_reference/langchain/retrievers/langchain.retrievers.parent_document_retriever.ParentDocumentRetriever.html)).
# - Summary: create a summary for each document, embed that along with (or instead of) the document.
# - Hypothetical questions: create hypothetical questions that each document would be appropriate to answer, embed those along with (or instead of) the document.
#
# Note that this also enables another method of adding embeddings - manually. This is useful because you can explicitly add questions or queries that should lead to a document being recovered, giving you more control.
#
# Below we walk through an example. First we instantiate some documents. We will index them in an (in-memory) [Chroma](/docs/integrations/providers/chroma/) vector store using [OpenAI](https://python.langchain.com/docs/integrations/text_embedding/openai/) embeddings, but any LangChain vector store or embeddings model will suffice.

# In[ ]:


get_ipython().run_line_magic(
    "pip",
    "install --upgrade --quiet  langchain-chroma langchain langchain-openai > /dev/null",
)


# In[1]:


from langchain.storage import InMemoryByteStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

loaders = [
    TextLoader("paul_graham_essay.txt"),
    TextLoader("state_of_the_union.txt"),
]
docs = []
for loader in loaders:
    docs.extend(loader.load())
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
docs = text_splitter.split_documents(docs)

# The vectorstore to use to index the child chunks
vectorstore = Chroma(
    collection_name="full_documents", embedding_function=OpenAIEmbeddings()
)


# ## Smaller chunks
#
# Often times it can be useful to retrieve larger chunks of information, but embed smaller chunks. This allows for embeddings to capture the semantic meaning as closely as possible, but for as much context as possible to be passed downstream. Note that this is what the [ParentDocumentRetriever](https://python.langchain.com/api_reference/langchain/retrievers/langchain.retrievers.parent_document_retriever.ParentDocumentRetriever.html) does. Here we show what is going on under the hood.
#
# We will make a distinction between the vector store, which indexes embeddings of the (sub) documents, and the document store, which houses the "parent" documents and associates them with an identifier.

# In[2]:


import uuid

from langchain.retrievers.multi_vector import MultiVectorRetriever

# The storage layer for the parent documents
store = InMemoryByteStore()
id_key = "doc_id"

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key,
)

doc_ids = [str(uuid.uuid4()) for _ in docs]


# We next generate the "sub" documents by splitting the original documents. Note that we store the document identifier in the `metadata` of the corresponding [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html) object.

# In[3]:


# The splitter to use to create smaller chunks
child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

sub_docs = []
for i, doc in enumerate(docs):
    _id = doc_ids[i]
    _sub_docs = child_text_splitter.split_documents([doc])
    for _doc in _sub_docs:
        _doc.metadata[id_key] = _id
    sub_docs.extend(_sub_docs)


# Finally, we index the documents in our vector store and document store:

# In[4]:


retriever.vectorstore.add_documents(sub_docs)
retriever.docstore.mset(list(zip(doc_ids, docs)))


# The vector store alone will retrieve small chunks:

# In[5]:


retriever.vectorstore.similarity_search("justice breyer")[0]


# Whereas the retriever will return the larger parent document:

# In[6]:


len(retriever.invoke("justice breyer")[0].page_content)


# The default search type the retriever performs on the vector database is a similarity search. LangChain vector stores also support searching via [Max Marginal Relevance](https://python.langchain.com/api_reference/core/vectorstores/langchain_core.vectorstores.base.VectorStore.html#langchain_core.vectorstores.base.VectorStore.max_marginal_relevance_search). This can be controlled via the `search_type` parameter of the retriever:

# In[7]:


from langchain.retrievers.multi_vector import SearchType

retriever.search_type = SearchType.mmr

len(retriever.invoke("justice breyer")[0].page_content)


# ## Associating summaries with a document for retrieval
#
# A summary may be able to distill more accurately what a chunk is about, leading to better retrieval. Here we show how to create summaries, and then embed those.
#
# We construct a simple [chain](/docs/how_to/sequence) that will receive an input [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html) object and generate a summary using a LLM.
#
# import ChatModelTabs from "@theme/ChatModelTabs";
#
# <ChatModelTabs customVarName="llm" />
#

# In[8]:


# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI()


# In[9]:


import uuid

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

chain = (
    {"doc": lambda x: x.page_content}
    | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
    | llm
    | StrOutputParser()
)


# Note that we can [batch](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.Runnable.html#langchain_core.runnables.base.Runnable) the chain across documents:

# In[10]:


summaries = chain.batch(docs, {"max_concurrency": 5})


# We can then initialize a `MultiVectorRetriever` as before, indexing the summaries in our vector store, and retaining the original documents in our document store:

# In[11]:


# The vectorstore to use to index the child chunks
vectorstore = Chroma(collection_name="summaries", embedding_function=OpenAIEmbeddings())
# The storage layer for the parent documents
store = InMemoryByteStore()
id_key = "doc_id"
# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key,
)
doc_ids = [str(uuid.uuid4()) for _ in docs]

summary_docs = [
    Document(page_content=s, metadata={id_key: doc_ids[i]})
    for i, s in enumerate(summaries)
]

retriever.vectorstore.add_documents(summary_docs)
retriever.docstore.mset(list(zip(doc_ids, docs)))


# In[17]:


# # We can also add the original chunks to the vectorstore if we so want
# for i, doc in enumerate(docs):
#     doc.metadata[id_key] = doc_ids[i]
# retriever.vectorstore.add_documents(docs)


# Querying the vector store will return summaries:

# In[12]:


sub_docs = retriever.vectorstore.similarity_search("justice breyer")

sub_docs[0]


# Whereas the retriever will return the larger source document:

# In[13]:


retrieved_docs = retriever.invoke("justice breyer")

len(retrieved_docs[0].page_content)


# ## Hypothetical Queries
#
# An LLM can also be used to generate a list of hypothetical questions that could be asked of a particular document, which might bear close semantic similarity to relevant queries in a [RAG](/docs/tutorials/rag) application. These questions can then be embedded and associated with the documents to improve retrieval.
#
# Below, we use the [with_structured_output](/docs/how_to/structured_output/) method to structure the LLM output into a list of strings.

# In[16]:


from typing import List

from pydantic import BaseModel, Field


class HypotheticalQuestions(BaseModel):
    """Generate hypothetical questions."""

    questions: List[str] = Field(..., description="List of questions")


chain = (
    {"doc": lambda x: x.page_content}
    # Only asking for 3 hypothetical questions, but this could be adjusted
    | ChatPromptTemplate.from_template(
        "Generate a list of exactly 3 hypothetical questions that the below document could be used to answer:\n\n{doc}"
    )
    | ChatOpenAI(max_retries=0, model="gpt-4o").with_structured_output(
        HypotheticalQuestions
    )
    | (lambda x: x.questions)
)


# Invoking the chain on a single document demonstrates that it outputs a list of questions:

# In[17]:


chain.invoke(docs[0])


# We can batch then batch the chain over all documents and assemble our vector store and document store as before:

# In[18]:


# Batch chain over documents to generate hypothetical questions
hypothetical_questions = chain.batch(docs, {"max_concurrency": 5})


# The vectorstore to use to index the child chunks
vectorstore = Chroma(
    collection_name="hypo-questions", embedding_function=OpenAIEmbeddings()
)
# The storage layer for the parent documents
store = InMemoryByteStore()
id_key = "doc_id"
# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key,
)
doc_ids = [str(uuid.uuid4()) for _ in docs]


# Generate Document objects from hypothetical questions
question_docs = []
for i, question_list in enumerate(hypothetical_questions):
    question_docs.extend(
        [Document(page_content=s, metadata={id_key: doc_ids[i]}) for s in question_list]
    )


retriever.vectorstore.add_documents(question_docs)
retriever.docstore.mset(list(zip(doc_ids, docs)))


# Note that querying the underlying vector store will retrieve hypothetical questions that are semantically similar to the input query:

# In[19]:


sub_docs = retriever.vectorstore.similarity_search("justice breyer")

sub_docs


# And invoking the retriever will return the corresponding document:

# In[20]:


retrieved_docs = retriever.invoke("justice breyer")
len(retrieved_docs[0].page_content)
