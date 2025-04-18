#!/usr/bin/env python
# coding: utf-8
---
sidebar_position: 6
---
# # How to construct filters for query analysis
# 
# We may want to do query analysis to extract filters to pass into retrievers. One way we ask the LLM to represent these filters is as a Pydantic model. There is then the issue of converting that Pydantic model into a filter that can be passed into a retriever. 
# 
# This can be done manually, but LangChain also provides some "Translators" that are able to translate from a common syntax into filters specific to each retriever. Here, we will cover how to use those translators.

# In[1]:


from typing import Optional

from langchain.chains.query_constructor.ir import (
    Comparator,
    Comparison,
    Operation,
    Operator,
    StructuredQuery,
)
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain_community.query_constructors.elasticsearch import ElasticsearchTranslator
from pydantic import BaseModel


# In this example, `year` and `author` are both attributes to filter on.

# In[2]:


class Search(BaseModel):
    query: str
    start_year: Optional[int]
    author: Optional[str]


# In[3]:


search_query = Search(query="RAG", start_year=2022, author="LangChain")


# In[4]:


def construct_comparisons(query: Search):
    comparisons = []
    if query.start_year is not None:
        comparisons.append(
            Comparison(
                comparator=Comparator.GT,
                attribute="start_year",
                value=query.start_year,
            )
        )
    if query.author is not None:
        comparisons.append(
            Comparison(
                comparator=Comparator.EQ,
                attribute="author",
                value=query.author,
            )
        )
    return comparisons


# In[5]:


comparisons = construct_comparisons(search_query)


# In[6]:


_filter = Operation(operator=Operator.AND, arguments=comparisons)


# In[7]:


ElasticsearchTranslator().visit_operation(_filter)


# In[8]:


ChromaTranslator().visit_operation(_filter)

