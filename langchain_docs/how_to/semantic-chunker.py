#!/usr/bin/env python
# coding: utf-8

# # How to split text based on semantic similarity
# 
# Taken from Greg Kamradt's wonderful notebook:
# [5_Levels_Of_Text_Splitting](https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb)
# 
# All credit to him.
# 
# This guide covers how to split chunks based on their semantic similarity. If embeddings are sufficiently far apart, chunks are split.
# 
# At a high level, this splits into sentences, then groups into groups of 3
# sentences, and then merges one that are similar in the embedding space.

# ## Install Dependencies

# In[ ]:


get_ipython().system('pip install --quiet langchain_experimental langchain_openai')


# ## Load Example Data

# In[1]:


# This is a long document we can split up.
with open("state_of_the_union.txt") as f:
    state_of_the_union = f.read()


# ## Create Text Splitter

# To instantiate a [SemanticChunker](https://python.langchain.com/api_reference/experimental/text_splitter/langchain_experimental.text_splitter.SemanticChunker.html), we must specify an embedding model. Below we will use [OpenAIEmbeddings](https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.openai.OpenAIEmbeddings.html). 

# In[4]:


from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

text_splitter = SemanticChunker(OpenAIEmbeddings())


# ## Split Text
# 
# We split text in the usual way, e.g., by invoking `.create_documents` to create LangChain [Document](https://python.langchain.com/api_reference/core/documents/langchain_core.documents.base.Document.html) objects:

# In[5]:


docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)


# ## Breakpoints
# 
# This chunker works by determining when to "break" apart sentences. This is done by looking for differences in embeddings between any two sentences. When that difference is past some threshold, then they are split.
# 
# There are a few ways to determine what that threshold is, which are controlled by the `breakpoint_threshold_type` kwarg.
# 
# Note: if the resulting chunk sizes are too small/big, the additional kwargs `breakpoint_threshold_amount` and `min_chunk_size` can be used for adjustments.
# 
# ### Percentile
# 
# The default way to split is based on percentile. In this method, all differences between sentences are calculated, and then any difference greater than the X percentile is split. The default value for X is 95.0 and can be adjusted by the keyword argument `breakpoint_threshold_amount` which expects a number between 0.0 and 100.0.

# In[12]:


text_splitter = SemanticChunker(
    OpenAIEmbeddings(), breakpoint_threshold_type="percentile"
)


# In[13]:


docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)


# In[14]:


print(len(docs))


# ### Standard Deviation
# 
# In this method, any difference greater than X standard deviations is split. The default value for X is 3.0 and can be adjusted by the keyword argument `breakpoint_threshold_amount`.

# In[15]:


text_splitter = SemanticChunker(
    OpenAIEmbeddings(), breakpoint_threshold_type="standard_deviation"
)


# In[16]:


docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)


# In[17]:


print(len(docs))


# ### Interquartile
# 
# In this method, the interquartile distance is used to split chunks. The interquartile range can be scaled by the keyword argument `breakpoint_threshold_amount`, the default value is 1.5.

# In[18]:


text_splitter = SemanticChunker(
    OpenAIEmbeddings(), breakpoint_threshold_type="interquartile"
)


# In[19]:


docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)


# In[20]:


print(len(docs))


# ### Gradient
# 
# In this method, the gradient of distance is used to split chunks along with the percentile method. This method is useful when chunks are highly correlated with each other or specific to a domain e.g. legal or medical. The idea is to apply anomaly detection on gradient array so that the distribution become wider and easy to identify boundaries in highly semantic data.
# Similar to the percentile method, the split can be adjusted by the keyword argument `breakpoint_threshold_amount` which expects a number between 0.0 and 100.0, the default value is 95.0.

# In[ ]:


text_splitter = SemanticChunker(
    OpenAIEmbeddings(), breakpoint_threshold_type="gradient"
)


# In[6]:


docs = text_splitter.create_documents([state_of_the_union])
print(docs[0].page_content)


# In[8]:


print(len(docs))

