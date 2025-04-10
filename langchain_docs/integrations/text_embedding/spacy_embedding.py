#!/usr/bin/env python
# coding: utf-8

# # SpaCy
# 
# >[spaCy](https://spacy.io/) is an open-source software library for advanced natural language processing, written in the programming languages Python and Cython.
#  
# 
# ## Installation and Setup

# In[ ]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  spacy')


# Import the necessary classes

# In[ ]:


from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings


# ## Example
# 
# Initialize SpacyEmbeddings.This will load the Spacy model into memory.

# In[ ]:


embedder = SpacyEmbeddings(model_name="en_core_web_sm")


# Define some example texts . These could be any documents that you want to analyze - for example, news articles, social media posts, or product reviews.

# In[ ]:


texts = [
    "The quick brown fox jumps over the lazy dog.",
    "Pack my box with five dozen liquor jugs.",
    "How vexingly quick daft zebras jump!",
    "Bright vixens jump; dozy fowl quack.",
]


# Generate and print embeddings for the texts . The SpacyEmbeddings class generates an embedding for each document, which is a numerical representation of the document's content. These embeddings can be used for various natural language processing tasks, such as document similarity comparison or text classification.

# In[ ]:


embeddings = embedder.embed_documents(texts)
for i, embedding in enumerate(embeddings):
    print(f"Embedding for document {i+1}: {embedding}")


# Generate and print an embedding for a single piece of text. You can also generate an embedding for a single piece of text, such as a search query. This can be useful for tasks like information retrieval, where you want to find documents that are similar to a given query.

# In[ ]:


query = "Quick foxes and lazy dogs."
query_embedding = embedder.embed_query(query)
print(f"Embedding for query: {query_embedding}")

