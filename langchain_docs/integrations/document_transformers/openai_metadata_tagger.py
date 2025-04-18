#!/usr/bin/env python
# coding: utf-8

# # OpenAI metadata tagger
# 
# It can often be useful to tag ingested documents with structured metadata, such as the title, tone, or length of a document, to allow for a more targeted similarity search later. However, for large numbers of documents, performing this labelling process manually can be tedious.
# 
# The `OpenAIMetadataTagger` document transformer automates this process by extracting metadata from each provided document according to a provided schema. It uses a configurable `OpenAI Functions`-powered chain under the hood, so if you pass a custom LLM instance, it must be an `OpenAI` model with functions support. 
# 
# **Note:** This document transformer works best with complete documents, so it's best to run it first with whole documents before doing any other splitting or processing!
# 
# For example, let's say you wanted to index a set of movie reviews. You could initialize the document transformer with a valid `JSON Schema` object as follows:

# In[1]:


from langchain_community.document_transformers.openai_functions import (
    create_metadata_tagger,
)
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI


# In[2]:


schema = {
    "properties": {
        "movie_title": {"type": "string"},
        "critic": {"type": "string"},
        "tone": {"type": "string", "enum": ["positive", "negative"]},
        "rating": {
            "type": "integer",
            "description": "The number of stars the critic rated the movie",
        },
    },
    "required": ["movie_title", "critic", "tone"],
}

# Must be an OpenAI model that supports functions
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm)


# You can then simply pass the document transformer a list of documents, and it will extract metadata from the contents:

# In[3]:


original_documents = [
    Document(
        page_content="Review of The Bee Movie\nBy Roger Ebert\n\nThis is the greatest movie ever made. 4 out of 5 stars."
    ),
    Document(
        page_content="Review of The Godfather\nBy Anonymous\n\nThis movie was super boring. 1 out of 5 stars.",
        metadata={"reliable": False},
    ),
]

enhanced_documents = document_transformer.transform_documents(original_documents)


# In[4]:


import json

print(
    *[d.page_content + "\n\n" + json.dumps(d.metadata) for d in enhanced_documents],
    sep="\n\n---------------\n\n",
)


# The new documents can then be further processed by a text splitter before being loaded into a vector store. Extracted fields will not overwrite existing metadata.
# 
# You can also initialize the document transformer with a Pydantic schema:

# In[5]:


from typing import Literal

from pydantic import BaseModel, Field


class Properties(BaseModel):
    movie_title: str
    critic: str
    tone: Literal["positive", "negative"]
    rating: int = Field(description="Rating out of 5 stars")


document_transformer = create_metadata_tagger(Properties, llm)
enhanced_documents = document_transformer.transform_documents(original_documents)

print(
    *[d.page_content + "\n\n" + json.dumps(d.metadata) for d in enhanced_documents],
    sep="\n\n---------------\n\n",
)


# 
# 
# ## Customization
# 
# You can pass the underlying tagging chain the standard LLMChain arguments in the document transformer constructor. For example, if you wanted to ask the LLM to focus specific details in the input documents, or extract metadata in a certain style, you could pass in a custom prompt:

# In[6]:


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    """Extract relevant information from the following text.
Anonymous critics are actually Roger Ebert.

{input}
"""
)

document_transformer = create_metadata_tagger(schema, llm, prompt=prompt)
enhanced_documents = document_transformer.transform_documents(original_documents)

print(
    *[d.page_content + "\n\n" + json.dumps(d.metadata) for d in enhanced_documents],
    sep="\n\n---------------\n\n",
)


# In[ ]:




