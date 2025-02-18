#!/usr/bin/env python
# coding: utf-8

# # DashScope Reranker
#
# This notebook shows how to use DashScope Reranker for document compression and retrieval. [DashScope](https://dashscope.aliyun.com/) is the generative AI service from Alibaba Cloud (Aliyun).
#
# DashScope's [Text ReRank Model](https://help.aliyun.com/document_detail/2780058.html?spm=a2c4g.2780059.0.0.6d995024FlrJ12) supports reranking documents with a maximum of 4000 tokens. Moreover, it supports Chinese, English, Japanese, Korean, Thai, Spanish, French, Portuguese, Indonesian, Arabic, and over 50 other languages. For more details, please visit [here](https://help.aliyun.com/document_detail/2780059.html?spm=a2c4g.2780058.0.0.3a9e5b1dWeOQjI).

# In[ ]:


get_ipython().run_line_magic("pip", "install --upgrade --quiet  dashscope")


# In[ ]:


get_ipython().run_line_magic("pip", "install --upgrade --quiet  faiss")

# OR  (depending on Python version)

get_ipython().run_line_magic("pip", "install --upgrade --quiet  faiss-cpu")


# In[ ]:


# To create api key: https://bailian.console.aliyun.com/?apiKey=1#/api-key

import getpass
import os

if "DASHSCOPE_API_KEY" not in os.environ:
    os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("DashScope API Key:")


# In[6]:


# Helper function for printing docs
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


# ## Set up the base vector store retriever
# Let's start by initializing a simple vector store retriever and storing the 2023 State of the Union speech (in chunks). We can set up the retriever to retrieve a high number (20) of docs.

# In[7]:


from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = TextLoader("../../how_to/state_of_the_union.txt").load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)
retriever = FAISS.from_documents(texts, DashScopeEmbeddings()).as_retriever(  # type: ignore
    search_kwargs={"k": 20}
)

query = "What did the president say about Ketanji Brown Jackson"
docs = retriever.invoke(query)
pretty_print_docs(docs)


# ## Reranking with DashScopeRerank
# Now let's wrap our base retriever with a `ContextualCompressionRetriever`. We'll use the `DashScopeRerank` to rerank the returned results.

# In[8]:


from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.dashscope_rerank import DashScopeRerank

compressor = DashScopeRerank()
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

compressed_docs = compression_retriever.invoke(
    "What did the president say about Ketanji Jackson Brown"
)
pretty_print_docs(compressed_docs)


# In[ ]:
