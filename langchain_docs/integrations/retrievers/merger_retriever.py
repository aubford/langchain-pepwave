#!/usr/bin/env python
# coding: utf-8

# # LOTR (Merger Retriever)
# 
# >`Lord of the Retrievers (LOTR)`, also known as `MergerRetriever`, takes a list of retrievers as input and merges the results of their get_relevant_documents() methods into a single list. The merged results will be a list of documents that are relevant to the query and that have been ranked by the different retrievers.
# 
# The `MergerRetriever` class can be used to improve the accuracy of document retrieval in a number of ways. First, it can combine the results of multiple retrievers, which can help to reduce the risk of bias in the results. Second, it can rank the results of the different retrievers, which can help to ensure that the most relevant documents are returned first.

# In[ ]:


import os

import chromadb
from langchain.retrievers import (
    ContextualCompressionRetriever,
    DocumentCompressorPipeline,
    MergerRetriever,
)
from langchain_chroma import Chroma
from langchain_community.document_transformers import (
    EmbeddingsClusteringFilter,
    EmbeddingsRedundantFilter,
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

# Get 3 diff embeddings.
all_mini = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
multi_qa_mini = HuggingFaceEmbeddings(model_name="multi-qa-MiniLM-L6-dot-v1")
filter_embeddings = OpenAIEmbeddings()

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "db")

# Instantiate 2 diff chromadb indexes, each one with a diff embedding.
client_settings = chromadb.config.Settings(
    is_persistent=True,
    persist_directory=DB_DIR,
    anonymized_telemetry=False,
)
db_all = Chroma(
    collection_name="project_store_all",
    persist_directory=DB_DIR,
    client_settings=client_settings,
    embedding_function=all_mini,
)
db_multi_qa = Chroma(
    collection_name="project_store_multi",
    persist_directory=DB_DIR,
    client_settings=client_settings,
    embedding_function=multi_qa_mini,
)

# Define 2 diff retrievers with 2 diff embeddings and diff search type.
retriever_all = db_all.as_retriever(
    search_type="similarity", search_kwargs={"k": 5, "include_metadata": True}
)
retriever_multi_qa = db_multi_qa.as_retriever(
    search_type="mmr", search_kwargs={"k": 5, "include_metadata": True}
)

# The Lord of the Retrievers will hold the output of both retrievers and can be used as any other
# retriever on different types of chains.
lotr = MergerRetriever(retrievers=[retriever_all, retriever_multi_qa])


# ## Remove redundant results from the merged retrievers.

# In[ ]:


# We can remove redundant results from both retrievers using yet another embedding.
# Using multiples embeddings in diff steps could help reduce biases.
filter = EmbeddingsRedundantFilter(embeddings=filter_embeddings)
pipeline = DocumentCompressorPipeline(transformers=[filter])
compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline, base_retriever=lotr
)


# ## Pick a representative sample of documents from the merged retrievers.

# In[ ]:


# This filter will divide the documents vectors into clusters or "centers" of meaning.
# Then it will pick the closest document to that center for the final results.
# By default the result document will be ordered/grouped by clusters.
filter_ordered_cluster = EmbeddingsClusteringFilter(
    embeddings=filter_embeddings,
    num_clusters=10,
    num_closest=1,
)

# If you want the final document to be ordered by the original retriever scores
# you need to add the "sorted" parameter.
filter_ordered_by_retriever = EmbeddingsClusteringFilter(
    embeddings=filter_embeddings,
    num_clusters=10,
    num_closest=1,
    sorted=True,
)

pipeline = DocumentCompressorPipeline(transformers=[filter_ordered_by_retriever])
compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline, base_retriever=lotr
)


# ## Re-order results to avoid performance degradation.
# No matter the architecture of your model, there is a substantial performance degradation when you include 10+ retrieved documents.
# In brief: When models must access relevant information  in the middle of long contexts, then tend to ignore the provided documents.
# See: https://arxiv.org/abs//2307.03172

# In[ ]:


# You can use an additional document transformer to reorder documents after removing redundancy.
from langchain_community.document_transformers import LongContextReorder

filter = EmbeddingsRedundantFilter(embeddings=filter_embeddings)
reordering = LongContextReorder()
pipeline = DocumentCompressorPipeline(transformers=[filter, reordering])
compression_retriever_reordered = ContextualCompressionRetriever(
    base_compressor=pipeline, base_retriever=lotr
)

